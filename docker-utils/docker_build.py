import os
from pathlib import Path
import argparse
import logging
import yaml
import time
import subprocess
import multiprocessing as mp
import datetime
from utils.timeout import run_command
from utils.project_details import ProjectDetails

WORKING_DIRECTORY = '/home/contextml/temporal-study-docker/temporal-study/'  # your working directory

import sys

sys.path.append(WORKING_DIRECTORY + 'data-collection/')

from clone_git_repos import get_repo_list, get_repo_directory, get_repo_from_repo_directory

# for simple testing
GENERAL_CONFIG_FILE = WORKING_DIRECTORY + 'config-build/general-build.yaml'
CONFIG_FILE = WORKING_DIRECTORY + 'config-build/single-process-vm1.yaml'

SUPER_USER = 'sudo '
TIMEOUT = 'TIMEOUT'
DEFAULT_END = 'END'


def list_subfiles(folder_path):
    sub_folders = []
    project_repos = []
    
    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            sub_folder_path = os.path.join(root, directory)
            sub_folders.append(sub_folder_path)
            
        # only the first level of subfolders
        break
    
    for sub_folder in sub_folders:
        for root, dirs, files in os.walk(sub_folder):
            project_repos.extend(files)

    return project_repos


def get_file_items(input_file):
    repo_file = open(input_file, 'r')

    repo_list = [r.replace('\n', '') for r in repo_file.readlines()]
    repo_file.close()

    return repo_list


def check_dockerfile_exists(repo_dir, input_dirs):
    """
    Check if the Dockerfile exists in the root directory of the repository: (input_dir[x]/repo_dir)
    
    Parameters:
        repo_dir (str): repository directory
        input_dirs (list): list of input directories
        
    Returns:
        a tuple of (dockerfile_exists, dockerfile_path, part_number):
            dockerfile_exists (bool): whether the Dockerfile exists in the root directory, default=False
            dockerfile_path (str): path to the Dockerfile, default=''
            part_number (int): part number (process number) of the repository, default=0
    """
    
    for i, input_dir in enumerate(input_dirs):
        path = Path(f"{input_dir}/{repo_dir}")
        dockerfile_path = list(path.glob("Dockerfile*"))

        # check 1 dockerfile in the root directory
        if len(dockerfile_path) != 1:
            continue
        else:
            dockerfile_path = str(dockerfile_path[0]).split(
                '/')[-1]  # get file name from the path
            return (True, dockerfile_path, i)

    return (False, '', 0)  # default part_number=0


def clean_docker_daemon(current_builds, loggers, clean_rate, cleanup_file, timeout, image_names=[""], part_numbers=[0],
                        remove_image=True):
    """
    Clean the docker daemon every "clean_rate" builds.
    
    Parameters:
        current_builds (int): number of builds so far
        loggers (list): list of loggers (as we are using multiprocessing, we need a logger for each process)
        clean_rate (int): clean the docker daemon every "clean_rate" builds
        cleanup_file (str): bash file to clean the docker daemon
        timeout (int): timeout duration for the containerization process
        image_names (list): list of image names to remove
        part_numbers (list): list of part numbers for the images (each part number represents the process number in which the image was built)
        remove_image (bool): whether there is any image to remove
    """
    
    if remove_image:
        for image_name, part_number in zip(image_names, part_numbers):
            run_command(f"{SUPER_USER}docker rmi {image_name}", timeout)
            loggers[part_number].debug("[REMOVING IMAGE ...]")

    if (current_builds % clean_rate == 0):
        print("cleaning-round1")

        start = time.time()
        run_command(f"bash {cleanup_file} > clean_out.log 2>&1", timeout)
        end = time.time()

        # if the cleanup takes more than 80% of the timeout, means the cleanup is stuck, run it again
        if (end - start) >= int(0.8 * timeout):  
            print("cleaning-round2")
            run_command(f"bash {cleanup_file} > clean_out.log 2>&1", timeout)

        print("cleaning-finished")

        # to log the cleanup only once per loggers
        part_set = set(part_numbers)
        for part_number in part_set:
            loggers[part_number].debug("[CLEANING UP ...]")


