from mpi4py import MPI
import time
import argparse
import os
import sys
import csv
import chrono_modules.ollama_helper as ollama_helper
import resources.chrono_logging as chrono_logging
import resources.common as cmn
from threading import Lock


log = chrono_logging.get_logger("main", json=False)

# Constants
DEFAULT_ROLE = "Generalist"
IS_MEASURE_QUERY_RESPONSE_TIME = True
input_file_path = os.path.abspath('data/prompts.txt')
DEFAULT_ROLE = "Generalist"
IS_MEASURE_QUERY_RESPONSE_TIME = False
IS_LOG_RESPONSE = False
IS_WRITE_QUERY_RESPONSE_TIME_TO_FILE = False
IS_WRITE_AGREEMENT_PERCENTAGE_TO_FILE = False
file_write_lock = None
output_file_path = None
agreement_output_file_path = None

# Configuration for verbose levels
VERBOSE_CONFIG = {
    0: {"IS_MEASURE_QUERY_RESPONSE_TIME": False, 
        "IS_LOG_RESPONSE": False, 
        "IS_WRITE_QUERY_RESPONSE_TIME_TO_FILE": False,
        "IS_WRITE_AGREEMENT_PERCENTAGE_TO_FILE": False
        },
    1: {"IS_MEASURE_QUERY_RESPONSE_TIME": True, 
        "IS_LOG_RESPONSE": False, 
        "IS_WRITE_QUERY_RESPONSE_TIME_TO_FILE": True,
        "IS_WRITE_AGREEMENT_PERCENTAGE_TO_FILE": True
        },
    2: {"IS_MEASURE_QUERY_RESPONSE_TIME": True, 
        "IS_LOG_RESPONSE": True, 
        "IS_WRITE_QUERY_RESPONSE_TIME_TO_FILE": True,
        "IS_WRITE_AGREEMENT_PERCENTAGE_TO_FILE": True
        },
}


def set_verbose_level(level):
    """Sets the verbose level and updates configuration flags."""
    global file_write_lock, output_file_path, agreement_output_file_path
    config = VERBOSE_CONFIG.get(level, VERBOSE_CONFIG[0])  # Default to level 0 if the level is not recognized
    globals().update(config)
    if level > 0:
        # Thread-safe lock for file writing
        file_write_lock = Lock()
        output_file_path = 'tasks_log.csv'  # Path to the CSV file
        agreement_output_file_path = 'agreement_percentage.csv'



def parse_arguments():
    """
    Parses command-line arguments with default values.

    Returns:
        argparse.Namespace: Parsed arguments object.
    """
    parser = argparse.ArgumentParser(description="A script with optional verbose mode.")
    parser.add_argument('-v', '--verbose', type=int, default=1, help="Enable verbose mode (default: 1). 0: Minimum logging plus LLM response latency. 1: Write each LLM-Role's decision and justification to a file 2: Log both LLM latency and LLM's responses (decision and justification)")
    parser.add_argument('-m', '--num_models', type=int, default=3, help="Number of models to use")
    parser.add_argument('-r', '--num_roles', type=int, default=2, help="Number of roles to use")
    
    return parser.parse_args()


def write_to_csv(file_path, data):
    """Thread-safe function to write a row to a CSV file."""
    with file_write_lock:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)


def process_task(task, rank=-1):
    """Process a single task and return results with prompt_id."""
    prompt_id, model, prompt, role, server, original_prompt = task
    start_time = time.time()
    
    # Dynamically generate the prompt for Layer 3
    # prompt = ollama_helper.generate_prompt(prompt, role=role)

    # Query LLM
    response = ollama_helper.query_ollama(model, prompt, server_base_url=server)
    end_time = time.time()
    
    if IS_MEASURE_QUERY_RESPONSE_TIME:
        print(f"[rank={rank}] Task: {model}-{role or 'Generalist'} | Time: {end_time - start_time:.2f} seconds")
        
        # Write logs to a file
        if IS_WRITE_QUERY_RESPONSE_TIME_TO_FILE:
            log_entry = [model, role or 'Generalist', f"{end_time - start_time:.2f}"]
            write_to_csv(output_file_path, log_entry)

    try:
        if response:
            result = ollama_helper.process_response(response)
            agree = 1 if result.decision == "TRUE" else 0
            decision = 1
            
            # Log each of the LLM's decision and justification
            if IS_LOG_RESPONSE:
                log.info(f"Role: {role}")
                log.info(f"Prompt: {original_prompt}")
                log.info(f"Decision: {result.decision}")
                log.info(f"Justification: {result.justification}")
                
    except Exception as e:
        agree = 0
        decision = 0
        print(f"Error processing task {task}: {e}")

    return prompt_id, agree, decision, original_prompt


