from utils.class_utils import DockerfileFlakinessInfo
import chromadb
import pickle
import random
from llm_apis.bedrock_api_call import invoke_titan_embedding
from utils.file_utils import read_file, list_files_with_extension
from error_repair.constants import FLAKY_REPOS_PATH, ROOT_CAUSE_SEPARATOR
from utils.string_utils import truncate_string

def get_embedding(sentence, model):
    embedding = model.encode([sentence])[0]  # Get the 1D embedding vector
    return embedding

def get_embedding_bedrock(sentence, bedrock_runtime):
    embedding = invoke_titan_embedding(sentence, bedrock_runtime)
    return embedding

def save_embeddings_to_file(records, embeddings, file_path):
    # first, create a dictionary with records as keys and embeddings as values
    # second, store the dictionary in a pickle file
    embedding_dict = dict(zip(records, embeddings))
    
    with open(file_path, "wb") as file:
        pickle.dump(embedding_dict, file)

    
def load_embeddings_from_file(file_path):
    with open(file_path, "rb") as file:
        embedding_dict = pickle.load(file)
    
    return embedding_dict


def retrieve_relevant_records(run_time_model, query: str, collection: chromadb.Collection, top_k: int = 4, model_type = "huggingface") -> list[str]:

    if model_type == "huggingface":
        query_embedding = get_embedding(query, run_time_model).tolist()
    elif model_type == "bedrock":
        query_embedding = get_embedding_bedrock(query, run_time_model)
    elif model_type == "ada-v2":
        query = query.replace("\n", " ")
        query_embedding = run_time_model.embeddings.create(input = [query], model="text-embedding-ada-002").data[0].embedding
    
    relevant_records = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    return relevant_records


def generate_retrieval_collection(records: list[str], record_embeddings: list) -> chromadb.Collection:
    client = chromadb.Client()
    collection = client.create_collection("build_relevance")
    
    # embeddings_list = [embedding.tolist() for embedding in record_embeddings]
    embeddings_list = [embedding for embedding in record_embeddings]
    
    collection.add(
        embeddings=embeddings_list,
        ids=[str(i) for i in range(0, len(records))],  # IDs are just strings
        documents=records,
        metadatas=[{"type": "relevant records"} for _ in range(0, len(records))],
    )
    
    return collection


def retrieve_relevant_projects(retrieved_builds: list[str], build_project_mapping: dict[str, list[DockerfileFlakinessInfo]], top_k: int = 3) -> list[dict]:
    """
    Returns:
        list[dict]: list of dictionaries containing the project id and the retrieved builds. each dictionary contains the following keys: dockerfile, build_error, repair(first one)
    """
    
    retrieved_projects = []
    for retrieved_build in retrieved_builds:
        project = build_project_mapping[retrieved_build]
        project_id = project.project_name
        
        retrieved_project = {
            "dockerfile": project.dockerfile,
            "build_error": retrieved_build
        }
        
        # first check if it's a suggestion
        suggestion_required = False
        
        root_cause_file_content = read_file(FLAKY_REPOS_PATH + project_id + "/root_cause.txt")
        file_segments = root_cause_file_content.split(ROOT_CAUSE_SEPARATOR)
        for segment in file_segments:
            if "suggestion:" in segment:
                suggestion = segment.replace("suggestion:", "").strip()
                retrieved_project["suggestion"] = suggestion
                suggestion_required = True
                break
                
        # if it's not a suggestion, then it's a repair, retrieve all the repairs for the project
        if not suggestion_required:
            repair_files = list_files_with_extension(FLAKY_REPOS_PATH + project_id, "repair", None, False)
            for i, repair_file in enumerate(repair_files):
                repair_content = read_file(repair_file)
                retrieved_project["repair" + str(i+1)] = truncate_string(repair_content, 2048)
            retrieved_project["num_of_repairs"] = len(repair_files)
    
        retrieved_projects.append(retrieved_project)
        
    if (len(retrieved_projects) > top_k):
        retrieved_projects = retrieved_projects[:top_k]
    
    return retrieved_projects