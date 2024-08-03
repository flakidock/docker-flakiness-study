from tqdm import tqdm
import json
from sentence_transformers import SentenceTransformer
from error_categorization.error_parser.sentence_similarity import get_embedding, calculate_embedding_similarity
from utils.file_utils import list_files_with_extension, list_folder
from utils.class_utils import SummaryInfo, ClusterItem
from llm_apis import gpt_api_calls
from path_config import ROOT_PATH

FLAKY_BUILD_DIR = ROOT_PATH + '/possible-flaky-repos'
SUMMARY_DIR = '/unique-build-errors'
SUMMARY_FILE_IDENTIFIER = 'llm-summary-'

SIMILARITY_THRESHOLD = 0.75

UNKNOWN = 'CORRUPTED_JSON_FORMAT'
CLUSTER_KEY = 'initial cluster name'

CLUSTER_OUTPUT_FILE = ROOT_PATH + '/error_categorization/data/0-label-clusters.json'


def calculate_average_similarity(cluster_item, cluster):
    accumulated_similarity = 0
    for item in cluster:
        accumulated_similarity += calculate_embedding_similarity(cluster_item.embedding, item.embedding)

    return accumulated_similarity / len(cluster)


def update_clusters(cluster_item, clusters):
    best_similarity = 0
    best_index = -1
    for i, cluster in enumerate(clusters):
        avg_similarity = calculate_average_similarity(cluster_item, cluster)
        if avg_similarity > SIMILARITY_THRESHOLD and avg_similarity > best_similarity:
            best_index = i
            best_similarity = avg_similarity
            
    if best_index != -1:
        clusters[best_index].append(cluster_item)
    else: 
        clusters.append([cluster_item])
        
    return clusters


def append_new_cluster(cluster_name, list_of_errors, cluster_objects):
    for cluster_object in cluster_objects:
        if cluster_name in cluster_object:
            cluster_object[cluster_name].extend(list_of_errors)
            return
        
    new_cluster_object = {
        cluster_name: list_of_errors
    }
    
    cluster_objects.append(new_cluster_object)
        

def cluster_with_embeddings(error_summaries):
    
    model = SentenceTransformer('all-mpnet-base-v2')
    
    print("Calculating embeddings...")
    embeddings = [get_embedding(summary.serialize_str(), model) for summary in tqdm(error_summaries)]
    
    clusters = []
        
    print("Clustering...")
    for embedding, summary in tqdm(zip(embeddings, error_summaries)):
        cluster_item = ClusterItem(embedding, summary)
        clusters = update_clusters(cluster_item, clusters)

    print("Generating cluster names with LLM...")
    cluster_objects = []
    for i, cluster in tqdm(enumerate(clusters)):
        list_of_errors = list(set([item.info.serialize_str() for item in cluster]))
        cluster_name = gpt_api_calls.prompt_chat_gpt_for_generate_cluster_name(
            list_of_errors='\n'.join(list_of_errors)
        )
        
        append_new_cluster(cluster_name, list_of_errors, cluster_objects)
    
    with open(CLUSTER_OUTPUT_FILE, 'w') as file:
        file.write(json.dumps(cluster_objects, indent=4))
        
    print(f"Found {len(cluster_objects)} unique clusters")
    
    return cluster_objects


def get_summaries_info(summary_files):
    summaries_info = []
    
    for summary_file in summary_files:
        repo_name = summary_file.split('/')[2]
        build_date = summary_file.split('/')[-1].split(SUMMARY_FILE_IDENTIFIER)[-1].replace('.log.json', '')
        
        with open(summary_file, 'r') as f:
            try:        
                data = json.load(f)
                data = json.loads(json.loads(data))
                label = data.get('label', UNKNOWN)
                summary = data.get('summary', UNKNOWN)
                error_sources = data.get('sources of error', UNKNOWN)
                new_summary = SummaryInfo(
                    project=repo_name + '-' + build_date, 
                    label=label, 
                    summary=summary, 
                    sources=error_sources
                )
                
                
            except: # we should fix all exceptions manually: Done
                new_summary = SummaryInfo(
                    project=repo_name + '-' + build_date, 
                    label=UNKNOWN, 
                    summary=UNKNOWN, 
                    sources=UNKNOWN
                )
            
            summaries_info.append(new_summary)
            
    return summaries_info


def cluster_with_llm(summaries_info):
    unique_labels = list(set([summary.label for summary in summaries_info]))
    list_of_errors_str = '\n'.join(unique_labels)
    # with open('unique_labels.txt', 'w') as file:
    #     file.write(list_of_errors_str)
    
    clusters: str = gpt_api_calls.prompt_chat_gpt_for_initial_error_clustering(
        list_of_errors=list_of_errors_str[:100]
    )
    clusters_formatted = json.dumps(clusters, indent=4)
    
    with open('clusters.json', 'w') as file:
        file.write(clusters_formatted)
                    
    return clusters


def update_summary_files(clusters, list_of_repos):
    # generate a dictionary with the error as key and the cluster name as value
    label_to_cluster = {}
    for cluster in clusters:
        for cluster_name in cluster:
            for error in cluster[cluster_name]:
                label_to_cluster[error] = cluster_name
                
    # with open('label_to_cluster.json', 'w') as file:
    #     file.write(json.dumps(label_to_cluster, indent=4))
                
    # update the summary files with the cluster name
    print("Updating summary files...")
    for repo_dir in tqdm(list_of_repos):
        summary_path = repo_dir + SUMMARY_DIR
        summary_files = list_files_with_extension(summary_path, SUMMARY_FILE_IDENTIFIER)
        
        for summary_file in summary_files:
            try:        
                with open(summary_file, 'r') as f:
                    data = json.load(f)
                    
                    # Depends on the format of the summary file, you may need to comment this line
                    data = json.loads(json.loads(data))
                    
                    label = data.get('label', UNKNOWN)
                
                data[CLUSTER_KEY] = label_to_cluster[label]
                
                with open(summary_file, 'w') as f:
                    f.write(json.dumps(data, indent=4))
     
            except Exception as e: # This exception should not happen!
                print(f"Error reading {summary_file}: {e}: label {label}")
                           

if __name__ == '__main__':
    list_of_repos = list_folder(FLAKY_BUILD_DIR, True)
    
    print("Read summary files...")
    summaries_info = []
    for repo_dir in tqdm(list_of_repos):
        
        summary_path = repo_dir + SUMMARY_DIR
        summary_files = list_files_with_extension(summary_path, SUMMARY_FILE_IDENTIFIER)
        
        summaries_info.extend(get_summaries_info(summary_files))
    
    # approach 1: cluster using Sentence BERT embeddings + LLMs for cluster naming
    clusters = cluster_with_embeddings(summaries_info)
    update_summary_files(clusters, list_of_repos)
    
    # approach 2: cluster using GPT-3.5 prompting
    # clusters = cluster_with_llm(summaries_info)
    