import json
from tqdm import tqdm
from utils.class_utils import DockerfileExecutionRecord, DockerfileFlakinessInfo
from error_repair.constants import EXCLUDED_CATEGORIES, DOCKERFILE_INDEPENDENT_FLAKINESS, DOCKERFILE_DEPENDENCT_FLAKINESS, CATEGORY_SEPARATOR, NON_FLAKINESS_DATASET_PATH, FLAKINESS_DATASET_PATH, MISCELLANEOUS_CATEGORY


def get_proper_category_labels(project):
    # remove the first and last item from the hierarchy (first: whether it's dockerfile related or not, last: the leaf category)
    category = CATEGORY_SEPARATOR.join(project["category"].split(CATEGORY_SEPARATOR)[1:3]).strip() if CATEGORY_SEPARATOR in project["category"] else project["category"]
    return category, category.split(CATEGORY_SEPARATOR)[0].strip()


def update_project_info(project, project_info, category, top_category, dataset_type="flaky", is_excluded=False) -> DockerfileFlakinessInfo:
    if dataset_type != "flaky":
        if not project_info:
            return DockerfileFlakinessInfo(project['repo_name'], project['dockerfile'], True if dataset_type == "flaky" else False, project['build_output'])
        
        return project_info
        
    if not project_info:
        new_project_info = DockerfileFlakinessInfo(project['repo_name'], project['dockerfile'], True if dataset_type == "flaky" else False)
        
        if not is_excluded:
            new_project_info.records.append(DockerfileExecutionRecord(error_line=project['metadata']['dockerfile_error_line'], 
                                                                    category=category, 
                                                                    top_category=top_category,
                                                                    error_segment=project['metadata']['error_segment'],
                                                                    dockerfile_segment=project['metadata']['dockerfile_error_segment'],
                                                                    build_output=project['build_output'],
                                                                    build_time=project['build_time']))
        return new_project_info
        
    elif not is_excluded:
        new_record = DockerfileExecutionRecord(error_line=project['metadata']['dockerfile_error_line'], 
                                                category=category, 
                                                top_category=top_category,
                                                error_segment=project['metadata']['error_segment'],
                                                dockerfile_segment=project['metadata']['dockerfile_error_segment'],
                                                build_output=project['build_output'],
                                                build_time=project['build_time'])
        for record in project_info.records:
            if record.error_line == new_record.error_line and record.category == new_record.category:
                return project_info
        
        project_info.records.append(new_record)
        
    return project_info


def read_dataset(dataset_path, dataset_type="flaky", add_misc=False) -> dict[str, DockerfileFlakinessInfo]:
    """
    for each project in the dataset, extract the list of unique records. unique records are defined as the combination of error line and category.
    So if a project has multiple records with the same error line and category, only one of them will be included in the unique records list.
    The reason for doing that is to have the list of error lines and categories corresponding to those lines for each project:
        project: {line1: category1, line2: category2, line3: category1}
    """
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
        
    project_info = {}
    category_set = set()
    top_category_set = set()
    
    for project in tqdm(dataset):
        is_excluded = False
        if dataset_type == "flaky":
            if EXCLUDED_CATEGORIES in project["category"]:
                
                # skip miscellaneous errors
                if not add_misc:
                    if MISCELLANEOUS_CATEGORY in project["category"]:
                        continue
                
                is_excluded = True
                project["category"] = project["category"].replace(EXCLUDED_CATEGORIES, DOCKERFILE_INDEPENDENT_FLAKINESS)
                
            else:
                project["category"] = F"{DOCKERFILE_DEPENDENCT_FLAKINESS} {CATEGORY_SEPARATOR} {project['category']}"
        
            category, top_category = get_proper_category_labels(project)
        else:
            # non-flaky dataset
            category, top_category = project["category"], project["category"]
        
        category_set.add(category)
        top_category_set.add(top_category)
        
        project_info[project['repo_name']] = update_project_info(project, project_info.get(project['repo_name'], False), category, top_category, dataset_type=dataset_type, is_excluded=is_excluded)
        
        is_excluded = False
        
        
    return project_info, sorted(category_set), sorted(top_category_set)


def exclude_off_topic_flaky_projects(flaky_dataset, non_flaky_dataset):
    """
    exclude flaky projects that are not related to dockerfiles
    """
    updated_flaky_dataset = {}
    updated_non_flaky_dataset = {}
    
    # first add the non-flaky projects
    for project_id, project in non_flaky_dataset.items():
        updated_non_flaky_dataset[project_id] = project
    
    # check if the flaky project is an off-topic project -> move it to the non-flaky dataset
    for project_id, project in flaky_dataset.items():
        if len(project.records) == 0:
            project.is_flaky = False
            updated_non_flaky_dataset[project_id] = project
            continue
        
        updated_flaky_dataset[project_id] = project
    
    return updated_flaky_dataset, updated_non_flaky_dataset


def read_whole_dataset():
    flaky_dataset, flaky_categories, flaky_top_categories = read_dataset(dataset_path=FLAKINESS_DATASET_PATH, dataset_type="flaky")
    non_flaky_dataset, non_flaky_categories, non_flaky_top_categories = read_dataset(dataset_path=NON_FLAKINESS_DATASET_PATH, dataset_type="non_flaky")
    
    # exclude off-topic flaky projects and move them to the non-flaky dataset
    updated_flaky_dataset, updated_non_flaky_dataset = exclude_off_topic_flaky_projects(flaky_dataset, non_flaky_dataset)
    
    merged_categories = flaky_categories + non_flaky_categories
    merged_categories = [category for category in merged_categories if category not in EXCLUDED_CATEGORIES]
    merged_top_categories = flaky_top_categories + non_flaky_top_categories
    
    return updated_flaky_dataset, updated_non_flaky_dataset, merged_categories, merged_top_categories


def get_dockerfile_segments(dataset, excluded_repos=[]):
    
    # make a copy of the dataset
    copy_dataset = dataset.copy()
    
    # remove the excluded repos
    for repo in excluded_repos:
        copy_dataset.pop(repo, None)
        
    # extract the dockerfile segments: if flaky, check dockerfile_segment, if not empty, add it to the list, otherwise, add the dockerfile, if non-flaky, add the dockerfile
    dockerfile_segments = []
    for project in copy_dataset.values():
        if not project.is_flaky:
            dockerfile_segments.append(project.dockerfile)
            continue
        for record in project.records:
            if record.dockerfile_segment:
                dockerfile_segments.append(record.dockerfile_segment)
            else:
                dockerfile_segments.append(project.dockerfile)
    
    return dockerfile_segments


def get_dockerfile_segment_to_record_mappings(dataset):
    dockerfile_to_project = {}
    
    for _, project in dataset.items():
        if not project.is_flaky:
            if project.dockerfile not in dockerfile_to_project:
                dockerfile_to_project[project.dockerfile] = []
                
            dockerfile_to_project[project.dockerfile].append(project)
            continue
        
        for record in project.records:
            if record.dockerfile_segment:
                if record.dockerfile_segment not in dockerfile_to_project:
                    dockerfile_to_project[record.dockerfile_segment] = []
                dockerfile_to_project[record.dockerfile_segment].append(project)

            else:
                if project.dockerfile not in dockerfile_to_project:
                    dockerfile_to_project[project.dockerfile] = []
                dockerfile_to_project[project.dockerfile].append(project)
    
    return dockerfile_to_project