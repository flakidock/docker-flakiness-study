import os
import threading
import subprocess
import argparse
import yaml
import logging
from datetime import datetime
from tqdm import tqdm

WORKING_DIRECTORY = '/home/contextml/temporal-study-docker/temporal-study/' # your working directory

import sys
sys.path.append(WORKING_DIRECTORY + 'general-info-extraction/')
from repo_info_extraction.fetch_dated_commit_sha import fetch_last_commit_sha

GENERAL_CONFIG_FILE = WORKING_DIRECTORY + \
    'configs/git_clone/general-config.yaml'
CONFIG_FILE = WORKING_DIRECTORY + 'configs/git_clone/part1.yaml'

DEFAULT_END = 'END'

# INPUT_FILE = WORKING_DIRECTORY + 'dataset/shipwright/shipwright_repos.txt'
# OUTPUT_DIR = WORKING_DIRECTORY + 'temp_repos_cloned'
# DEFAULT_START = 0
# THREADS = 20

total_cloned = 0


def instantiate_logger(log_file, part_num):
    logger = logging.getLogger('clone' + str(part_num))
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def get_repo_list(path):
    repo_file = open(path, 'r')

    repo_list = [r.replace('\n', '') for r in repo_file.readlines()]
    repo_list = [r.replace('git://', 'https://') for r in repo_list]

    repo_file.close()

    return repo_list


def make_and_enter_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)

def get_repo_directory(repo):
    (repo_owner, repo_name) = (repo.split('/')
                               [-2], repo.split('/')[-1].replace('.git', ''))
    return f"{repo_owner}@{repo_name}"


def get_repo_from_repo_directory(repo_directory):
    return f"https://github.com/{repo_directory.split('@')[0]}/{repo_directory.split('@')[1]}"


def clone_repos(repos, check_repos, i, logger):
    global total_cloned
    for repo in repos:
        if (repo not in check_repos):
            check_repos.add(repo)
            
            repo_dir = get_repo_directory(repo)
            new_command = f"git clone {repo} {repo_dir}"

            new_process = subprocess.Popen(new_command, shell=True)
            new_process.communicate()
            new_process.terminate()
            total_cloned += 1

            logger.debug(
                f"Total cloned: {total_cloned}, thread: {i}, repo: {get_repo_directory(repo)}")


def fetch_repos(input_file, output_dir, threads, start_index, end_index, logger):
    repos = get_repo_list(input_file)  # get list of repositories

    if end_index == DEFAULT_END:
        repos = repos[start_index:]
    else:
        repos = repos[start_index:int(end_index)]

    make_and_enter_directory(output_dir)  # mkdir + cd -> to repo folder

    thread_list = []
    checked_repos = set()
    for i in range(threads):  # for parallelism

        t = threading.Thread(target=clone_repos, args=(
            repos, checked_repos, i, logger))

        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()

def checkout_repos(input_file, output_dir, start_index, end_index, clone_datetime, logger):
    repos = get_repo_list(input_file)  # get list of repositories

    if end_index == DEFAULT_END:
        repos = repos[start_index:]
    else:
        repos = repos[start_index:int(end_index)]

    for repo in tqdm(repos):
        repo_path = output_dir + '/' + get_repo_directory(repo)
        if os.path.isdir(repo_path):
            os.chdir(repo_path)
            
            last_commit_sha = fetch_last_commit_sha(repo_path, clone_datetime)
            new_command = f"git checkout {last_commit_sha}"
            new_process = subprocess.Popen(new_command, shell=True)
            new_process.communicate()
            new_process.terminate()

            logger.debug(
                f"Repo: {get_repo_directory(repo)}, checkout to: {last_commit_sha}")

def update_repos():  # to be implemented
    pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--general_conf_file',
                        help='general config file', type=str, default=GENERAL_CONFIG_FILE)
    parser.add_argument('-c', '--config_file',
                        help='config file', type=str, default=CONFIG_FILE)

    args = parser.parse_args()

    general_config = open(args.general_conf_file, 'r')
    general_config_content = yaml.safe_load(general_config)
    config = open(args.config_file, 'r')
    config_content = yaml.safe_load(config)

    general_config.close()
    config.close()

    (input_file, output_dir, threads, start_index, end_index, log_file, part_num) = (
        general_config_content['parent_directory'] +
        general_config_content['working_directory'] +
        general_config_content['input_file'],

        general_config_content['parent_directory'] +
        general_config_content['output_dir'] +
        config_content['output_inner_dir'],

        general_config_content['threads'],

        config_content['start'],

        config_content['end'],

        general_config_content['parent_directory'] +
        general_config_content['log_dir'] +
        config_content['log_file'],

        int(config_content['output_inner_dir'].split(
            '-')[0].replace("part", ''))
    )
    
    dated_cloning = False
    clone_datetime = None
    if ("last_commit" in general_config_content):
        dated_cloning = True
        date_attributes = general_config_content["last_commit"]
        clone_datetime = datetime(date_attributes[0], date_attributes[1], date_attributes[2], date_attributes[3], date_attributes[4])    

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger = instantiate_logger(log_file, part_num)

    fetch_repos(input_file, output_dir, threads,
                start_index, end_index, logger)
    
    if (dated_cloning):
        checkout_repos(input_file, output_dir, start_index, end_index, clone_datetime, logger)