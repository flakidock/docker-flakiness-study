import pandas as pd
from error_categorization.error_parser.docker_error_parser import get_error_segments_as_json
from llm_apis import gpt_api_calls
from langchain_community.callbacks import get_openai_callback
from utils.file_utils import list_files_with_extension, list_files, read_file, serialize_json
from utils.string_utils import num_gpt_tokens_in_a_string, split_unique_build_files
from path_config import ROOT_PATH

DEFAULT_DIRECTORY_NAME = ROOT_PATH + '/possible-flaky-repos/'
UNIQUE_BUILD_PATH = 'unique-build-errors'
NON_UNIQUE_BUILD_FILE_IDENTIFIERS = ['llm-summary-', 'clusters']


def calc_stats():
    directory = DEFAULT_DIRECTORY_NAME
    list_of_files = list_files_with_extension(directory, extension="failure.log")

    token_count_file_name_stats = []
    token_count_error_segment_stats = []
    token_count_dockerfile_error_line_stats = []
    token_count_stderr_stats = []
    token_count_exit_code_stats = []

    token_count_complete_error_json_file_stats = []

    for path in list_of_files:
        raw_build_log = read_file(path)
        build_info = get_error_segments_as_json(path, raw_build_log)

        token_count_file_name = num_gpt_tokens_in_a_string(build_info["file_name"])
        token_count_error_segment = num_gpt_tokens_in_a_string(build_info["error_segment"])
        token_count_dockerfile_error_line = num_gpt_tokens_in_a_string(build_info["dockerfile_error_line"])
        token_count_stderr = num_gpt_tokens_in_a_string(build_info["stderr"])
        token_count_exit_code = num_gpt_tokens_in_a_string(build_info["stderr"].split(":")[-1])
        token_count_complete_error_json_file = num_gpt_tokens_in_a_string(serialize_json(build_info))

        token_count_file_name_stats.append(token_count_file_name)
        token_count_error_segment_stats.append(token_count_error_segment)
        token_count_dockerfile_error_line_stats.append(token_count_dockerfile_error_line)
        token_count_stderr_stats.append(token_count_stderr)
        token_count_exit_code_stats.append(token_count_exit_code)
        token_count_complete_error_json_file_stats.append(token_count_complete_error_json_file)
        
    
    list_of_unique_files = [file for file in list_files(directory) if (UNIQUE_BUILD_PATH in file) and
                            (not any(identifier in file for identifier in NON_UNIQUE_BUILD_FILE_IDENTIFIERS))]
    
    token_count_dockerfile_segment_stats = []
    
    for path in list_of_unique_files:
        raw_log = read_file(path)
        build_info = split_unique_build_files(raw_log)
        
        token_count_dockerfile_segment = num_gpt_tokens_in_a_string(build_info["dockerfile_segment"])
        
        token_count_dockerfile_segment_stats.append(token_count_dockerfile_segment)
    
    

    print("token_count_file_name_stats...")
    print(pd.Series(token_count_file_name_stats).describe())
    print("............................................")

    print("token_count_error_segment_stats...")
    print(pd.Series(token_count_error_segment_stats).describe())
    print("............................................")

    print("token_count_dockerfile_error_line_stats...")
    print(pd.Series(token_count_dockerfile_error_line_stats).describe())
    print("............................................")
    
    print("token_count_dockerfile_segment_stats...")
    print(pd.Series(token_count_dockerfile_segment_stats).describe())
    print("............................................")

    print("token_count_stderr_stats...")
    print(pd.Series(token_count_stderr_stats).describe())
    print("............................................")
    
    print("token_count_exit_code_stats...")
    print(pd.Series(token_count_exit_code_stats).describe())
    print("............................................")

    print("token_count_stats for the complete error json file...")
    print(pd.Series(token_count_complete_error_json_file_stats).describe())
    
    

def calc_unique_stats():
    pass

def fetch_unique_exit_codes():
    directory = DEFAULT_DIRECTORY_NAME
    list_of_files = list_files_with_extension(directory, extension="failure.log")
    unique_exit_codes = []

    for path in list_of_files:
        raw_build_log = read_file(path)
        build_info = get_error_segments_as_json(path, raw_build_log)
        
        exit_code = build_info["stderr"].split(":")[-1].strip()
        
        if exit_code.isdigit():
            unique_exit_codes.append(exit_code)
    
    count_each_exit_code = pd.Series(unique_exit_codes).value_counts()
    print(count_each_exit_code)

    

def test_basic_prompt():
    ERROR_LINE = "RUN apt-get -y update"
    ERROR_SEGMENT = """
    ** ERROR_SEGMENT **: 
> [2/6] RUN apt-get -y update:
Err:8 http://security.debian.org/debian-security stretch/updates/main amd64 Packages
Err:10 http://deb.debian.org/debian stretch/main amd64 Packages
  404  Not Found
Err:12 http://deb.debian.org/debian stretch-updates/main amd64 Packages
  404  Not Found
Reading package lists...
W: The repository 'http://security.debian.org/debian-security stretch/updates Release' does not have a Release file.
W: The repository 'http://deb.debian.org/debian stretch Release' does not have a Release file.
W: The repository 'http://deb.debian.org/debian stretch-updates Release' does not have a Release file.
E: Failed to fetch http://security.debian.org/debian-security/dists/stretch/updates/main/binary-amd64/Packages  404  Not Found
E: Failed to fetch http://deb.debian.org/debian/dists/stretch/main/binary-amd64/Packages  404  Not Found
E: Failed to fetch http://deb.debian.org/debian/dists/stretch-updates/main/binary-amd64/Packages  404  Not Found
E: Some index files failed to download. They have been ignored, or old ones used instead.
ERROR: process "/bin/sh -c apt-get -y update" did not complete successfully: exit code: 100
    """

    with get_openai_callback() as cb:
        res = gpt_api_calls.prompt_chat_gpt_for_error_summarization(error_line = ERROR_LINE,
            error_message=ERROR_SEGMENT)

        print(f"response from chat_gpt_plain: {res}")
        print("............................................")
        print("An example of token usage:")
        print(cb)
    return res



if __name__ == '__main__':
    calc_stats()
    test_basic_prompt()
    # fetch_unique_exit_codes()
