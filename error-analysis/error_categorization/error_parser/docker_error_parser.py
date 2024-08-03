import re
from tqdm import tqdm
from utils.file_utils import list_files_with_extension, list_folder, read_file, remove_and_generate_new_dir
from utils.string_utils import split_string_with_delimiters, string_contains_keys, remove_pattern_from_string
from path_config import ROOT_PATH

STAGE_SUCCESS_PATTERN = r"#\d+\sDONE\s\d+\.?\d*s"  # patterns like "#1 DONE 0.1s" which indicates the stage is done successfully
STEP_PATTERN = r'#\d+\s\d+(?:\.\d+)?\s'  # patterns like "#14 1.234 "
STEP_PATTERN_SECOND_PART = r'\d+\.\d+ ' # patterns like "#1.234 "
STEP_PATTERN_FIRST_PART = r'#\d+\s'  # patterns like "#14 "
DELIMITERS = ["\n------\n", "\n--------------------\n"]
ERROR_KEYWORDS = ["ERROR:", "ERROR ", "error:", "Err:", "E:", "W:", "NameError", "ERR!", "[ERROR]", "Error ", "Error: ", "Error]", "ParseError", "FetchError", "[Error", " error ", "'error'", "\"error\"", "'Error'", "\"Error\"", "'ERROR'", "\"ERROR\""]
IGNORE_KEYWORDS = ["+--", "`--", "└──"]  # keywords which demonstrate the hierarchy of packages installed
DOCKERFILE_ERROR_INDICATOR = ">>> " # indicator of the line of error in Dockerfile mentioned in the error message
DURATION_INDICATOR = "Duration: "
UNKNOWN = "unknown"
SIMILARITY_THRESHOLD = 0.9 # TODO: threshold for similarity between two lines of error build log
MAX_ERROR_SEGMENT_LINES = 100

DEFAULT_DIRECTORY_NAME = ROOT_PATH + '/possible-flaky-repos/'


def get_last_n_lines(string, n=2000):
    lines = string.split('\n')
    total_lines = len(lines)

    if total_lines > n:
        last_n_lines = lines[-n:]
    else:
        last_n_lines = lines

    return '\n'.join(last_n_lines)

def trim_error(error_part, stderr, original_error_segment="", check_length=False):
    lines = error_part.splitlines()
    filtered_lines = [line for line in lines if len(line) != 1] # remove lines with less than 4 characters
    error_part = '\n'.join(filtered_lines)
    
    error_part = re.sub('\n+', '\n', error_part)
     
    num_of_lines = len(error_part.splitlines())
    
    if (check_length) and (num_of_lines >= MAX_ERROR_SEGMENT_LINES): # if the error part is too long, it's probably because of repeating patterns
        error_part = original_error_segment
    
    if (stderr not in error_part):
        error_part = error_part + "\n" + stderr
    
    return error_part


def get_stderr(error_message):
    return error_message.split("\n")[0]


def parse_error_part(error_segments, path=''):
    error_lines = []
    docker_lines = []

    if len(error_segments) == 0:
        return UNKNOWN, UNKNOWN, UNKNOWN

    elif len(error_segments) == 1:
        
        error_parts = error_segments[0].split("\n")
        
        stderr = remove_pattern_from_string([STEP_PATTERN, STEP_PATTERN_FIRST_PART, STEP_PATTERN_SECOND_PART], error_parts[-1])
        
        if len(error_parts) < 3: # probably one-line error message
            return stderr, UNKNOWN, stderr
        
        step_pattern = re.findall(STEP_PATTERN, error_parts[-2]) # find step pattern in the last line before stderr
        considerable_lines = 3 # for simplicity: last 3 lines before stderr
        
        if len(step_pattern) > 0:
            step_second_part_pattern = step_pattern[0][3:] # remove "#n " from the step pattern
            patterns_found = len([line for line in error_parts if ((step_pattern[0] in line) or (step_second_part_pattern in line))])
            considerable_lines = considerable_lines if patterns_found >= 10 else patterns_found # at most 10 lines before stderr
        
        for i in range(-1-considerable_lines, -1):
            pruned_line = remove_pattern_from_string([STEP_PATTERN, STEP_PATTERN_FIRST_PART, STEP_PATTERN_SECOND_PART], error_parts[i])
            error_lines.append(pruned_line)
        
        error_lines.append(stderr)
        error_part = "\n".join(error_lines)
        error_part = trim_error(error_part, stderr)
          
        return error_part, UNKNOWN, stderr
    
    elif len(error_segments) < 5: # mainly due to "no space left on device" issue, or conditions where "Dockerfile: {n}" is concatenated with with error summary and error section, or rare/abnormal conditions

        docker_part, stderr = error_segments[-2], get_stderr(error_segments[-1])
        docker_parts = docker_part.split("\n")
        
        for docker_part in docker_parts:
            if DOCKERFILE_ERROR_INDICATOR in docker_part:
                docker_lines.append(docker_part.split(DOCKERFILE_ERROR_INDICATOR)[1])
        docker_part = "\n".join(docker_lines)
         
        return "", docker_part, stderr

    """
    structure of error_segments:
    [0]: last stage of execution which ended up with error/errors
    [1]: summary of the source of error
    [2]: containing: "Dockerfile:<line of error>"
    [3]: part of dockerfile which caused the error
    [4]: one-line error message (stderr) + duration of the whole build
    """
    last_stage, original_error_part, docker_part = error_segments[0], "\n".join(error_segments[1:-3]), error_segments[-2]
    
    
    steps_to_find = re.findall(STEP_PATTERN, original_error_part) # find steps like '#{n} {x}.{y} ' in the error part
    steps_second_parts = re.findall(STEP_PATTERN_SECOND_PART, original_error_part) # find steps like '{x}.{y} ' in the error part
    steps_to_find.extend(steps_second_parts) # add both patterns: '#{n} {x}.{y} ' and '{x}.{y} ' to the list of steps to find
    steps_to_find = list(set(steps_to_find)) # remove duplicates
    
    last_stages = last_stage.split("\n")
    error_parts = original_error_part.split("\n")
    docker_parts = docker_part.split("\n")

    error_segment_parts = split_string_with_delimiters(original_error_part, DELIMITERS)
    for error_segment_part in error_segment_parts:
        lines = error_segment_part.split("\n")   
        error_lines.append(lines[0])  # first line of original_error_part: indicates the stage of error
        
    for stage in last_stages: # find error lines in the last stage
        pruned_stage = remove_pattern_from_string([STEP_PATTERN, STEP_PATTERN_FIRST_PART, STEP_PATTERN_SECOND_PART], stage)
        if not string_contains_keys(stage, IGNORE_KEYWORDS):
            
            if (string_contains_keys(stage, steps_to_find)): # if the step is mentioned in the summary
                error_lines.append(pruned_stage)
            elif (string_contains_keys(pruned_stage, ERROR_KEYWORDS) or (pruned_stage in error_parts)): # if the line contains error keywords or is mentioned in the error summary
                new_step = re.findall(STEP_PATTERN, stage)
                new_step.extend(re.findall(STEP_PATTERN_SECOND_PART, stage))
                steps_to_find.extend(new_step)

                error_lines.append(pruned_stage)

    stderr = error_lines[-1]
    error_part = "\n".join(error_lines)
    error_part = trim_error(error_part, stderr, original_error_part, True)

    for docker_part in docker_parts:
        if DOCKERFILE_ERROR_INDICATOR in docker_part:
            docker_lines.append(docker_part.split(DOCKERFILE_ERROR_INDICATOR)[1])

    docker_part = "\n".join(docker_lines)

    return error_part, docker_part, stderr

