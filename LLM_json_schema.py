import os
from llama_cpp_wrapper.python_llama_cpp.inference_with_completion import do_inference
from constrainers import JsonSchemaConstrainer, end_token
import argparse
import json
from jsonschema import Draft7Validator


def run_inference_constrained_by_json_schema(model_path: str, json_schema: dict, prompt: str):
    """
    This function runs inference on a given model, constrained by a JSON schema.

    Parameters:
    model_path (str): The path to the LLM model in gguf format.
    json_schema (dict): The JSON schema to enforce.
    prompt (str): The input prompt.

    Yields:
    str: The generated text that follows the constraints of the JSON schema.
    """
    json_schema_completer = None
    if json_schema:
        json_schema_completer = JsonSchemaConstrainer(json_schema)
    def do_completion(history: str):
        first_index = history.find(prompt)
        bot_history = history[first_index+len(prompt):]
        completions = None
        if json_schema_completer:
            completions = json_schema_completer.compute_completion(bot_history)
        # print(f"""[completions:{completions}]""")
        byte_completions = completions
        if isinstance(completions, list):
            byte_completions = [c.encode() if type(c) is str else c for c in completions]
        return byte_completions
    byte_prompt = prompt.encode()
    for chunk in do_inference(prompt=byte_prompt, model_path=model_path, completion_callback=do_completion, verbose=False):
        if end_token in chunk:
            yield chunk.replace(end_token, "")
            return
        yield chunk

def cli():
    """
    Command Line Interface for running inference constrained by a JSON schema.

    This function parses command line arguments for model path, prompt, and JSON schema.
    It then validates the model path and JSON schema, and runs inference using the provided model and prompt, constrained by the JSON schema.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, required=True, help="Path to the LLM model in gguf format")
    parser.add_argument("--prompt", type=str, required=True, help="Input prompt")
    parser.add_argument("--json-schema", type=str, help="JSON schema to enforce")
    args = parser.parse_args()

    model_path = args.model_path
    string_json_schema = args.json_schema
    prompt = args.prompt

    if not os.path.exists(model_path):
        print("Error: The model path does not exist.")
        return
    if not model_path.endswith('.gguf'):
        print("Error: The model path does not have a .gguf extension.")
        return
    
    try:
        json_schema = json.loads(string_json_schema)
    except:
        print("Error: The JSON schema is not a valid json.")
        return

    try:
        Draft7Validator.check_schema(json_schema)
    except Exception as e:
        print(e)
        print("Error: The JSON schema is not a valid json schema.")        
        return
    
    for chunk in run_inference_constrained_by_json_schema(model_path, json_schema, prompt):
        print(chunk, end="", flush=True)
    print("", flush=True)


if __name__ == "__main__":
    # for chunk in run_inference_constrained_by_json_schema("models/Mistral-7B-Instruct-v0.1.gguf", {"type":"object", "properties":{"country":{"type":"string"}, "capital":{"type":"string"}}}, "What is the capital of France?\n\n"):
    #     print(chunk, end="", flush=True)
    # print("", flush=True)
    # for chunk in run_inference_constrained_by_json_schema("models/Mistral-7B-Instruct-v0.1.gguf", {"type":"array", "items":{"type":"number"}}, "Count until 20.\n\n"):
    #     print(chunk, end="", flush=True)
    # print("", flush=True)
    cli()
