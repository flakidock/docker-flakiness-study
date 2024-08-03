from tqdm import tqdm
from error_categorization.error_parser.docker_error_parser import get_error_segments_as_json, remove_duration, get_error_segments
from error_categorization.error_parser.sentence_similarity import get_embedding, calculate_embedding_similarity
from sentence_transformers import SentenceTransformer
from utils.file_utils import read_file, list_files_with_extension, list_folder, create_or_empty_folder
from utils.class_utils import ClusterItem
import sys


DEFAULT_DIRECTORY_NAME = '/possible-flaky-repos/'
UNIQUE_BUILD_PATH = 'unique-build-errors'
CLUSTER_FILENAME = "clusters.txt"
DOCKERFILE_NAME = "Dockerfile"
DOCKERFILE_ERROR_INDICATOR = ">>> " # indicator of the line of error in Dockerfile mentioned in the error message
SIMILARITY_THRESHOLD = 0.85

BASED_OPERATION = "extract-unique"
APPEND_OPERATION = "append-dockerfile"
COMBINED_OPERATION = "combined" # default: extract-unique and append-dockerfile

# model = SentenceTransformer('all-mpnet-base-v2')
        

def list_parsed_errors(file_paths):
    parsed_errors = []
    for path in file_paths:
        raw_build_log = read_file(path)
        build_info = get_error_segments_as_json(path, raw_build_log)
        parsed_errors.append(build_info)
        
    return parsed_errors


def calculate_average_similarity(cluster_item, cluster):
    accumulated_similarity = 0
    for item in cluster:
        accumulated_similarity += calculate_embedding_similarity(cluster_item.embedding, item.embedding)

    return accumulated_similarity / len(cluster)

def update_clusters(cluster_item, clusters, similarity_threshold=SIMILARITY_THRESHOLD):
    for cluster in clusters:
        avg_similarity = calculate_average_similarity(cluster_item, cluster)
        if avg_similarity > similarity_threshold:
            cluster.append(cluster_item)
            return clusters

    clusters.append([cluster_item])
    return clusters

def fetch_unique_segments(parsed_errors):
        
    embeddings = [get_embedding(parsed_error['error_segment'], model) for parsed_error in parsed_errors]
    clusters = []
    
    for embedding, parsed_error in zip(embeddings, parsed_errors):
        cluster_item = ClusterItem(embedding, parsed_error)
        clusters = update_clusters(cluster_item, clusters)
                
    return (clusters)


# def get_exit_code(stderr):
    


def get_error_context(parsed_error):
    filename = parsed_error["file_name"].split("/")[-1].replace(".failure", "")
    error_context = ""
    
    for key in parsed_error.keys():
        if 'file_name' not in key:
            error_context += "** " + key.upper() + " **: \n" + parsed_error[key] + "\n\n"
    
    # exit_code = get_exit_code(parsed_error["stderr"])
    # if exit_code > 0:
    #     error_context += "** EXIT CODE **: \n" + exit_code + "\n\n"
    
    return filename, error_context


def add_unique_parsed_errors(clusters, error_dir):
    for cluster in clusters:
        cluster_sample = cluster[0] # store the first item of each cluster
        
        file_name, context = get_error_context(cluster_sample.info)
        
        file_path = error_dir + "/" + file_name
        with open(file_path, 'w') as file:
            file.write(context)


def add_cluster_info(clusters, error_dir):
    output_path = error_dir + "/" + CLUSTER_FILENAME
    cluster_info = ""
    
    for i, cluster in enumerate(clusters):
        cluster_info += "** Cluster " + str(i+1) + " **\n"
        for item in cluster:
            filename = item.info["file_name"].split("/")[-1].replace(".failure", "")
            cluster_info += filename + "\n"
            
        with open(output_path, 'w') as file:
            file.write(cluster_info)            


def get_corresponding_build_file(unique_file):
    unique_date = unique_file.split("/")[-1].split(".")[0]
    corresponding_failure_file = unique_file.split(UNIQUE_BUILD_PATH)[0] + unique_date + ".failure.log"
    return corresponding_failure_file

