import json
from tqdm import tqdm
import os
from utils.file_utils import list_files_with_extension, list_folder
from dataset_types import RepoHistory
from error_categorization.dataset_generation.constants import FLAKY_BUILD_DIR, NON_FLAKY_BUILD_DIR, FLAKY_HISTORY_DATASET_FILE


def get_all_build_dates(repo_paths):
    """
    Extract all build dates from the build logs of the repos (all dates that exists in the logs)
    """
    
    all_build_dates = []
    
    for repo_path in repo_paths:
        build_files = list_files_with_extension(repo_path, '.log', None, check_depth=False)
        build_files.sort()
        
        for build_file in build_files:
            # extract the build date from the file name
            build_date = build_file.split('/')[-1].split('.')[0]
            
            if build_date not in all_build_dates:
                all_build_dates.append(build_date)
                
    return all_build_dates

def get_first_successful_build_path(project_path):
    """
    Search through the history of build logs and return the path of the first successful build
    """
    
    build_files = list_files_with_extension(project_path, '.log', None, check_depth=False)
    build_files.sort()
    
    for build_file in build_files:
        build_status = build_file.split('/')[-1].split('.')[-2]
        if build_status == 'success':
            return build_file 

    print(f"No successful build found for {project_path}")
    return ""


def get_build_history(path, build_dates) -> list:
    """
    extract the build history using the valid build dates list and the path of the flaky repos
    
    Parameters:
        path (str): the path of the flaky repos
        build_dates (list): list of all available build dates
    """
    
    build_history = []
    
    print(f"Getting build history for flaky repos...")
    
    repo_paths = list_folder(path, check_depth=False)
    for repo_path in tqdm(repo_paths):
        
        repo_name = repo_path.split('/')[-1]
        
        build_logs = list_files_with_extension(repo_path, '.log', None, check_depth=False)
        
        project_history = [{build_log.split('/')[-1].split('.')[0]: build_log.split('/')[-1].split('.')[1]} for build_log in build_logs]
        project_dates = [list(build.keys())[0] for build in project_history]
        
        for build_date in build_dates:
               if build_date not in project_dates:
                    project_history.append({build_date: 'none'})     
        project_history = sorted(project_history, key=lambda x: list(x.keys()))
        
        build_history.append(
            RepoHistory(
                repo_name=repo_name, 
                build_history=project_history
            ).to_dict()
        )
        
    return build_history


if __name__ == '__main__':
    
    repo_paths = list_folder(NON_FLAKY_BUILD_DIR, check_depth=False)
    
    all_build_dates = get_all_build_dates(repo_paths)    
    
    flaky_builds_history_list = get_build_history(path=FLAKY_BUILD_DIR, build_dates=all_build_dates)
    
    print(f"Number of flaky history builds: {len(flaky_builds_history_list)}")
    
    # ----------------------------------------
    
    print("Writing history dataset...")
    
    with open(FLAKY_HISTORY_DATASET_FILE, 'w') as json_file:
        json.dump(flaky_builds_history_list, json_file, indent=4)    
        
    print("Compressing build dataset...")
    
    os.system(f"gzip {FLAKY_HISTORY_DATASET_FILE}")