import os
from os import path
import json
import argparse
import logging

def read_info(info_path):
    with open(info_path) as file:
        file.readline() # consume the first javascript line
        return json.load(file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run a certain tree decomposition solver on a certain set of networks.')
    parser.add_argument('--networks', '-n', type=str, required=True,
        help='Path to folder with network visualization folders')
    parser.add_argument('--treewidths-json', '-t', type=str, required=True,
        help='Path to folder with network visualization folders')
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    args.networks = path.normpath(args.networks)
    args.treewidths_json = path.normpath(args.treewidths_json)

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    treewidths_database = {}
    all_directories = sorted(os.listdir(args.networks))
    for i, network_directory in enumerate(all_directories):
        netpath = f'{args.networks}/{network_directory}/structs/network.gr'
        if not path.exists(netpath):
            logging.warning(f'Skipping network {netpath}')
            continue

        info_path = f'{args.networks}/{network_directory}/info.js'
        network_info = read_info(info_path)
        treewidth = network_info['treedecs']['meiji2016']['treewidth']
        treewidths_database[network_directory] = treewidth

        logging.info(f'Done {network_directory}: {i+1}/{len(all_directories)}.')

    with open(args.treewidths_json, 'w') as file:
        file.write(json.dumps(treewidths_database, indent=4))
