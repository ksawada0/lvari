#!/usr/bin/env bash

# Usage function to display help message
usage() {
    script_name=$(basename "$0")
    cat <<EOF
Usage: $script_name [NUM CORES]

Options:
  -p, --processes NUM        Number of MPI processes to use (default: 3)
  -h, --help                 Display this help message

Description:
  This script executes an MPI-based Python script multiple times with varying 
  numbers of language models (1 to 6) and roles (1 to 10) to verify generative AI outputs.
  It stores the results in the directory 'results/percent_agreement'.

Examples:
  $ script_name        
  $ script_name -p 5          # Runs with 5 MPI processes
   
EOF
    exit 0
}

# Default number of MPI processes
processes=3

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--processes)
            processes="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Main loop to run the script with varying number of processes
for m in {2..3}; do
    for n in {2..3}; do
        echo "mpiexec -n $processes python3 main_mpi.py -m $m -r $n"
        mpiexec -n "$processes" python3 main_mpi.py "-m $m" "-r $n"
    done
done
