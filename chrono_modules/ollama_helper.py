#!/usr/bin/env python

import time
import json
import requests
from classes.DecisionResult import DecisionResult
import resources.chrono_logging as chrono_logging
import resources.common as cmn

log = chrono_logging.get_logger("main", json=False)

def query_ollama(model_name, prompt, server_base_url='http://127.0.0.1:11434'):
    """Queries the Ollama server."""
    max_retries = 5
    full_response = None
    
    for i in range(max_retries + 1):
        response = requests.post(
            f"{server_base_url}/api/generate",  
            json={"model": model_name, "prompt": prompt, "temperature": 0.2},
            stream=True,
        )
        
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line.decode("utf-8"))
                    full_response += json_response.get("response", "")
            break
        
        log.info(f"No response was received from {model_name} [i={i}]")
        
    if not full_response:
        log.info(f"Failed to get a response from {model_name} after {max_retries} retries.]")

    return full_response
    
    
def generate_prompt(original_prompt, role="Generalist"):
    """Construct the prompt based on the layer, role, and agreement count."""
    base_prompt = (
        f"Is this statement true? '{original_prompt}' Please generate your response in the following format: First answer either TRUE or FALSE, followed by a period. Then, state the reason for my decision is [your reason]' Please limit your response to a maximum of {cmn.MAX_PROMPT_LENGTH} bytes. Ensure your response fits within this limit."
    )
    return f"{base_prompt} Respond as an expert {role}."
    


def process_response(response):
    """Process LLM response."""
    decision = "TRUE" if "true" in response.lower() else "FALSE"
    return DecisionResult(decision, response)

