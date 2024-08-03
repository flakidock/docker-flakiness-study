import re
import tiktoken
from utils.class_utils import DockerErrorTrace


def split_string_with_delimiters(text, delimiters):
    pattern = '|'.join(map(re.escape, delimiters))

    parts = re.split(pattern, text)
    parts = [part.strip() for part in parts]
    return parts


def string_contains_keys(string, key_list):
    for key in key_list:
        if key in string:
            return key
    return False


def remove_pattern_from_string(patterns, string):
    result = string
    for pattern in patterns:
        result = re.sub(pattern, '', result)
    return result


def num_gpt_tokens_in_a_string(string: str, encoding_name: str = 'gpt2') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_string(string: str, max_tokens: int, encoding_name: str = 'gpt2') -> str:
    """Truncates a string to a maximum number of tokens."""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(string)
    if len(tokens) <= max_tokens:
        return string
    # print("large string!")
    truncated_tokens = tokens[-max_tokens:]
    truncated_string = encoding.decode(truncated_tokens)
    return truncated_string


def parse_unique_error_files(error_string: str, total_tokens: int = 4096,
                             prompt_tokens: int = 1213) -> DockerErrorTrace:
    """
    Parses an error string and returns a JSON object.

    Parameters:
    error_string (str): The error string to parse.
    total_tokens (int): The total number of tokens to use.
    prompt_tokens (int): The number of tokens used so far. Default is 1213: 
        system_prompt_template_tokens=840
        user_prompt_template_tokens=117
        completion_prompt_template_tokens=256

    Returns:
    DockerErrorTrace: A DockerErrorTrace object.
    """

    # Split the string into segments based on "**"
    segments = split_unique_build_files(error_string)
    error_segment, error_line, stderr_line, dockerfile_segment, exit_code = segments.values()

    error_segment_tokens = num_gpt_tokens_in_a_string(error_segment, 'gpt2')
    error_line_tokens = num_gpt_tokens_in_a_string(error_line, 'gpt2')
    dockerfile_segment_tokens = num_gpt_tokens_in_a_string(dockerfile_segment, 'gpt2')
    exit_code_tokens = num_gpt_tokens_in_a_string(exit_code, 'gpt2')

    error_total_tokens = error_segment_tokens + error_line_tokens + dockerfile_segment_tokens

    if (prompt_tokens + error_total_tokens) > total_tokens:
        budget = total_tokens - prompt_tokens
        tokenizer = tiktoken.get_encoding('gpt2')

        if error_segment_tokens > budget:
            tokens = tokenizer.encode(error_segment)
            tokens = tokens[-budget:]
            error_segment = tokenizer.decode(tokens)
            error_line = ""
            dockerfile_segment = ""

        # too long error line, focus on the error segment
        elif error_line_tokens > 2500 or dockerfile_segment_tokens > budget:
            error_line = ""
            dockerfile_segment = ""

        elif (error_segment_tokens + error_line_tokens) > budget:
            budget = budget - error_line_tokens

            tokens = tokenizer.encode(error_line)
            tokens = tokens[-budget:]
            error_line = tokenizer.decode(tokens)
            dockerfile_segment = ""

        elif (error_segment_tokens + error_line_tokens + dockerfile_segment_tokens) > budget:
            budget = budget - error_segment_tokens - error_line_tokens

            tokens = tokenizer.encode(dockerfile_segment)
            tokens = tokens[-budget:]
            dockerfile_segment = tokenizer.decode(tokens)

    return DockerErrorTrace(error_segment=error_segment.strip(),
                            error_line=error_line.strip(),
                            dockerfile_segment=dockerfile_segment.strip(),
                            exit_code=exit_code.strip())


def split_unique_build_files(build_content: str):
    segments = build_content.split("** DOCKERFILE_ERROR_LINE **:")

    error_segment = segments[0].replace("** ERROR_SEGMENT **:", "")
    error_line = segments[1].split("** STDERR **: ")[0].strip().replace("** DOCKERFILE_ERROR_LINE **:", "")
    stderr_line = segments[1].split("** STDERR **: ")[1].strip().split("** DOCKERFILE_ERROR_SEGMENT **: ")[0].replace(
        "** STDERR **: ", "")
    dockerfile_segment = build_content.split("** DOCKERFILE_ERROR_SEGMENT **: ")[1]

    if (len(error_segment.strip()) == 0):
        error_segment = stderr_line

    # extract the exit code from the stderr line: after the last colon
    exit_code = stderr_line.split(":")[-1].strip()
    exit_code = exit_code if len(exit_code) < 50 else ""

    return {
        "error_segment": error_segment.strip(),
        "error_line": error_line.strip(),
        "stderr_line": stderr_line.strip(),
        "dockerfile_segment": dockerfile_segment.strip(),
        "exit_code": exit_code.strip()
    }


def count_equivalent_pairs(list1, list2):
    equivalent_count = sum(1 for s1 in list1 for s2 in list2 if s1 == s2 or s2.startswith(s1))
    not_equivalent_count1 = len(list1) - equivalent_count # detected - actual: those that are detected: flaky but the actual label is non-flaky
    not_equivalent_count2 = len(list2) - equivalent_count
    return equivalent_count, not_equivalent_count1, not_equivalent_count2


def find_substring_index(substring, string_list):
    for index, item in enumerate(string_list):
        if substring in item:
            return index
    return -1  # Return -1 if no substring is found