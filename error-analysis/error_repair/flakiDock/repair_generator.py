from llm_apis import gpt_api_calls, bedrock_api_call
from utils.string_utils import truncate_string, num_gpt_tokens_in_a_string
from error_repair.system_templates import SYSTEM_REPAIR_TEMPLATE_WITH_BUILD_OUTPUT_AND_SIMILARITY_AND_FEEDBACK, SYSTEM_REPAIR_TEMPLATE_WITH_BUILD_OUTPUT, SYSTEM_REPAIR_TEMPLATE
from error_repair.user_templates import user_repair_template_with_build_output_and_similar_shots_and_feedback, user_repair_template_with_build_info, user_repair_template

REMOVE_LINES = ["<<<<<", ">>>>>"]

def get_input_prompts(prompt_type: str, dockerfile: str, build_output: str, shots: list, feedbacks: list):
    """
    get the input prompts based on the prompt type
    """
    
    system_prompt = ""
    user_prompt = ""
    # TODO: improvements needed: 
    #   encapsulate dockerfiles and build outputs inside ```.
    #   maybe for repair use modification files for better demonstration.
    if prompt_type == "S":
        system_prompt = SYSTEM_REPAIR_TEMPLATE
        user_prompt = user_repair_template(dockerfile=dockerfile)
    if prompt_type == "SD":
        system_prompt = SYSTEM_REPAIR_TEMPLATE_WITH_BUILD_OUTPUT
        user_prompt = user_repair_template_with_build_info(dockerfile=dockerfile, build_error=build_output)
    
    if prompt_type == "Dockerfile_and_build_output":
        system_prompt = SYSTEM_REPAIR_TEMPLATE_WITH_BUILD_OUTPUT_AND_SIMILARITY_AND_FEEDBACK
        user_prompt = user_repair_template_with_build_output_and_similar_shots_and_feedback(dockerfile=dockerfile, build_error=build_output, shots=shots, feedbacks=feedbacks)
    
    return system_prompt, user_prompt


def clean_response(response: str, original_dockerfile) -> str:
    """
    clean the response from the LLM. the Dockerfile is within five angle brackets. so, need to remove those.
    """
    for line in REMOVE_LINES:
        response = response.replace(line, "")
    return response.strip()
    


def generate_repaired_dockerfile(project_path, dockerfile, build_output, similar_records, feedbacks, model_under_test, round, output_folder, dockerfile_name, model="gpt4"):
    
    prompt_type = "Dockerfile_and_build_output"
    openai_runtime = gpt_api_calls.init_openai(model_under_test)
    bedrock_runtime = bedrock_api_call.init_bedrock()
    
    system_prompt, user_prompt = get_input_prompts(prompt_type=prompt_type, dockerfile=dockerfile, build_output=build_output, shots=similar_records, feedbacks=feedbacks)
    
    # store the user prompt:
    with open(f"{output_folder}/v{round}_user_prompt.txt", "w") as f:
        f.write(user_prompt)

    llm_response = ""
    if model == "gpt4":
        llm_response = gpt_api_calls.invoke_model(
            chat=openai_runtime,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            model_name=model_under_test
        )
        
    elif model == "llama3":
        # format_assurance_message = "VERY IMPORTANT: the output should have no description. It should be only <<<<< Dockerfile >>>>> and nothing else. Just the Dockerfile content."
        llm_response = bedrock_api_call.invoke_llama3(
            prompt=user_prompt + "\n\n" + system_prompt,
            bedrock_runtime=bedrock_runtime,
            model_id=model_under_test
        )
    
    dockerfile_content = clean_response(llm_response, dockerfile)
    with open(f"{output_folder}/{dockerfile_name}", "w") as f:
        f.write(dockerfile_content)
        
    # store the repaired Dockerfile inside the project directory
    with open(f"{project_path}/{dockerfile_name}", "w") as f:
        f.write(dockerfile_content)
        
    return dockerfile_content
     
      
def generate_repaired_dockerfile_SD(project_path, dockerfile, build_output, model_under_test, round, output_folder, dockerfile_name, model="gpt4"):
    
    prompt_type = "SD" # only static (Dockerfile) and dynamic (build output) information
    openai_runtime = gpt_api_calls.init_openai(model_under_test)
    bedrock_runtime = bedrock_api_call.init_bedrock()
    
    system_prompt, user_prompt = get_input_prompts(prompt_type=prompt_type, dockerfile=dockerfile, build_output=build_output, shots=[], feedbacks=[])
    
    # store the user prompt:
    with open(f"{output_folder}/v{round}_user_prompt.txt", "w") as f:
        f.write(user_prompt)

    if model == "gpt4":
        llm_response = gpt_api_calls.invoke_model(
            chat=openai_runtime,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            model_name=model_under_test
        )
        
    elif model == "llama3":
        llm_response = bedrock_api_call.invoke_llama3(
            prompt=user_prompt + "\n\n" + system_prompt,
            bedrock_runtime=bedrock_runtime,
            model_id=model_under_test
        )
    
    dockerfile_content = clean_response(llm_response, dockerfile)
    with open(f"{output_folder}/{dockerfile_name}", "w") as f:
        f.write(dockerfile_content)
        
    # store the repaired Dockerfile inside the project directory
    with open(f"{project_path}/{dockerfile_name}", "w") as f:
        f.write(dockerfile_content)
        
    return dockerfile_content 


def generate_repaired_dockerfile_S(project_path, dockerfile, model_under_test, round, output_folder, dockerfile_name, model="gpt4"):
    
    prompt_type = "S" # only static (Dockerfile) and dynamic (build output) information
    openai_runtime = gpt_api_calls.init_openai(model_under_test)
    bedrock_runtime = bedrock_api_call.init_bedrock()
    
    system_prompt, user_prompt = get_input_prompts(prompt_type=prompt_type, dockerfile=dockerfile, build_output="", shots=[], feedbacks=[])
    
    # store the user prompt:
    with open(f"{output_folder}/v{round}_user_prompt.txt", "w") as f:
        f.write(user_prompt)
    
    if model == "gpt4":
        llm_response = gpt_api_calls.invoke_model(
            chat=openai_runtime,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            model_name=model_under_test
        )
        
    elif model == "llama3":
        llm_response = bedrock_api_call.invoke_llama3(
            prompt=user_prompt + "\n\n" + system_prompt,
            bedrock_runtime=bedrock_runtime,
            model_id=model_under_test
        )
    
    dockerfile_content = clean_response(llm_response, dockerfile)
    with open(f"{output_folder}/{dockerfile_name}", "w") as f:
        f.write(dockerfile_content)
        
    # store the repaired Dockerfile inside the project directory
    with open(f"{project_path}/{dockerfile_name}", "w") as f:
        f.write(dockerfile_content)
        
    return dockerfile_content 