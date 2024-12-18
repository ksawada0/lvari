#!/usr/bin/env python
################################################################################
# Description:
#       This script maintains the constant variables and a class, used to execute
#       MDMS testing tasks
# ################################################################################

import datetime

##############################
# Ollama
##############################
BASE_URL_LOCAL = 'http://127.0.0.1:11434'
LI_BASE_URL_LOCAL = ['http://127.0.0.1:11434', 'http://127.0.0.1:11431']
# BASE_URL_LOCAL = 'http://0.0.0.0:11434'

# Dynamically fetch the Ollama server URL from the environment variable
# BASE_URL_LOCAL = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MAX_PROMPT_LENGTH = 3000


##############################
# Models and Roles
##############################
def get_models(n):
    if n == 1:
        return ["llama3"]
    elif n == 2:
        return ["llama3", "phi"]
    elif n == 3:
        return ["llama3", "phi", "gemma"]
    elif n == 4:
        return ["llama3", "phi", "gemma", "mistral"]
    elif n == 5:
        return ["phi", "llama3", "mistral-nemo", "gemma", "mistral"]
    else:
        return ["phi", "qwen2", "mistral-nemo", "gemma", "mistral", "llama3"]
    
def get_roles(n):
    if n == 1:
        # return  ["Philosophy Professor"]
        return  ["Generalist"]
    elif n == 2:
        # return  ["Engineer", "Philosophy Professor"]
        return  ["Generalist", "Engineer"]
    elif n == 3:
        # return  ["Engineer", "Philosophy Professor", "Mathematician"]
        return  ["Generalist", "Molecular Biologist", "Mathematician"]
    elif n == 4:
        # return  ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist"]
        return  ["Generalist", "Engineer", "Mathematician", "Molecular Biologist"]
    elif n == 5:
        return  ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist", "Physicist"]
    elif n == 6:
        return  ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist", "Physicist", "Molecular Biologist"]
    elif n == 7:
        return  ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist", "Physicist", "Molecular Biologist", "English Professor"]
    elif n == 8:
        return  ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist", "Physicist", "Molecular Biologist", "Occupational Therapist", "English Professor"]
    elif n == 9:
        return  ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist", "Physicist", "Social Worker", "Molecular Biologist", "Occupational Therapist", "English Professor"]
    else:
        return  ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist", "Physicist", "Astronomer", "Molecular Biologist", "Medical Doctor", "Social Worker", "Occupational Therapist", "English Professor"]

##############################
# Tokens
##############################
# Tokenizer mappings for each model (TODO: adjust sa needed)
MODEL_TOKENIZER_MAP = {
    "llama3": "gpt2",
    "phi": "gpt2",
    "gemma": "gpt2",
    "qwen2": "gpt2",
    "mistral-nemo": "gpt2",
    "mistral": "gpt2"
}

##############################
# Model Response Time Tracking
##############################
# def get_model_response_time_dict:
#     MODEL_RESPOSE_TIME = {}
#     for model in MODELS:
#         for role in ROLES:
#             MODEL_RESPOSE_TIME[f'{model}-{role}'] = -1
    # {'model 1':
    #     {'role 1': 'some role',
    #     'role 2': 'another role',
    #     },
    # 'model 1':
    #     {'role 1': 'some role',
    #     'role 2': 'another role',
    #     },
    # }


##############################
# Miscellaneous
##############################
TODAY = datetime.date.today()
YESTERDAY = TODAY - datetime.timedelta(days=1)
START_TIME = datetime.datetime.now()