def get_dockerfile_error_line(build_file):
    raw_build_log = read_file(build_file)
    
    raw_build_log = remove_duration(raw_build_log)

    error_segments = get_error_segments(raw_build_log)
    
    if len(error_segments) <= 1:
        return -1
    else:
        # fetch dockerfile error line from the build output
        docker_parts = error_segments[-2]
        
        # extract the line from this pattern: "{n} | >>> {command}"
        docker_lines = [docker_part for docker_part in docker_parts.split("\n") if DOCKERFILE_ERROR_INDICATOR in docker_part]
        
        if len(docker_lines) == 0:
            return -1
        
        # get the line number from the last line containing ">>>"
        last_number = docker_lines[-1].split("|")[0]
        last_number = int(last_number.strip())
        
        return last_number
    
"""
If the error line is valid, then we should return the dockerfile content up to that line,
Otherwise, we should return the entire dockerfile
"""
def get_dockerfile_content(unique_repo_dir, dockerfile_error_line):
    dockerfile_path = unique_repo_dir.split(UNIQUE_BUILD_PATH)[0] + DOCKERFILE_NAME
    dockerfile_content = read_file(dockerfile_path)
    
    dockerfile_lines = dockerfile_content.split("\n")
    
    dockerfile_content = "\n".join(dockerfile_lines[:dockerfile_error_line]) if dockerfile_error_line > 0 else dockerfile_content
    
    return dockerfile_content
    
def append_unique_file(unique_file, dockerfile_content):
    with open(unique_file, 'a') as file:
        new_content = "** DOCKERFILE_ERROR_SEGMENT **: \n" + dockerfile_content + "\n"
        file.write(new_content)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        operation = COMBINED_OPERATION
    else:
        operation = sys.argv[1] #append-dockerfile
    
    if not operation in [BASED_OPERATION, APPEND_OPERATION, COMBINED_OPERATION]:
        print("Invalid operation")
        exit()
        
    # search through repos and fetch list of repo directories
    directory = DEFAULT_DIRECTORY_NAME
    list_of_repos = list_folder(directory, check_depth=False)
        
    if operation in [BASED_OPERATION, COMBINED_OPERATION]:
    
        for repo_dir in tqdm(list_of_repos):
            
            print("repo_dir:", repo_dir)
            
            # for each repo dir, search for all FAILURE log files
            list_of_files = list_files_with_extension(repo_dir, extension="failure.log", not_extension="2023-03-02-00")   

            # for each .failure.log file, parse the error segments 
            list_of_parsed_errors = list_parsed_errors(list_of_files)
            
            # start iterating over segments and find unique ones
            clusters = fetch_unique_segments(list_of_parsed_errors)
            
            unique_error_dir = repo_dir + "/" + UNIQUE_BUILD_PATH
            create_or_empty_folder(unique_error_dir)
            
            add_unique_parsed_errors(clusters, unique_error_dir)
            
            add_cluster_info(clusters, unique_error_dir) 
            
        
            
    list_of_repos = list_folder(directory, check_depth=True)
    
    if operation in [APPEND_OPERATION, COMBINED_OPERATION]:
        # fetch all unique error directories
        unique_repo_dirs = [repo_dir for repo_dir in list_of_repos if UNIQUE_BUILD_PATH in repo_dir]
        for unique_repo_dir in tqdm(unique_repo_dirs):
            
            # get the original repo dir and its FAILURE log files, ignore failures from 2023-03-02-00 (this is our system error)
            original_repo_dir = unique_repo_dir.replace(f"/{UNIQUE_BUILD_PATH}", "")
            list_of_files = list_files_with_extension(original_repo_dir, extension="failure.log", not_extension="2023-03-02-00")
            
            # get the unique error files
            unique_files = list_files_with_extension(unique_repo_dir, extension="20") #extension: first two digits of the year
            
            for unique_file in unique_files:
                
                # find the failure file from the unique file generated for clustering
                corresponding_file = get_corresponding_build_file(unique_file)
                
                # find the line number of the error in the Dockerfile
                dockerfile_error_line = get_dockerfile_error_line(corresponding_file)
                print("dockerfile_error_line:", dockerfile_error_line)
                
                dockerfile_content = get_dockerfile_content(unique_repo_dir, dockerfile_error_line)
                print("dockerfile_content:", dockerfile_content)
                
                append_unique_file(unique_file, dockerfile_content)
                
            
            
            