
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

# Usage

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


