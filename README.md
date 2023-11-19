
# What is LLM_json_schema?

LLM_json_schema can enforce the output of an LLM model to follow a given json schema. The following types are available: string, number, boolean, array, object.

The output is guaranteed to have the correct format.

# Example

```bash
python3 LLM_json_schema.py --model models/Mistral-7B-Instruct-v0.1.gguf --json-schema '{"type":"object", "properties":{"country":{"type":"string"}, "capital":{"type":"string"}}}' --prompt "What is the capital of France?\n\n"
```

output:
```json
{"country":"France", "capital":"Paris"}
```

# How does it work?

It adds biases to the logits outputted by the LLM to enforce that only valid tokens can be chosen.

# Installation

## Install LLM_json_schema

```bash
cd LLM_json_schema
pip3 install -r requirements.txt
```

## Download an convert an LLM model

Download an LLM model, and convert it to the gguf format.

Example:
```bash
mkdir models
cd models
git clone https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
git clone https://github.com/ggerganov/llama.cpp.git
pip install -r llama.cpp/requirements.txt
python3 llama.cpp/convert.py Mistral-7B-Instruct-v0.1 \
  --outfile Mistral-7B-Instruct-v0.1.gguf \
  --outtype q8_0
cd ..
```

# Usage from CLI

```
usage: LLM_json_schema.py [-h] --model-path MODEL_PATH --prompt PROMPT [--json-schema JSON_SCHEMA]

options:
  -h, --help            show this help message and exit
  --model-path MODEL_PATH
                        Path to the LLM model in gguf format
  --prompt PROMPT       Input prompt
  --json-schema JSON_SCHEMA
                        JSON schema to enforce
```

```bash
python3 LLM_json_schema.py --model models/Mistral-7B-Instruct-v0.1.gguf --json-schema '{"type":"object", "properties":{"country":{"type":"string"}, "captial":{"type":"string"}}}' --prompt "What is the capital of France?\n\n"
```

# Usage from Python

```python
from LLM_json_schema import run_inference_constrained_by_json_schema
import os
script_path = os.path.dirname(os.path.realpath(__file__))
model_path=os.environ.get('MODEL_PATH', os.path.join(script_path, "./models/Mistral-7B-Instruct-v0.1.gguf"))
prompt = "\n\n### Instruction:\nWhat is the capital of France?\n\n### Response:\n"
json_schema = {"type":"object", "properties":{"country":{"type":"string"}, "capital":{"type":"string"}}}
for chunk in run_inference_constrained_by_json_schema(model_path=model_path, json_schema=json_schema, prompt=prompt):
    print(chunk, end="", flush=True)
print("")
```

# Citation

If you use this work please cite the following:

```
@article{author2022title,
  title={LLM Json Schema},
  author={Olivier Duchenne},
  journal={Github},
  url={https://github.com/olivierDuchenne/LLM_json_schema},
  year={2023}
}
```

