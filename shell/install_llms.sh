#!/usr/bin/env bash

# Pull all language models
for model in phi qwen2 mistral-nemo gemma mistral llama3; do 
    /usr/local/bin/ollama pull $model; 
done