import os
import time
from pathlib import Path
from utils.timeout_utils import run_command
from error_categorization.error_parser.docker_error_parser import get_error_segments_as_json


def check_dockerfile_exists(project_path):
    """
    Check if the Dockerfile exists in the current directory:
    
    Parameters:
        project_path (str): repository directory
        
    Returns:
        a tuple of (dockerfile_exists, dockerfile_path):
            dockerfile_exists (bool): whether the Dockerfile exists in the root directory, default=False
            dockerfile_path (str): path to the Dockerfile, default=''
    """
    
    path = Path(project_path)
    dockerfile_path = list(path.glob("Dockerfile*"))

    # check if only one Dockerfile exists
    if len(dockerfile_path) == 1:
        dockerfile_path = dockerfile_path[0]
        return (True, dockerfile_path)
    
    return (False, '')


def check_build_failure(build_output):
    success_message = "exporting to image"
    if success_message in build_output:
        return False
    return True


def read_and_parse_build_output(file_path):
    """
    Read and parse the build output from the shell script: if no error, return the build output, otherwise return the parsed error segments.
    
    Parameters:
        file_path (str): path to the shell output file
        
    Returns:
        a tuple of (error_code, build_output):
            error_code (int): return code of the build command: 0 if successful, 1 if failed
            build_output (str): output of the build command
    """
    
    with open(file_path, "r") as f:
        build_output = f.read()
        
    is_failed = check_build_failure(build_output)
    
    if not is_failed:
        return 0, build_output
    
    parsed_build_output = get_error_segments_as_json("", build_output)["error_segment"]
    
    return 1, parsed_build_output


def build_docker_image(project_path, dockerfile_path, iteration, output_folder, stage_version):
    """
    Build the Dockerfile for a specific iteration and clean the Docker daemon.
    
    Parameters:
        project_path (str): repository directory
        dockerfile_path (str): path to the Dockerfile
        iteration (int): current build iteration number
    
    Returns:
        a tuple of (return_code, build_output):
            return_code (int): return code of the build command: 0 if successful, 1 if failed
            build_output (str): output of the build command
    """
    
    timeout = 2000
    image_name = project_path.split("/")[-1].replace("@", "_")
    
    
    # generate the command to build the Dockerfile
    docker_build_command = f"""sudo docker build -t image_name_{stage_version} -f {dockerfile_path} {project_path}  --no-cache"""
    shell_output = f"{output_folder}/{stage_version}_build_output.log"
    docker_build_command = f"{docker_build_command} > {shell_output} 2>&1"
    
    # execute and log the build command
    start_time = time.time()
    exec_out = run_command(docker_build_command, timeout)
    end_time = time.time()
    
    duration = end_time - start_time
    (minutes, seconds) = (duration // 60, duration % 60)
    print("\tDuration: {:d}:{:.2f}".format(int(minutes), seconds))

    shell_file = open(shell_output, "a")

    # check exec duration
    if duration >= timeout:
        shell_file.write(f"Duration: {timeout}")
    else:
        shell_file.write(
            "Duration: {:.0f}:{:.2f}".format(minutes, seconds))
        
    # clean the Docker daemon
    print("\tCleaning the Docker daemon...")
    clean_command = """sudo docker builder prune -af && sudo docker system prune -af"""
    exec_out = run_command(clean_command, timeout)
    
    # read and parse the build output
    error_code, build_output = read_and_parse_build_output(shell_output)
    
    build_results_path = f"{output_folder}/build_history.txt"
    new_record = f"{stage_version}: success" if error_code == 0 else f"{stage_version}: failed\n"
    with open(build_results_path, "a") as f:
        f.write(new_record)
    
    return error_code, build_output


def extract_build_output(project_path, dockerfile_path, build_iterations, output_folder, stage="0"):
    """
    Build the Dockerfile and extract the build output:
    
    Parameters:
        project_path (str): repository directory
        dockerfile_path (str): path to the Dockerfile
        build_iterations (int): number of build iterations
        
    Returns:
        a tuple of (is_flaky, build_output):
            is_flaky (bool): whether the Dockerfile is flaky, default=False
            build_output (list): list of build outputs, default=[]
    """
    
    build_output = ""
    is_flaky = False
    iterations = 0
    
    for i in range(build_iterations):
        print(f"Iteration {i+1}:")
        stage_version = f"v{stage}_{i+1}"
        return_code, build_output = build_docker_image(project_path, dockerfile_path, i, output_folder, stage_version)
        iterations += 1
        
        if return_code != 0:
            is_flaky = True
            break
    
    # print(f"Removing build outputs after {iterations} iterations")
    # os.system(f"rm -rf {output_folder}/*")
    
    return is_flaky, build_output