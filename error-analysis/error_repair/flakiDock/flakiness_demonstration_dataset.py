import re
from error_repair.constants import FLAKY_REPOS_PATH, FLAKINESS_DATASET_PATH, REPAIRED_PROJECTS_PATH, ROOT_CAUSE_SEPARATOR
from utils.dataset_utils import read_dataset
from utils.file_utils import read_file, list_files_with_extension
from utils.class_utils import DemonstrationMetadata, DemonstrationRecord
from utils.string_utils import truncate_string
from error_repair.information_retrieval import generate_retrieval_collection
from error_repair.similarity_retrieval_utils import save_embeddings


def get_root_cause_info(project_name):
    root_cause_file_content = read_file(FLAKY_REPOS_PATH + project_name + "/root_cause.txt")
    file_segments = root_cause_file_content.split(ROOT_CAUSE_SEPARATOR)
    
    root_cause_label = file_segments[0].replace("label: ", "").strip()
    root_cause_info = file_segments[1].strip()
    
    rounds = 0
    date = ""
    for segment in file_segments:
        if "rounds:" in segment:
            rounds = int(segment.replace("rounds: ", "").strip())
        if "consider:" in segment:
            date = re.search(r'consider: (.*)', segment).group(1).strip()

    return root_cause_label, root_cause_info, rounds, date


def get_error_info(project, date):
    # check if date is an empty string
    if not date:
        error_line = project.records[-1].error_line
        error_category = project.records[-1].category
        build_output = project.records[-1].error_segment
        
        return error_line, error_category, build_output

    for record in project.records:
        if date in record.build_time:
            error_line = record.error_line
            error_category = record.category
            build_output = record.error_segment
            
            return error_line, error_category, build_output
        

def get_repaired_dockerfile(project_name):
    root_cause_file_content = read_file(FLAKY_REPOS_PATH + project_name + "/root_cause.txt")
    file_segments = root_cause_file_content.split(ROOT_CAUSE_SEPARATOR)
    for segment in file_segments:
        if "suggestion:" in segment:
            suggestion = segment.replace("suggestion:", "# SUGGESTION:").strip()
            return suggestion
    
    # if it's not a suggestion, then it's a repair, retrieve all the repairs for the project
    repairs = []
    repair_files = list_files_with_extension(FLAKY_REPOS_PATH + project_name, "repair", None, False)
    for i, repair_file in enumerate(repair_files):
        repair_content = read_file(repair_file)
        repairs.append(repair_content)
    
    return repairs
    

def get_demonstration_info(repaired_dataset):
    demonstration_dataset = {}
    for project_id, project in repaired_dataset.items():
        
        root_cause_label, root_cause_info, rounds, date = get_root_cause_info(project_id)
        error_line, error_category, build_output = get_error_info(project, date)
        repair_context = get_repaired_dockerfile(project_id)
        
        metadata = DemonstrationMetadata(
            root_cause_info=root_cause_info,
            error_line=error_line,
            error_category=error_category
        )
        demonstration_record = DemonstrationRecord(
            dockerfile=project.dockerfile,
            build_output=build_output,
            root_cause_label=root_cause_label,
            repair=repair_context,
            rounds=rounds,
            metadata=metadata
        )
        demonstration_dataset[project_id] = demonstration_record
    
    return demonstration_dataset


def get_comparison_context(dockerfile, build_output, max_tokens=3000):
    build_output = truncate_string(build_output, max_tokens)
    dockerfile = truncate_string(dockerfile, max_tokens-1000)
    # static_segments = f"## Dockerfile:\n {dockerfile}"
    static_segments = f""
    dynamic_segments = f"## Build Output:\n {build_output}"
    return static_segments + "\n" + dynamic_segments


def get_comparison_segments(demonstration_dataset: dict[str, DemonstrationRecord]):
    """
    For each project, get the static and dynamic segments for similarity comparison stage
    """
    
    comparison_segments = []
    for project_id, demonstration_record in demonstration_dataset.items():
        comparison_segment = get_comparison_context(demonstration_record.dockerfile, demonstration_record.build_output)
        comparison_segments.append(comparison_segment)
        
    return comparison_segments


def get_comparison_segment_to_project(demonstration_dataset: dict[str, DemonstrationRecord]):
    """
    For each project, get the static and dynamic segments and map it to the project (comparison_segment -> project)
    """
    
    comparison_to_project = {}
    for project_id, demonstration_record in demonstration_dataset.items():
        comparison_segment = get_comparison_context(demonstration_record.dockerfile, demonstration_record.build_output)
        comparison_to_project[comparison_segment] = demonstration_record
    
    return comparison_to_project
    

def generate_demonstration_dataset():
    project_dataset, _, _ = read_dataset(FLAKINESS_DATASET_PATH)
    
    # get the flaky dataset shown in repaired_projects.txt
    repaired_project_keys = [project.strip() for project in read_file(REPAIRED_PROJECTS_PATH).split("\n") if project.strip()]
    repaired_dataset = {project_id: project_dataset[project_id] for project_id in repaired_project_keys}
    
    demonstration_dataset = get_demonstration_info(repaired_dataset)
    
    return demonstration_dataset
    
    # loaded_embeddings, build_embeddings = save_embeddings("", build_segments, "bedrock") -> use information_retrieval
    
    # collection = generate_retrieval_collection(build_segments, build_embeddings) -> use information_retrieval