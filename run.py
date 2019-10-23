import time
import os
from os import path
import subprocess
import json
import argparse
import logging
import treedec

def check_treedec(solver_treedec_path):
    if not path.exists(solver_treedec_path):
        return None
    with open(solver_treedec_path) as file:
        my_treedec = treedec.parse(file)
    return my_treedec

def write_info(info_path, info):
    with open(info_path, 'w') as file:
        file.write('var info =\n')
        file.write(json.dumps(info, indent=4))

def read_info(info_path):
    with open(info_path) as file:
        file.readline() # consume the first javascript line
        return json.load(file)

def time_run(command_dir, command_list, input_filepath, output_filepath, often, timeout):
    runtimes = []
    for _ in range(often):
        network_file = open(input_filepath)
        treedec_file = open(output_filepath, 'w')
        start = time.time()
        try:
            solver_process = subprocess.run(
                command_list,
                stdin=network_file,
                stdout=treedec_file,
                cwd=command_dir,
                timeout=timeout)
            solver_process.check_returncode()
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
    parser.add_argument('--often', '-o', type=int, default=1,
        help='How many times the solver should run per network')
    parser.add_argument('--timeout', '-t', type=int, default=30,
        help='Number of seconds after which any solver times out')
    parser.add_argument('--overwrite', '-w', default=False, action='store_const', const=True,
        help='Should the solver overwrite a non-existent or invalid tree decomposition?')
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    args.networks = path.normpath(args.networks)
    args.solvers_json = path.normpath(args.solvers_json)

    assert args.often >= 0

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
        logging.info(f'Working network {network_directory}: {i+1}/{len(all_directories)}..')

        network_start = time.time()
        for solver_name, solver_info in solvers.items():
            solver_start = time.time()
            logging.info(f'Launching solver {solver_name}..')
            solver_treedec_path = f'{args.networks}/{network_directory}/structs/{solver_name}.td'

            # Skip this solver, if we do not want to overwrite things and there is already a tree decomposition there
            if not args.overwrite:
                my_treedec = check_treedec(solver_treedec_path)
                if my_treedec is not None:
                    logging.warning(f'Will not overwrite {solver_treedec_path}; skipping..')
                    continue

            command = solver_info['command'].split()
            command += ['-g', network_directory]
            runtimes = time_run(
                solver_info['working_directory'],
                command,
                netpath,
                solver_treedec_path,
                args.often,
                args.timeout)
            if runtimes is None:
                logging.warning(f'Solver {solver_name} failed at network {netpath}')
                continue

            # Update network information
            my_treedec = check_treedec(solver_treedec_path)
            if my_treedec is None:
                logging.warning(f'Tree decomposition of solver {solver_name} does not exist or is invalid; skipping..')

            my_num_nodes, my_num_joins, my_treewidth, my_joinwidth = my_treedec.collect_info()
            network_info = read_info(info_path)
            if 'treedecs' not in network_info:
                network_info['treedecs'] = {}
            if solver_name not in network_info['treedecs']:
                network_info['treedecs'][solver_name] = {}

            # Fill in some info about this tree decomposition
            my_info = network_info['treedecs'][solver_name]
            my_info['network_name'] = network_directory
            my_info['solver_title'] = solver_info['solver_title']
            my_info['network_title'] = network_directory
            my_info['treedec_title'] = f'{solver_info["solver_title"]} tree decomposition'
            my_info['nodes'] = my_num_nodes
            my_info['join_nodes'] = my_num_joins
            my_info['edges'] = my_num_nodes - 1
            my_info['treewidth'] = my_treewidth
            my_info['joinwidth'] = my_joinwidth

            write_info(info_path, network_info)
            logging.info(f'Solver {solver_name} finished in {time.time() - solver_start}s.')

        logging.info(f'Done with network {network_directory} in {time.time() - network_start}s: {i+1}/{len(all_directories)}.')
