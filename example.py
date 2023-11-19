from LLM_json_schema import run_inference_constrained_by_json_schema
import os
script_path = os.path.dirname(os.path.realpath(__file__))
model_path=os.environ.get('MODEL_PATH', os.path.join(script_path, "./models/Mistral-7B-Instruct-v0.1.gguf"))
prompt = "\n\n### Instruction:\nWhat is the capital of France?\n\n### Response:\n"
json_schema = {"type":"object", "properties":{"country":{"type":"string"}, "capital":{"type":"string"}}}
for chunk in run_inference_constrained_by_json_schema(model_path=model_path, json_schema=json_schema, prompt=prompt):
    print(chunk, end="", flush=True)
print("")