def remove_duration(raw_build_log: str) -> str:
    build_lines = raw_build_log.split("\n")
    raw_build_log = "\n".join([line for line in build_lines if DURATION_INDICATOR not in line])
    return raw_build_log

def get_error_segments(raw_build_log: str) -> str:
    number_of_lines = len(raw_build_log.split("\n"))
    if number_of_lines < 1000:
        error_part = raw_build_log
    else: # log output is too long, we only consider the last part which resulted in error    
        build_segments = re.split(STAGE_SUCCESS_PATTERN, raw_build_log)
        error_part = build_segments[-1]
    
    error_part = get_last_n_lines(error_part)
    
    error_segments = split_string_with_delimiters(error_part, DELIMITERS)    
    return error_segments


def get_error_segments_from_file_content(file_contents: str):
    number_of_lines = len(file_contents.split("\n"))
    if number_of_lines < 1000:
        error_part = file_contents
    else: # log output is too long, we only consider the last part which resulted in error    
        build_segments = re.split(STAGE_SUCCESS_PATTERN, file_contents)
        error_part = build_segments[-1]
        
    error_part = get_last_n_lines(error_part)
    
    error_segments = split_string_with_delimiters(error_part, DELIMITERS)    
    return error_segments


def get_build_segments(file_content: str):
    duration = ""
    build_segments = re.split(STAGE_SUCCESS_PATTERN, file_content)
    last_line = file_content.split("\n")[-1]
    if DURATION_INDICATOR in last_line:
        duration = last_line
    return build_segments[:-1], duration


def get_error_segments_as_json(filename, raw_build_log: str):
    build_info = {
        "file_name": [],
        "error_segment": [],
        "dockerfile_error_line": [],
        "stderr": []
    }
    
    raw_build_log = remove_duration(raw_build_log)

    error_segments = get_error_segments(raw_build_log)
        
    error_part, dockerfile_error_line, stderr = parse_error_part(error_segments, filename)

    build_info["file_name"] = filename
    build_info["error_segment"] = error_part
    build_info["dockerfile_error_line"] = dockerfile_error_line
    build_info["stderr"] = stderr

    return build_info


def list_parsed_errors(file_paths):
    parsed_errors = []
    for path in file_paths:
        raw_build_log = read_file(path)
        build_info = get_error_segments_as_json(path, raw_build_log)
        parsed_errors.append(build_info)
        
    return parsed_errors


def get_error_context(parsed_error):
    filename = parsed_error["file_name"].split("/")[-1].replace(".failure", "")
    error_context = ""
    
    for key in parsed_error.keys():
        if 'file_name' not in key:
            error_context += "** " + key.upper() + " **: \n" + parsed_error[key] + "\n"
    
    return filename, error_context

def add_parsed_errors(parsed_errors, error_dir):
    for parsed_error in parsed_errors:
        file_name, context = get_error_context(parsed_error)
        
        file_path = error_dir + "/" + file_name
        # print(file_path)
        with open(file_path, 'w') as file:
            file.write(context)

# if __name__ == "__main__":
    
#     list_of_repos = list_folder(DEFAULT_DIRECTORY_NAME)
    
#     for repo_dir in tqdm(list_of_repos):
            
#         # for each repo dir, search for all FAILURE log files
#         list_of_files = list_files_with_extension(repo_dir, extension="failure.log")   

#         # for each .failure.log file, parse the error segments 
#         list_of_parsed_errors = list_parsed_errors(list_of_files)
        
#         error_dir = repo_dir + "/" + "parser-results"
#         remove_and_generate_new_dir(error_dir)
        
#         add_parsed_errors(list_of_parsed_errors, error_dir)