def build_single_image(queue, i, part_number, repo_name, repos_len, repo_directory, exec_command, timeout,
                       shell_output):
    """
    Given the repository name, build the docker image and store the logs in the output directory.
    
    Parameters:
        queue (multiprocessing.Queue): queue to store the build message
        i (int): index of the repository
        part_number (int): part number (process number) of the repository
        repo_name (str): repository name
        repos_len (int): total number of repositories
        repo_directory (str): repository directory
        exec_command (str): command to execute the docker build
        timeout (int): timeout duration for the containerization process
        shell_output (str): shell output file to store the logs
    """
    
    build_message = ''

    # execute command
    start_time = time.time()
    exec_out = run_command(exec_command, timeout)
    end_time = time.time()
    
    duration = end_time - start_time
    (minutes, seconds) = (duration // 60, duration % 60)

    shell_file = open(shell_output, "a")

    # check exec duration
    if duration >= timeout:
        shell_file.write(f"Duration: {TIMEOUT}")
    else:
        shell_file.write(
            "Duration: {:.0f}:{:.2f}".format(minutes, seconds))

    shell_file.close()

    if duration >= timeout:
        build_message = f"[END]: index: {i}/{repos_len} | repo: {repo_directory} | Duration: {TIMEOUT}"
    else:
        build_message = f"[END]: index: {i}/{repos_len} | repo: {repo_directory}" + \
                        "| Duration: {:.0f}:{:.2f}".format(minutes, seconds)

    queue.put([repo_name, part_number, build_message])


def build_docker_image(repos, input_dirs, output_dirs, timeout, clean_rate, loggers, cleanup_file, num_processes):
    queue = mp.Queue()

    # initial cleanup: start with a clean docker daemon
    clean_docker_daemon(current_builds=0, loggers=loggers, clean_rate=1,
                        cleanup_file=cleanup_file, timeout=timeout, remove_image=False)

    repos_len = len(repos)

    # number of builds (n-process builds) so far
    current_builds = 0
    
    # chunk the repositories based on the number of processes
    for i, repos_group in enumerate([repos[j:j + num_processes] for j in range(0, len(repos), num_processes)]):

        # initialize lists to store values
        project_details = []

        # group repos for multi-processing
        for k, repo in enumerate(repos_group):
            repo_name = (repo.split('/')[-1].replace('.git', '')).lower()
            repo_directory = get_repo_directory(repo)
            
            (dockerfile_exists, dockerfile_path, part_number) = check_dockerfile_exists(
                repo_directory, input_dirs)

            input_dir, output_dir, logger = (
                input_dirs[part_number], output_dirs[part_number], loggers[part_number])

            build_shell_command = f"{SUPER_USER}docker build {input_dir}/{repo_directory} -t {repo_name} -f {input_dir}/{repo_directory}/{dockerfile_path} --no-cache"
            shell_output = f"{output_dir}/{repo_directory}.log"
            exec_command = f"{build_shell_command} > {shell_output} 2>&1"

            project_detail = ProjectDetails(index=(i * num_processes + k + 1), repo_name=repo_name,
                                            repo_directory=repo_directory, dockerfile_exists=dockerfile_exists,
                                            dockerfile_path=dockerfile_path, input_dir=input_dir,
                                            output_dir=output_dir, part_number=part_number, shell_output=shell_output,
                                            exec_command=exec_command)

            project_details.append(project_detail)

        # MULTIPROCESSING: execute docker build for each group of repos
        processes = []
        current_part_numbers = []
        current_repo_names = []
        num_of_builds = 0
        
        for project in project_details:
            if ((not os.path.exists(project.shell_output)) and project.dockerfile_exists):
                p = mp.Process(target=build_single_image, args=(queue, project.index, project.part_number,
                                                                project.repo_name, repos_len, project.repo_directory,
                                                                project.exec_command,
                                                                timeout, project.shell_output))
                processes.append(p)

                num_of_builds += 1

        # start the processes
        for p in processes:
            p.start()

        # wait for all processes to finish
        for p in processes:
            p.join()

            repo_name, part_number, build_message = queue.get()
            current_part_numbers.append(part_number)
            current_repo_names.append(repo_name)

            loggers[part_number].debug(build_message)

        # clean the docker daemon every "clean_rate" builds
        if num_of_builds > 0:
            current_builds += 1

            clean_docker_daemon(current_builds, loggers, clean_rate,
                                cleanup_file, timeout, current_repo_names, current_part_numbers, True)

            for part_number in set(current_part_numbers):
                loggers[part_number].debug(
                    f"multiprocessing of {num_of_builds} builds finished.")

    # final cleanup
    clean_docker_daemon(current_builds=0, loggers=loggers, clean_rate=1,
                        cleanup_file=cleanup_file, timeout=timeout, remove_image=False)


def instantiate_logger(log_file, part_num):
    logger = logging.getLogger('build' + str(part_num))
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger


def zip_content(directory_to_zip, zip_folder):
    # Change directory to the target folder
    os.chdir(directory_to_zip)

    zip_file_name = f"{zip_folder}.zip"

    subprocess.run(['zip', '-r', zip_file_name, zip_folder])


def config_initials(args):
    """
    Generate the initial configurations for the build process
    
    Parameters:
        args (argparse.ArgumentParser): command line arguments: represents the config files
        
    Returns:
        general_config_content (dict): general configurations
        timeout (int): timeout duration for the containerization process
        clean_rate (int): clean the docker daemon every "clean_rate" images
        cleanup_file (str): bash file to clean the docker daemon
        num_processes (int): number of processes to run
        current_date (str): current date
        parent_dir (str): parent directory
        input_dirs (list): list of input directories
        output_dirs (list): list of output directories
        repos (list): list of repositories
        loggers (list): list of loggers (as we are using multiprocessing, we need a logger for each process)
    """
    
    # read the general config (equal for all machines) and machine-specific config files
    general_config = open(args.general_conf_file, 'r')
    general_config_content = yaml.safe_load(general_config)
    config = open(args.config_file, 'r')
    config_content = yaml.safe_load(config)

    general_config.close()
    config.close()
    
    # extract configuration details
    (input_file, start_index, end_index, timeout, clean_rate, cleanup_file, num_processes, is_resume,
     resume_output_dir) = (
        general_config_content['parent_directory'] +
        general_config_content['working_directory'] +
        general_config_content['input_file'],

        config_content['start'],

        config_content['end'],

        general_config_content['timeout'],

        general_config_content['clean_rate'],

        general_config_content['parent_directory'] +
        general_config_content['working_directory'] +
        general_config_content['cleanup_file'],

        general_config_content['num_processes'],

        general_config_content['is_resume'],

        general_config_content['parent_directory'] +
        general_config_content['resume_output_dir']
    )

    # set input and output directories + log files + current date
    parent_dir = general_config_content['parent_directory']
    current_date = datetime.datetime.now().strftime('%Y-%m-%d-%H')

    # if the process is a resume process use the resume output directory
    if is_resume:
        general_output_dir = resume_output_dir
    else:
        general_output_dir = parent_dir + \
                             general_config_content['output_dir'] + current_date

    
    # extract input directories, output directories, log files, and part numbers ()
    input_dirs, output_dirs, log_files, part_nums = [], [], [], []
    for in_dir, out_dir, log_file in zip(config_content['input_inner_dir'],
                                         config_content['output_inner_dir'],
                                         config_content['log_file']):
        input_dirs.append(
            parent_dir + general_config_content['input_dir'] + in_dir)
        output_dirs.append(general_output_dir + '/' + out_dir)
        log_files.append(general_output_dir + '/' + log_file)
        part_nums.append(int(in_dir.split('-')[0].replace('part', '')))

    for output_dir in output_dirs:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # get the list of repositories
    repos = get_repo_list(input_file)

    # set the start and end index for the repositories based on the config file: 
    # Machine1: 0-5000, Machine2: 5000-10000, Machine3: 10000-15000, Machine4: 15000-END(shipwright dataset)
    if end_index == DEFAULT_END:
        repos = repos[start_index:]
    else:
        repos = repos[start_index:int(end_index)]

    # if there is an input checker file: meaning it is a resume process, get the checked repositories
    if ("input_checker_file" in general_config_content):
        input_checker_file = general_config_content['parent_directory'] + \
                             general_config_content['working_directory'] + \
                             general_config_content["input_checker_file"]

        checked_repos = get_file_items(input_checker_file)
        repo_directories = [get_repo_directory(repo) for repo in repos]
        repos = list(set(checked_repos) & set(repo_directories))
        repos = [get_repo_from_repo_directory(repo) for repo in repos]

    loggers = []
    for log_file, part_num in zip(log_files, part_nums):
        new_logger = instantiate_logger(log_file, part_num)
        loggers.append(new_logger)
        new_logger.debug(f"build{part_num}")

    # if it is a resume process, get the built repositories and remove them from the list of repositories
    if is_resume:
        built_repos = list_subfiles(resume_output_dir)
        built_repos = [repo.replace('.log', '') for repo in built_repos]

        main_repo_dirs = [get_repo_directory(repo) for repo in repos]
        repos = list(set(main_repo_dirs) - set(built_repos))
        repos = [get_repo_from_repo_directory(repo) for repo in repos]

    return general_config_content, timeout, clean_rate, cleanup_file, num_processes, current_date, parent_dir, input_dirs, output_dirs, repos, loggers


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--general_conf_file',
                        help='general config file', type=str, default=GENERAL_CONFIG_FILE)
    parser.add_argument('-c', '--config_file',
                        help='config file', type=str, default=CONFIG_FILE)

    args = parser.parse_args()

    general_config_content, timeout, clean_rate, cleanup_file, num_processes, current_date, parent_dir, input_dirs, output_dirs, repos, loggers = config_initials(
        args)

    build_docker_image(repos, input_dirs, output_dirs, timeout,
                       clean_rate, loggers, cleanup_file, num_processes)

    zip_content(
        parent_dir, general_config_content['output_dir'] + current_date)
