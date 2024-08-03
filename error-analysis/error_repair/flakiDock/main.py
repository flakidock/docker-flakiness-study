import os
import argparse

from utils.file_utils import list_subfolders, read_file
from llm_apis import bedrock_api_call, gpt_api_calls
from error_repair.constants import DEMONSTRATION_SEGMENT_EMBEDDINGS_PATH, DEMONSTRATION_BUILD_SEGMENT_EMBEDDINGS_PATH, REPOSITORIES_FOLDER, TEST_PROJECTS_PATH, FLAKIDOCK_BUILD_PATH
from error_repair.information_retrieval import generate_retrieval_collection
from error_repair.similarity_retrieval_utils import save_embeddings

from error_repair.flakiDock.flakiness_demonstration_dataset import generate_demonstration_dataset, get_comparison_segments, get_comparison_segment_to_project
from error_repair.flakiDock.dockerfile_builder import check_dockerfile_exists, extract_build_output
from error_repair.flakiDock.similarity_retriever import retrieve_similar_records
from error_repair.flakiDock.repair_generator import generate_repaired_dockerfile
from error_repair.flakiDock.repair_validator import verify_repaired_dockerfile

BUILD_ITERATIONS = 2
HALLUCINATION_THRESHOLD = 3
TOP_K = 3
MAX_ITERATIONS = 5


def get_project_info(project_path):
    """
    Get the Dockerfile path and Dockerfile content:
    
    Parameters:
        project_path (str): project path
        
    Returns:
        a tuple of (dockerfile_path, dockerfile):
            dockerfile_path (str): Dockerfile path
            dockerfile (str): Dockerfile content
    """

    dockerfile_exists, dockerfile_path = check_dockerfile_exists(project_path)
    
    if not dockerfile_exists:
        return None, None
    
    with open(dockerfile_path, 'r') as f:
        dockerfile = f.read()
    
    return dockerfile_path, dockerfile

def get_projects_path():
    """
    Get the projects path:
        
    Returns:
        projects_path (list): list of projects path
    """
    
    test_project_names = read_file(TEST_PROJECTS_PATH)
    test_project_names = [project_name.strip() for project_name in test_project_names.split("\n") if project_name.strip()]
    
    projects_path = []
    if not os.path.exists(REPOSITORIES_FOLDER):
        return projects_path
    
    for project_name in test_project_names:
        project_path = os.path.join(REPOSITORIES_FOLDER, project_name)
        if os.path.exists(project_path):
            projects_path.append(project_path)

    return projects_path

def update_project_stats_file(project_name, status):
    """
    Update the project stats file:
    
    Parameters:
        project_name (str): project name
        status (str): status
    """
    
    project_stat_file = FLAKIDOCK_BUILD_PATH + "projects_stats.txt"
    if not os.path.exists(project_stat_file):
        with open(project_stat_file, "w") as f:
            f.write(project_name + ":" + status + "\n")
        return
    
    with open(project_stat_file, "r") as f:
        lines = f.readlines()
    
    with open(project_stat_file, "w") as f:
        project_seen = False
        for line in lines:
            if project_name in line:
                f.write(project_name + ":" + status + "\n")
                project_seen = True
            else:
                f.write(line)
        
        if not project_seen:
            f.write(project_name + ":" + status + "\n")


def project_already_finished(project_name):
    """
    Check if the project is already finished:
    
    Parameters:
        project_name (str): project name
        
    Returns:
        bool: True if the project is already finished, False otherwise
    """
    
    project_stat_file = FLAKIDOCK_BUILD_PATH + "projects_stats.txt"
    if not os.path.exists(project_stat_file):
        return False
    
    with open(project_stat_file, "r") as f:
        lines = f.readlines()
    
    for line in lines:
        if project_name in line:
            if "success" in line or "failed" in line or "non-flaky" in line:
                return True
    
    return False 


