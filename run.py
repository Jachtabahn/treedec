import time
import os
from os import path
import subprocess
import json
import argparse
import logging
import treedec

def write_info(info_path, info):
    with open(info_path, 'w') as file:
        file.write('var info =\n')
        file.write(json.dumps(info, indent=4))

def read_info(info_path):
    with open(info_path) as file:
        file.readline() # consume the first javascript line
        return json.load(file)

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

    if args.often < 1:
        logging.error('Must run the solvers at least once.')
        exit(1)

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

    all_directories = sorted(os.listdir(args.networks))
    for i, network_directory in enumerate(all_directories):
        netpath = f'{args.networks}/{network_directory}/structs/network.gr'
        info_path = f'{args.networks}/{network_directory}/info.js'
        if not path.exists(netpath):
            logging.warning(f'Skipping network {netpath}')
            continue

        start = time.time()
        for solver_name, solver_info in solvers.items():
            solver_treedec_path = f'{args.networks}/{network_directory}/structs/{solver_name}.td'
            runtimes = time_run(solver_info['working_directory'], solver_info['command'].split(), netpath, solver_treedec_path, args.often)
            if runtimes is None:
                logging.warning(f'Solver {solver_name} failed at network {netpath}')
                continue

            # Update network information
            with open(solver_treedec_path) as file:
                my_treedec = treedec.parse(file)
            my_treewidth, my_joinwidth = my_treedec.compute_widths()
            network_info = read_info(info_path)
            if 'treedecs' not in network_info:
                network_info['treedecs'] = {}
            if solver_name not in network_info['treedecs']:
                network_info['treedecs'][solver_name] = {}
            network_info['treedecs'][solver_name]['treewidth'] = my_treewidth
            network_info['treedecs'][solver_name]['joinwidth'] = my_joinwidth
            solver_title = solver_info['solver_title']
            network_info['treedecs'][solver_name]['treedec_title'] = f'{solver_title} tree decomposition'
            write_info(info_path, network_info)

        logging.info(f'Done {network_directory} in {time.time() - start}s: {i+1}/{len(all_directories)}.')
