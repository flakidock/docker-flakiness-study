from llm_apis import gpt_api_calls
from error_repair.information_retrieval import retrieve_relevant_records
from utils.class_utils import DemonstrationRecord
from error_repair.flakiDock.flakiness_demonstration_dataset import get_comparison_context


def retrieve_similar_records(dockerfile, build_output, top_k, segment_project_mapping, collection) -> list[DemonstrationRecord]:
    
    openai_client = gpt_api_calls.init_client()
    query = get_comparison_context(dockerfile, build_output)
    
    similar_segments = retrieve_relevant_records(run_time_model=openai_client, query=query, collection=collection, top_k=top_k, model_type="ada-v2")
    similar_segments = similar_segments['documents'][0]
    
    # remove the query itself from the retrieved segments, if exists
    # Note: remove this line if the comparison is just based on build output segment (without error line)
    if query in similar_segments:
        self_index = similar_segments.index(query)
        similar_segments.pop(self_index)
    
    similar_records = [segment_project_mapping[similar_segment] for similar_segment in similar_segments]
        
    return similar_records
    