if __name__ == "__main__":
        if not os.path.exists(FLAKIDOCK_BUILD_PATH):
            os.makedirs(FLAKIDOCK_BUILD_PATH)
        projects_path = get_projects_path()
        
        # ---------- get the runtime model ----------
        model_under_test = "gpt-4o"
        llama_model_under_test = "meta.llama3-1-405b-instruct-v1:0"
        bedrock_runtime = bedrock_api_call.init_bedrock()
        openai_runtime = gpt_api_calls.init_openai(model_under_test)
        client = gpt_api_calls.init_client()
        
        # ---------- get demonstration dataset, its embeddings, and collection for comparison ----------
        demonstration_dataset = generate_demonstration_dataset()
        
        segments = get_comparison_segments(demonstration_dataset)
        
        loaded_embeddings, embeddings = save_embeddings("text-embedding-ada-002", segments, DEMONSTRATION_BUILD_SEGMENT_EMBEDDINGS_PATH, "ada-v2", client)
        
        segment_project_mapping = get_comparison_segment_to_project(demonstration_dataset)
        
        collection = generate_retrieval_collection(segments, embeddings)
        
        # ---------- iterate over projects and repair the Dockerfile ----------
        total_projects = len(projects_path)
        print(f"Total projects: {total_projects}")
        
        
        for i, project_path in enumerate(projects_path):
            try:
            
                # update project stats file
                project_name = project_path.split("/")[-1]
                
                # check if the project is already finished (previous runs)
                if (project_already_finished(project_name)):
                    print(f"********** {i+1}/{total_projects} - {project_path} - already finished!")
                    continue
                    
                update_project_stats_file(project_name, "running")
                # print the iteration number
                print(f"********** {i+1}/{total_projects} - {project_path}")
                
                # create output folder
                output_folder = os.path.join(FLAKIDOCK_BUILD_PATH, project_name)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                
                dockerfile_path, dockerfile = get_project_info(project_path)
                
                # check invalid path or Dockerfile
                if dockerfile_path is None or dockerfile is None:
                    update_project_stats_file(project_name, "failed")
                    continue
                
                # save the Dockerfile content
                with open(os.path.join(output_folder, "v0_Dockerfile"), "w") as f:
                    f.write(dockerfile)
                
                print("# Dockerfile Builder: Initiating...")
                is_flaky, build_output = extract_build_output(
                    project_path=project_path,
                    dockerfile_path=dockerfile_path,
                    build_iterations=BUILD_ITERATIONS,
                    output_folder=output_folder
                )
                
                print("# Done")
                if not is_flaky:
                    update_project_stats_file(project_name, "non-flaky")
                    continue
                
                print("# Similarity Retriever: Initiating...")
                similar_records = retrieve_similar_records(
                    dockerfile=dockerfile, 
                    build_output=build_output, 
                    top_k=TOP_K,
                    segment_project_mapping=segment_project_mapping,
                    collection=collection,
                )
                print("# Done")
                
                feedbacks = []
                rounds = 1
                
                # repair & verification loop
                while(True):
                    
                    # generate a repair for the Dockerfile using prompt-based repair
                    dockerfile_name = f"v{rounds}_Dockerfile"
                    
                    print("# Round:", rounds)
                    print("# Repair Generator: Initiating...")
                    repaired_dockerfile = generate_repaired_dockerfile(
                        project_path=project_path,
                        dockerfile=dockerfile,
                        build_output=build_output,
                        similar_records=similar_records,
                        feedbacks=feedbacks,
                        model_under_test=model_under_test,
                        round=rounds,
                        output_folder=output_folder,
                        dockerfile_name=dockerfile_name,
                        model="gpt4"
                    )

                    print("# Done")
                    
                    
                    print("# Repair Validator: Initiating...")
                    verification_message, feedbacks = verify_repaired_dockerfile(
                        project_path=project_path,
                        dockerfile_name = dockerfile_name,
                        repaired_dockerfile=repaired_dockerfile,
                        build_iterations=BUILD_ITERATIONS,
                        feedbacks=feedbacks,
                        hallucination_threshold=HALLUCINATION_THRESHOLD,
                        output_folder=output_folder,
                        stage=rounds
                    )
                    print("# Done")
                    
                    # successful repair
                    if verification_message == 'SUCCESS':
                        update_project_stats_file(project_name, "success")                
                        print("***** Dockerfile successfully repaired! *****")
                        break
                    
                    if verification_message == 'UNABLE_TO_RESOLVE':
                        update_project_stats_file(project_name, "failed")
                        print("***** Unable to resolve! *****")
                        break
                    
                    if rounds == MAX_ITERATIONS:
                        update_project_stats_file(project_name, "failed")
                        print("***** Maximum iterations reached! *****")
                        break
                    
                    rounds += 1
                    
            except Exception as e:                    
                print(f"Error: {e}")
                update_project_stats_file(project_name, "failed")
                continue