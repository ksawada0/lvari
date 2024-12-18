import os
import json
import random

def read_input_file(path):
    with open(path) as f:
        return [x.strip() for x in f.read().split('\n')]
    
    
def write_result_to_file(dict_result, filename='data', ):
    out_dir = os.path.abspath(filename)
    os.makedirs(out_dir, exist_ok=True)  # Create the directory if it doesn't exist

    out_path = os.path.join(out_dir, 'result.txt')  # Create the full path
    with open(out_path, 'w+') as f:
        f.write(json.dumps(dict_result))
        
        
# Function to read the file and return lines as a list of lists
def read_file_and_shuffle_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        lines_as_lists = [line.strip().split() for line in lines]

        # Shuffle the list of lines
        random.shuffle(lines_as_lists)
        return lines_as_lists

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
        
    