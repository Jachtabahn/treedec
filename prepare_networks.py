import network
import argparse
import logging
import os
from os import path
import json

info_schema = {
    'origin': 'Origin',
    'vertices': 'Vertices',
    'edges': 'Edges',
    'nodes': 'Nodes',
    'join_nodes': 'Join nodes',
    'treewidth': 'Treewidth',
    'joinwidth': 'Joinwidth'
}

def makedir(directory_path):
    if not path.exists(directory_path):
        os.mkdir(directory_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networks', '-n', dest='networks_dir', type=str, required=True,
        help='Path to folder with input networks')
    parser.add_argument('--server', '-s', dest='server_dir', type=str, required=True,
        help='Path to folder, where to put the visualization folders for the networks')
    parser.add_argument('--origin', '-o', type=str)
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    args.networks_dir = path.normpath(args.networks_dir)
    args.server_dir = path.normpath(args.server_dir)

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    for filename in os.listdir(args.networks_dir):
        if filename[-3:] != '.gr':
            logging.warning(f'Ignoring file {filename} with unknown extension.')
            continue

        # check if this is a real network
        filepath = f'{args.networks_dir}/{filename}'
        with open(filepath) as file:
            structure = network.parse(file)
            if structure is None:
                logging.warning(f'Error parsing network file {filepath}; ignoring..')
                continue

        structure_name = filename[:-3]
        makedir(f'{args.server_dir}/{structure_name}')
        makedir(f'{args.server_dir}/{structure_name}/structs')
        makedir(f'{args.server_dir}/{structure_name}/visuals')

        with open(f'{args.server_dir}/{structure_name}/structs/network.gr', 'w') as dest_file:
            with open(filepath) as file:
                network_string = file.read()
                dest_file.write(network_string)

        with open(f'{args.server_dir}/{structure_name}/info.js', 'w') as info_file:
            info_file.write('var info =\n')
            info = {
                'name': structure_name,
                'origin': args.origin
            }
            info_file.write(json.dumps(info, indent=4))

        with open(f'{args.server_dir}/{structure_name}/index.html', 'w') as index_file:
            with open('/home/tischler/treedec/habimm/network_template.html') as template_file:
                index_string = template_file.read()
                index_file.write(index_string)
