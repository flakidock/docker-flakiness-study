import json
import os
from time import sleep
from tqdm import tqdm
from langchain_community.callbacks import get_openai_callback
from llm_apis import gpt_api_calls
from llm_apis import system_templates
from utils.class_utils import DockerErrorTrace
from utils.file_utils import list_log_files
from utils.string_utils import parse_unique_error_files, num_gpt_tokens_in_a_string

from path_config import ROOT_PATH

def load_json(json_string):
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Couldn't decode json: {e}")
        print(f"Couldn't decode json string: {json_string}")
        data = {}  # or set to some default value
    return data

def get_prompt_tokens(system_prompt, user_prompt):
    system_prompt_template_tokens = num_gpt_tokens_in_a_string(system_prompt)
    user_prompt_template_tokens = num_gpt_tokens_in_a_string(user_prompt)
    
    # 512 tokens for: completion prompt + tokens reserved to ensure we don't exceed the token limit
    total_tokens = system_prompt_template_tokens + user_prompt_template_tokens + 512
    
    return total_tokens

def process_flaky_logs():
    # The directory to start from
    
    flaky_repo_dir = ROOT_PATH + '/possible-flaky-repos'
    
    prompt_tokens = get_prompt_tokens(system_templates.CHAT_COMPLETION_FILL_PROMPT_WITH_DOCKER_FILE_TEMPLATE, 
                                      system_templates.USER_PROMPT_WITH_FULL_DOCKERFILE)

    # Walk the directory
    project_counter = 0
    
    for root, dirs, files in tqdm(os.walk(flaky_repo_dir)):
        # Iterate over every file in the directory
        if 'unique-build-errors' in root:
            project_counter += 1

            for error_trace_log_file in list_log_files(root):
                
                # Construct the full file path
                file_path = os.path.join(root, error_trace_log_file)

                with open(file_path, 'r', errors='replace') as file:
                    file_name = file.name
                    raw_build_log = file.read()
                    
                    error_trace: DockerErrorTrace = parse_unique_error_files(raw_build_log, 16385, prompt_tokens)
                    
                    summary: str = gpt_api_calls.prompt_chat_gpt_for_error_summarization(
                        error_line = error_trace.error_line,
                        error_message=error_trace.error_segment,
                        dockerfile=error_trace.dockerfile_segment,
                        exit_code="",
                        chat_completion_fill_prompt_sys_template=system_templates.CHAT_COMPLETION_FILL_PROMPT_WITH_DOCKER_FILE_TEMPLATE
                    )
                    
                    summary_formatted = json.dumps(summary, indent=4)
                    
                    output_file_path = os.path.join(root, f"llm-summary-{error_trace_log_file}.json")
                    with open(output_file_path, 'w') as json_file:
                        json.dump(summary_formatted, json_file)
                        
                    # sleep in order to avoid potential rate limits
                    sleep(5)

                    print(f" processed file: {output_file_path}")
                    print("=========================================")
            



if __name__ == '__main__':
    with get_openai_callback() as cb:
        process_flaky_logs()
        print(cb)

