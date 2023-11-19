import os
from llama_cpp_wrapper.python_llama_cpp.inference_with_completion import do_inference
from constrainer import JsonSchemaConstrainer
import argparse
import json
from jsonschema import Draft7Validator


def main(model_path: str, json_schema: dict, prompt: str):
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
            byte_completions = [c.encode() for c in completions]
        return byte_completions
    byte_prompt = prompt.encode()
    do_inference(prompt=byte_prompt, model_path=model_path, completion_callback=do_completion)


def cli():
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
    
    main(model_path, json_schema, prompt)


if __name__ == "__main__":
    cli()
