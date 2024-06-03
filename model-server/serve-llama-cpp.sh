#!/bin/bash

cd ~/services/llama.cpp
# ./build/bin/server --model ../gguf/Meta-Llama-3-70B-Q4_K_M.gguf --n-gpu-layers 100 
./build/bin/server --model ../gguf/Cat-Llama-3-70B-instruct-Q4_K_S.gguf --n-gpu-layers 100 
