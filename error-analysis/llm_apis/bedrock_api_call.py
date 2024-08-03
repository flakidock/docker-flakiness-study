import json
import boto3
import logging
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)

def init_bedrock():
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )
    return bedrock_runtime


def invoke_claude(prompt, bedrock_runtime):
    """
    Invokes the Anthropic Claude 3 model to run an inference using the input
    provided in the request body.

    :param prompt: The prompt that you want Claude to complete.
    :return: Inference response from the model.
    """

    try:
        # The different model providers have individual request and response formats.
        # For the format, ranges, and default values for Anthropic Claude, refer to:
        # https://docs.anthropic.com/claude/reference/complete_post

        # Claude requires you to enclose the prompt as follows:
        enclosed_prompt = "Human: " + prompt + "\n\nAssistant:"

        body = {
            "messages": [{"role": "user", "content": enclosed_prompt}],
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 256,
            "temperature": 0.0,
            "stop_sequences": ["\n\nHuman:"],

        }

        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0", body=json.dumps(body)
        )

        response_body = json.loads(response.get("body").read())
        content = response_body.get("content")[0]['text']

        return content

    except ClientError:
        logger.error("Couldn't invoke Anthropic Claude")
        raise

def invoke_claude_vision(prompt, bedrock_runtime, base64_image):
    """
    Invokes the Anthropic Claude 3 model to run an inference using the input
    provided in the request body.

    :param prompt: The prompt that you want Claude to complete.
    :return: Inference response from the model.
    """

    try:
        # The different model providers have individual request and response formats.
        # For the format, ranges, and default values for Anthropic Claude, refer to:
        # https://docs.anthropic.com/claude/reference/complete_post


        body = {
            "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image
                    }
                },
            ],
        }],
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.0,
            "system": prompt

        }

        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0", body=json.dumps(body)
        )

        response_body = json.loads(response.get("body").read())
        content = response_body.get("content")[0]['text']

        return content

    except ClientError:
        logger.error("Couldn't invoke Anthropic Claude")
        raise
    
def invoke_llama3(prompt, bedrock_runtime, model_id="meta.llama3-8b-instruct-v1:0"):
    """
    Invokes the Anthropic Llama 3 model to run an inference using the input
    provided in the request body.

    :param prompt: The prompt that you want Llama to complete.
    :return: Inference response from the model.
    """

    try:

        # Embed the message in Llama 3's prompt format.
        formatted_prompt = f"""
        <|begin_of_text|>
        <|start_header_id|>user<|end_header_id|>
        {prompt}
        <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """

        # Format the request payload using the model's native structure.
        request = {
            "prompt": formatted_prompt,
            # Optional inference parameters:
            "max_gen_len": 2048,
            "temperature": 0.0,
            "top_p": 0.9,
        }

        # Encode and send the request.
        response = bedrock_runtime.invoke_model(body=json.dumps(request), modelId=model_id)

        # Decode the native response body.
        model_response = json.loads(response["body"].read())

        # Extract and print the generated text.
        response_text = model_response["generation"]
        
        return response_text
        
    except Exception as e:
        logger.error("Couldn't invoke Llama 3")
        raise
    
def invoke_titan_embedding(prompt, bedrock_runtime):
     
    try:
        body = json.dumps({
            "inputText": prompt,
        })
        
    
        model_id = 'amazon.titan-embed-text-v1' #look for embeddings in the modelID
        # model_id = 'amazon.titan-embed-text-v2:0' # we don't have access to this model

        accept = 'application/json' 
        content_type = 'application/json'
    
        # Invoke model 
        response = bedrock_runtime.invoke_model(
            body=body, 
            modelId=model_id, 
            accept=accept, 
            contentType=content_type
        )
        
        # Print response
        response_body = json.loads(response['body'].read())
        embedding = response_body.get('embedding')
        
        return embedding
    
    except ClientError:
        logger.error("Couldn't invoke Anthropic Claude")
        raise
    
def invoke_mistral_7b(prompt, bedrock_runtime):
    """
    Invokes the Mistral 7B model to run an inference using the input
    provided in the request body.

    :param prompt: The prompt that you want Mistral to complete.
    :return: List of inference responses from the model.
    """

    try:
        # Mistral instruct models provide optimal results when
        # embedding the prompt into the following template:
        instruction = f"<s>[INST] {prompt} [/INST]"

        model_id = "mistral.mistral-7b-instruct-v0:2"

        body = {
            "prompt": instruction,
            "max_tokens": 512,
            "temperature": 0.0,
        }

        response = bedrock_runtime.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )

        response_body = json.loads(response["body"].read())
        outputs = response_body.get("outputs")

        completions = [output["text"] for output in outputs]

        return completions[0].strip()

    except ClientError:
        logger.error("Couldn't invoke Mistral 7B")
        raise

    