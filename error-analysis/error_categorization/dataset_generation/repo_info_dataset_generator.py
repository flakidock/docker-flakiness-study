import json
from tqdm import tqdm
import os
from utils.file_utils import read_file, list_files_with_extension, list_folder
from utils.string_utils import split_unique_build_files
from dataset_types import RepoInfo, RepoMetadata
from error_categorization.dataset_generation.constants import FLAKY_BUILD_DIR, NON_FLAKY_BUILD_DIR, SUMMARY_DIR, SUMMARY_FILE_IDENTIFIER, FINAL_CATEGORY_KEY, NON_FLAKY_BUILD_DATASET_FILE, FLAKY_BUILD_DATASET_FILE


def get_first_successful_build_path(project_path):
    build_files = list_files_with_extension(project_path, '.log', None, check_depth=False)
    build_files.sort()
    
    for build_file in build_files:
        build_status = build_file.split('/')[-1].split('.')[-2]
        if build_status == 'success':
            return build_file 

    print(f"No successful build found for {project_path}")
    return ""


def get_build_info(path, repos_status):
    build_info = []
    
    print(f"Getting build info for {repos_status} repos...")
    
    repo_paths = list_folder(path, check_depth=False)
    for repo_path in tqdm(repo_paths):
        
        repo_name = repo_path.split('/')[-1]
        dockerfile_build_path = repo_path + '/Dockerfile'
        
        if repos_status == 'non-flaky':
            first_successful_build_path = get_first_successful_build_path(repo_path)
            
            build_info.append(
                RepoInfo(
                    repo_name=repo_name, 
                    build_time=first_successful_build_path.split('/')[-1].split('.')[0], 
                    dockerfile=read_file(dockerfile_build_path, 'latin1'), 
                    build_output=read_file(first_successful_build_path, 'latin1'), 
                    category='non-flaky',
                    metadata=RepoMetadata()    
                ).to_dict()
            )
        else: # flaky repos
            summary_files = list_files_with_extension(repo_path + SUMMARY_DIR, SUMMARY_FILE_IDENTIFIER)
            parser_files = list_files_with_extension(repo_path + SUMMARY_DIR, '.log', SUMMARY_FILE_IDENTIFIER)
            summary_files.sort()
            parser_files.sort()
            
            for summary_file, parser_file in zip(summary_files, parser_files):
                with open(summary_file, 'r') as f:
                    summary_data = json.load(f)
                
                # read a txt file and split it into unique build errors
                with open(parser_file, 'r') as f:
                    parser_data = f.read()
                    
                parser_info = split_unique_build_files(parser_data)
                    
                build_date = summary_file.split('/')[-1].split(SUMMARY_FILE_IDENTIFIER)[-1].replace('.log.json', '')
                failure_build_file = repo_path + '/' + build_date + '.failure.log'
                
                newRepoMetadata = RepoMetadata(
                    error_segment=parser_info["error_segment"], 
                    error_summary=summary_data["summary"],
                    initial_category=summary_data["initial cluster name"],
                    dockerfile_error_line=parser_info["error_line"],
                    dockerfile_error_segment=parser_info["dockerfile_segment"],
                    dockerfile_exit_code=parser_info["exit_code"],
                    stderr_line=parser_info["stderr_line"],
                    sources_of_error=summary_data["sources of error"]
                )
                
                build_info.append(
                    RepoInfo(
                        repo_name=repo_name, 
                        build_time=build_date, 
                        dockerfile=read_file(dockerfile_build_path, 'latin1'),
                        build_output=read_file(failure_build_file, 'latin1'),
                        category=summary_data[FINAL_CATEGORY_KEY],
                        metadata=newRepoMetadata    
                    ).to_dict()
                )
    return build_info


if __name__ == '__main__':
    
    non_flaky_builds_info_list = get_build_info(path=NON_FLAKY_BUILD_DIR, repos_status='non-flaky')
    flaky_builds_info_list = get_build_info(path=FLAKY_BUILD_DIR, repos_status='flaky')
    
    print(f"Number of non-flaky builds: {len(non_flaky_builds_info_list)}")
    print(f"Number of flaky builds: {len(flaky_builds_info_list)}")
    
    # ----------------------------------------
    
    print("Writing build dataset...")
    
    with open(NON_FLAKY_BUILD_DATASET_FILE, 'w') as json_file:
        json.dump(non_flaky_builds_info_list, json_file, indent=4)
    
    with open(FLAKY_BUILD_DATASET_FILE, 'w') as json_file:
        json.dump(flaky_builds_info_list, json_file, indent=4)
        
    print("Compressing build dataset...")
    
    # zip with gzig
    os.system(f"gzip {NON_FLAKY_BUILD_DATASET_FILE}")
    os.system(f"gzip {FLAKY_BUILD_DATASET_FILE}")
