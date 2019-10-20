import time
import os
from os import path
import subprocess
import json
import argparse
import logging

def time_run(command_dir, command_list, input_filepath, output_filepath, often):
    runtimes = []
    for _ in range(often):
        network_file = open(input_filepath)
        treedec_file = open(output_filepath, 'w')
        start = time.time()
        try: subprocess.run(command_list, stdin=network_file, stdout=treedec_file, cwd=command_dir)
        except Exception as e:
            logging.error(f'Solver process executed abnormally!')
            logging.error(e)
            return None
        runtimes.append(time.time() - start)
        treedec_file.close()
        network_file.close()
    return runtimes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run certain tree decomposition solvers on a certain set of networks.')
    parser.add_argument('--networks', '-n', type=str, required=True,
        help='Path to folder with network visualization folders')
    parser.add_argument('--solvers-json', '-s', type=str, required=True,
        help='Path to folder with network visualization folders')
    parser.add_argument('--often', type=int, default=1,
        help='How many times the solver should run per network')
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    args.networks = path.normpath(args.networks)
    args.solvers_json = path.normpath(args.solvers_json)

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    with open(args.solvers_json) as f:
        solvers = json.load(f)

    for network_directory in sorted(os.listdir(args.networks)):
        netpath = f'{args.networks}/{network_directory}/structs/network.gr'
        if not path.exists(netpath):
            logging.warning(f'Skipping network {netpath}')
            continue

        for name, info in solvers.items():
            solver_treedec_path = f'{args.networks}/{network_directory}/structs/{name}.td'
            runtimes = time_run(info['working_directory'], info['command'].split(), netpath, solver_treedec_path, args.often)
            if runtimes is None:
                logging.warning(f'Skipping running solver {name} on network {netpath}')
            else:
                pass

        logging.debug(f'Done {network_directory}.')
