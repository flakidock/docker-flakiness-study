from pathlib import Path
from clone_git_repos import get_repo_list, get_repo_directory, get_repo_from_repo_directory
import argparse
import yaml
import os
from tqdm import tqdm
import subprocess

WORKING_DIRECTORY = os.getcwd()
parts = WORKING_DIRECTORY.split("/")
parts = parts[:-1]

WORKING_DIRECTORY = "/".join(parts) + "/"

GENERAL_CONFIG_FILE = WORKING_DIRECTORY + \
    'configs/git_clone/general-config.yaml'


def check_dockerfile_exists(repo_dir, input_dirs):
    for i, input_dir in enumerate(input_dirs):
        path = Path(f"{input_dir}/{repo_dir}")
        dockerfile_path = list(path.glob("Dockerfile*"))

        if len(dockerfile_path) != 1:
            continue
        else:
            dockerfile_path = str(dockerfile_path[0]).split(
                '/')[-1]  
            
            return (dockerfile_path, i, input_dir.split('/')[-1])

    return ('', -1, '')  # default part_number = -1


def extract_dockerfiles(repositories, repo_dirs, dockerfiles_dir):
    for repo in tqdm(repositories):
        dockerfile_path, repo_idx, part_dir = check_dockerfile_exists(repo, repo_dirs)
        
        if repo_idx >= 0: # dockerfile exists
            current_dockerfile_path = f"{repo_dirs[repo_idx]}/{repo}/{dockerfile_path}"
            output_path = f"{dockerfiles_dir}/{repo}.Dockerfile"
            
            content = ''
            if (not os.path.isdir(current_dockerfile_path)) and os.path.isfile(current_dockerfile_path):
                with open(current_dockerfile_path, encoding='latin1') as file:
                    # read the content of the input file
                    content = file.read()

                # open the output file
                with open(output_path, 'w') as file:
                    # write the content to the output file
                    file.write(content)
            
def zip_content(directory_to_zip, zip_folder):
    # Change directory to the target folder
    os.chdir(directory_to_zip)

    zip_file_name = f"{zip_folder}.zip"
    
    subprocess.run(['zip', '-r', zip_file_name, zip_folder])
            
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--general_conf_file',
                        help='general config file', type=str, default=GENERAL_CONFIG_FILE)

    args = parser.parse_args()

    general_config = open(args.general_conf_file, 'r')
    general_config_content = yaml.safe_load(general_config)

    general_config.close()

    dataset_dir = general_config_content['parent_directory'] + \
        general_config_content['working_directory'] + \
        general_config_content['input_file']

    repo_dir = general_config_content['parent_directory'] + \
        general_config_content['output_dir']
        
    repo_dirs = [f.path for f in os.scandir(repo_dir) if f.is_dir()]
    part_dirs = [dir.split('/')[-1] for dir in repo_dirs]

    dockerfiles_dir = general_config_content['parent_directory'] + \
        general_config_content['dockerfiles_dir']
        
    dockerfiles_dirs = [dockerfiles_dir + part_dir for part_dir in part_dirs]
    
    if not os.path.exists(dockerfiles_dir):
        os.makedirs(dockerfiles_dir)

    repositories = get_repo_list(dataset_dir)
    repositories = [get_repo_directory(repo) for repo in repositories]
    
    extract_dockerfiles(repositories, repo_dirs, dockerfiles_dir)
    
    zip_folder = general_config_content['dockerfiles_dir'].replace('/', '')
    zip_content(
        general_config_content['parent_directory'], zip_folder)
