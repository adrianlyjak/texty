#!/bin/bash

cd "$(dirname "$0")"
source .venv/bin/activate
python -m vllm.entrypoints.openai.api_server \
  --model ./Meta-Llama-3-70B-Instruct-GPTQ-4b \
  --dtype auto \
  --tensor-parallel-size 2 \
  --enforce-eager \
  --max-model-len 2048 \
  --quantization gptq