def distribute_tasks(prompts, models, roles):
    """Generate tasks with prompt_id for distribution."""
    tasks = []
    for prompt_id, prompt in enumerate(prompts):
        for model in models:
            for role in roles:
                server = cmn.LI_BASE_URL_LOCAL[0] if (prompt_id%2 == 0) else cmn.LI_BASE_URL_LOCAL[1]

                tasks.append((prompt_id, model, ollama_helper.generate_prompt(prompt, role), role, server, prompt))

    # for task in tasks:
    #     log.info(f"rank: {task[0]}")
    #     log.info(f"prompt_id: {task[0]}")
    #     log.info(f"model: {task[1]}")
    #     log.info(f"prompt: {task[2]}")
    #     log.info(f"role: {task[3]}")
    #     log.info(f"server: {task[3]}")
        
    return tasks


def main():
    # MPI Initialization
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    argv = parse_arguments()
    set_verbose_level(argv.verbose)
    
    # Load prompts and define models and roles
    if rank == 0:

        with open(input_file_path) as f:
            prompts = [x.strip() for x in f.read().split('\n') if x.strip()]
            
        models = cmn.get_models(argv.num_models)
        roles = cmn.get_roles(argv.num_roles)
        
        print(f'Number of Processes: {size}')
        print(f'Number of Models: {len(models)}')
        print(f'Number of Roles: {len(roles)}')
        print(f'Number of Inputs Verified: {len(prompts)}')
        
        tasks = distribute_tasks(prompts, models, roles)

        # Divide tasks into chunks for processes
        chunk_size = len(tasks) // size
        chunks = [tasks[i * chunk_size:(i + 1) * chunk_size] for i in range(size)]

        # Handle any remaining tasks
        for i in range(len(tasks) % size):
            chunks[i].append(tasks[chunk_size * size + i])
    else:
        prompts = None
        tasks = None
        models = None
        roles = None
        chunks = None

    # Broadcast models and roles
    models = comm.bcast(models, root=0)
    roles = comm.bcast(roles, root=0)

    # Scatter tasks among processes
    local_tasks = comm.scatter(chunks, root=0)   

    # Process local tasks
    local_results = []
    for task in local_tasks:
        # log.info(f"Rank {rank}: Received tasks: {len(local_tasks)}")
        local_result = process_task(task, rank)
        local_results.append(local_result)
        # local_results.append(process_task(task, rank))
        

    # Gather results at root
    all_results = comm.gather(local_results, root=0)

    # Root process aggregates results
    if rank == 0:
        # Aggregate by prompt_id
        aggregated_results = {}
        for process_results in all_results:
            for prompt_id, agree, decision, original_prompt in process_results:
                if prompt_id not in aggregated_results:
                    aggregated_results[prompt_id] = {"prompt": original_prompt, "agree": 0, "decision": 0}
                aggregated_results[prompt_id]["agree"] += agree
                aggregated_results[prompt_id]["decision"] += decision
                aggregated_results[prompt_id]["prompt"] += original_prompt
        
        li_agree_percentage = []
        # Log results per prompt
        for prompt_id, counts in aggregated_results.items():
            agree = counts["agree"]
            decision = counts["decision"]
            prompt = counts["prompt"]
            score = agree / decision if decision > 0 else 0
            print("----------------------")
            print(f"Prompt ID: {prompt_id}")
            print(f"Prompt: {prompt.split('.')[0]}")
            print(f"Total Agreements: {agree}")
            print(f"Total Decisions: {decision}")
            print(f"Agreement Percentage: {score * 100:.2f}%")
            print("----------------------")
            
            li_agree_percentage.append(score)
        
            # Write logs to a file
            if IS_WRITE_AGREEMENT_PERCENTAGE_TO_FILE:
                scores_for_csv = [len(models), len(roles), f"{score:.4f}", len(prompts)]
                write_to_csv(agreement_output_file_path, scores_for_csv)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f'Elapsed Time = {elapsed_time:.1f} min.')
