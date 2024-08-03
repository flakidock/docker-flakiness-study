import os
from tqdm import tqdm
from llm_apis import bedrock_api_call
from error_repair.information_retrieval import get_embedding_bedrock
from utils.class_utils import ClusterItem, FeedbackInfo
from error_repair.flakiDock.dockerfile_builder import extract_build_output
from error_categorization.error_parser.sentence_similarity import get_embedding, calculate_embedding_similarity

SIMILARITY_THRESHOLD = 0.8


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


def cluster_with_embeddings(records):
    
    bedrock_runtime = bedrock_api_call.init_bedrock()
    embeddings = [get_embedding_bedrock(sentence, bedrock_runtime) for sentence in tqdm(records)]
    
    clusters = []
        
    # Clustering
    for embedding, record in tqdm(zip(embeddings, records)):
        cluster_item = ClusterItem(embedding, record)
        clusters = update_clusters(cluster_item, clusters)
    
    return clusters


def get_most_failure_count(feedbacks):
    build_outputs = [feedback.build_output for feedback in feedbacks]
    clusters = cluster_with_embeddings(build_outputs)
    
    largest_cluster = max(clusters, key=len)
    return len(largest_cluster)


def verify_repaired_dockerfile(project_path, dockerfile_name, repaired_dockerfile, build_iterations, feedbacks,hallucination_threshold, output_folder, stage):
    # extract build output from the repaired Dockerfile
    dockerfile_path = os.path.join(project_path, dockerfile_name)
    is_flaky, build_output = extract_build_output(project_path, dockerfile_path, build_iterations, output_folder=output_folder, stage=stage)
    
    if not is_flaky:
        return 'SUCCESS', feedbacks
    
    # remove the false repaired Dockerfile
    os.remove(dockerfile_path)
    
    # generate a new feedback
    new_feedback = FeedbackInfo(repaired_dockerfile, build_output)
    
    if len(feedbacks) >= hallucination_threshold:
        most_failure_count = get_most_failure_count(feedbacks)
        if most_failure_count >= hallucination_threshold:
            return 'UNABLE_TO_RESOLVE', feedbacks
    
    # if hallucination hasn't reached
    feedbacks.append(new_feedback)
    return 'FEEDBACK', feedbacks


def verify_repaired_dockerfile_SD(project_path, dockerfile_name, build_iterations, output_folder, stage):
    # extract build output from the repaired Dockerfile
    dockerfile_path = os.path.join(project_path, dockerfile_name)
    is_flaky, build_output = extract_build_output(project_path, dockerfile_path, build_iterations, output_folder=output_folder, stage=stage)
    
    if not is_flaky:
        return 'SUCCESS'
    else:
        return 'UNABLE_TO_RESOLVE'
    
def verify_repaired_dockerfile_S(project_path, dockerfile_name, build_iterations, output_folder, stage):
    # extract build output from the repaired Dockerfile
    dockerfile_path = os.path.join(project_path, dockerfile_name)
    is_flaky, build_output = extract_build_output(project_path, dockerfile_path, build_iterations, output_folder=output_folder, stage=stage)
    
    if not is_flaky:
        return 'SUCCESS'
    else:
        return 'UNABLE_TO_RESOLVE'