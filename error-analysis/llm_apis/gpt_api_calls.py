import os
import openai
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import AIMessage

from langchain_openai import ChatOpenAI
from llm_apis import system_templates


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

def init_client():
    client = openai.OpenAI()
    return client

def init_openai(model_name: str):
    openai_runtime = ChatOpenAI(model_name=model_name, temperature=0.0)
    return openai_runtime

def invoke_model(chat, user_prompt: str, system_prompt: str, model_name: str):
    
    messages = [
        SystemMessage(
            content=system_prompt
        ),
        HumanMessage(
            content=user_prompt
        ),
    ]
    
    output: AIMessage = chat.invoke(messages)
    
    return output.content


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


def generate_error_detection_user_prompt(dockerfile: str, build_error: str):
    
    if build_error != "":
        user_prompt = f"""
    
Detect the flaky category for the following dockerfile and build error:

# DOCKERFILE:
```
{dockerfile}
```

# BUILD_ERROR:
'''
{build_error}
'''

Analyze the dockerfile and the build error as required. Don't explain your process, just give the category label.
"""

    else:
        user_prompt = f"""
        
Detect the flaky category for the following dockerfile:

# DOCKERFILE:
```
{dockerfile}
```

Analyze the dockerfile as required. Don't explain your process, just give the category label.
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

def prompt_chat_gpt_for_error_summarization(error_line: str,
                   error_message: str,
                   dockerfile: str = "",
                   exit_code: str = "",
                   chat_completion_fill_prompt_sys_template: str = system_templates.CHAT_COMPLETION_FILL_PROMPT_TEMPLATE_ERROR_LINE_ONLY,
                   max_tokens: int = 150):
    
    user_prompt = generate_summarization_user_prompt(error_line, error_message, dockerfile, exit_code)
    
    """
    temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.    
    """
    
    chat = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0, max_tokens=max_tokens)
    
    messages = [
        SystemMessage(
            content=chat_completion_fill_prompt_sys_template
        ),
        HumanMessage(
            content=user_prompt
        ),
    ]
    
    output: AIMessage = chat.invoke(messages)
    
    return output.content

def prompt_chat_gpt_for_initial_error_clustering(list_of_errors: str, 
                    chat_completion_fill_prompt_sys_template: str = system_templates.CLUSTER_ERRORS_WITH_INITIAL_LABELS):
    
    user_prompt = f"""
# LIST_OF_ERRORS:
'''
{list_of_errors}
'''

Cluster these errors with initial labels. Don't explain your process, just give the JSON output. Make sure your output can be parsed by json.loads.
"""

    chat = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0)
    
    messages = [
        SystemMessage(
            content=chat_completion_fill_prompt_sys_template
        ),
        HumanMessage(
            content=list_of_errors
        ),
    ]
    
    output: AIMessage = chat.invoke(messages)
    
    return output.content

def prompt_chat_gpt_for_generate_cluster_name(list_of_errors: str, 
                    chat_completion_fill_prompt_sys_template: str = system_templates.GENERATE_LABEL_FROM_SUBITEMS):
    
    user_prompt = f"""
# LIST_OF_ERRORS:
'''
{list_of_errors}
'''

Generate a label for the cluster based on the subitems in the list. Don't explain your process, just give the output string.
"""

    chat = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0)
    
    messages = [
        SystemMessage(
            content=chat_completion_fill_prompt_sys_template
        ),
        HumanMessage(
            content=list_of_errors
        ),
    ]
    
    output: AIMessage = chat.invoke(messages)
    
    return output.content


def detect_dockerfile_error_category(dockerfile: str, system_template: str, build_error: str = "", model_name: str = "gpt-3.5-turbo-0125"):
    
    user_prompt = generate_error_detection_user_prompt(dockerfile, build_error)
    
    """
    temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.    
    """
    
    chat = ChatOpenAI(model_name=model_name, temperature=0.0)
    
    messages = [
        SystemMessage(
            content=system_template
        ),
        HumanMessage(
            content=user_prompt
        ),
    ]
    
    output: AIMessage = chat.invoke(messages)
    
    return output.content

def repair_dockerfile_error(dockerfile: str, build_error: str, flakiness_category:str, system_template: str):
    
    user_prompt = generate_error_repair_user_prompt(dockerfile, build_error, flakiness_category)
    
    """
    temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.    
    """
    
    chat = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.0)
    
    messages = [
        SystemMessage(
            content=system_template
        ),
        HumanMessage(
            content=user_prompt
        ),
    ]
    
    output: AIMessage = chat.invoke(messages)
    
    return output.content