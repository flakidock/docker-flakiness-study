from tqdm import tqdm
import os
import re
import pandas as pd
from llm_apis import gpt_api_calls, bedrock_api_call, google_gemini_api_call
from error_repair.constants import FLAKINESS_DATASET_PATH, REPAIRED_PROJECTS_PATH, FLAKY_REPOS_PATH, BUILD_SEGMENT_EMBEDDINGS_PATH, ROOT_CAUSE_SEPARATOR
from utils.dataset_utils import read_dataset
from utils.file_utils import read_file, list_files_with_extension
from utils.class_utils import DockerfileFlakinessInfo
from error_repair.system_templates import SYSTEM_REPAIR_TEMPLATE_WITH_BUILD_OUTPUT_AND_SIMILARITY, SYSTEM_REPAIR_TEMPLATE_AND_SIMILARITY
from error_repair.user_templates import user_repair_template_with_build_info_and_similar_shots, user_repair_template_and_similar_shots
from path_config import ROOT_PATH
from utils.string_utils import truncate_string, num_gpt_tokens_in_a_string

from error_repair.information_retrieval import retrieve_relevant_records, retrieve_relevant_projects
from error_repair.information_retrieval import generate_retrieval_collection, get_embedding, get_embedding_bedrock, save_embeddings_to_file, load_embeddings_from_file


def get_record_time(project_name: str):
    """
    based on the phrase: consider: <time> inside the root_cause.txt file inside the flaky repos, decide which record to use. the separator for this file is "__________"
    """
    
    root_cause_file_content = read_file(FLAKY_REPOS_PATH + project_name + "/root_cause.txt")
    file_segments = root_cause_file_content.split(ROOT_CAUSE_SEPARATOR)
    
    for segment in file_segments:
        if "consider:" in segment:
            time = re.search(r'consider: (.*)', segment).group(1).strip()
            return time
    return ""  

def get_parsed_build_info(project: DockerfileFlakinessInfo):
    """
    build info to be used in the repair template and similarity comparison
    """
    
    build_info = ""
    
    if len(project.records) == 0:
        return build_info
    
    # if there are multiple records, get the record with the required time: within root_cause.txt
    if len(project.records) > 1:
        required_record_time = get_record_time(project.project_name)
        for record in project.records:
            if required_record_time == record.build_time:
                build_info = record.error_segment
       
    else:
        build_info = project.records[-1].error_segment
            
    return build_info 


def get_build_segments(dataset): 
    """
    get the list of build segments to generate collections for comparison
    """
    
    build_segments = []
    for project in dataset.values():
        build_segments.append(get_parsed_build_info(project))
        
    return build_segments


def save_embeddings(model, records, path, model_type="huggingface", client=None):
    """
    If embedding file does not exist, generate embeddings using the model and save to file.
    Then, load the embeddings from the file and return the embeddings list.
    """
    
    if not os.path.exists(path):
        if model_type == "huggingface":
            print("Generating embeddings using Huggingface model...")
            embeddings = [get_embedding(sentence, model) for sentence in tqdm(records)]
            
        elif model_type == "bedrock":
            print("Generating embeddings using Bedrock model...")
            bedrock_runtime = bedrock_api_call.init_bedrock()
            embeddings = [get_embedding_bedrock(sentence, bedrock_runtime) for sentence in tqdm(records)]
            
        elif model_type == "ada-v2":
            embeddings = []
            for record in tqdm(records):
                text = record.replace("\n", " ")
                embeddings.append(
                    client.embeddings.create(input = [text], model=model).data[0].embedding
                )
            
        save_embeddings_to_file(records, embeddings, path)
        
    loaded_embeddings = load_embeddings_from_file(path)
    
    embeddings_list = []
    for record in records:
        embeddings_list.append(loaded_embeddings[record])
    
    return loaded_embeddings, embeddings_list  


def get_build_segment_to_project(dataset):
    """
    For each project, get the build segment and map it to the project (build_segment -> project)
    """
    
    build_to_project = {}
    
    for _, project in dataset.items():
        build_segment = get_parsed_build_info(project)
        build_to_project[build_segment] = project
    
    return build_to_project


def get_input_prompts(prompt_type: str, dockerfile: str, build_info: str, shots: list):
    """
    get the input prompts based on the prompt type
    """
    
    system_prompt = ""
    user_prompt = ""
    if prompt_type == "Dockerfile_only":
        system_prompt = SYSTEM_REPAIR_TEMPLATE_AND_SIMILARITY
        user_prompt = user_repair_template_and_similar_shots(dockerfile=dockerfile, shots=shots)
    
    if prompt_type == "Dockerfile_and_build_info":
        system_prompt = SYSTEM_REPAIR_TEMPLATE_WITH_BUILD_OUTPUT_AND_SIMILARITY
        user_prompt = user_repair_template_with_build_info_and_similar_shots(dockerfile=dockerfile, build_error=build_info, shots=shots)
    
    return system_prompt, user_prompt