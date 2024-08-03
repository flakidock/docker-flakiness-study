def generate_summarization_user_prompt(error_line: str, error_message: str, dockerfile: str, exit_code: str):
    
    user_prompt = ""
    if dockerfile:
        user_prompt += f"""
# DOCKERFILE:
```
{dockerfile}
```
"""
    
    user_prompt += f"""
# DOCKERFILE_ERROR_LINE:
```
{error_line}
```
            
# ERROR_MESSAGE:
'''
{error_message}
'''
"""

    if exit_code:
        user_prompt += f""" 
# EXIT_CODE:
'''
{exit_code}
'''
"""

    user_prompt += """
Parse this docker build error in the specified format. Don't explain your process, just give the JSON output. Make sure your output can be parsed by json.loads.
"""

    return user_prompt


def generate_error_detection_user_prompt(dockerfile: str):
    
    
    user_prompt = f"""

Detect if the following dockerfile is flaky, and if so, provide the flakiness category and error line. Otherwise, provide the category label and error line as "":

# DOCKERFILE:
```
{dockerfile}
```

Don't explain your process, just give the requested json format result.
"""

    return user_prompt

def generate_error_repair_user_prompt(dockerfile, build_error, flakiness_category):
    user_prompt = f"""
    
Repair the flaky dockerfile based on the dockerfile context, the build error, and the flakiness category:

# DOCKERFILE:
```
{dockerfile}
```

# BUILD_ERROR:
'''
{build_error}
'''

# FLAKINESS_CATEGORY
'''
{flakiness_category}
'''

Don't explain your process, just give the output result in required format.
"""

    return user_prompt