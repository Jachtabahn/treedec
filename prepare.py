import network
import argparse
import logging
import os
from os import path
import json

def makedir(directory_path):
    if not path.exists(directory_path):
        os.mkdir(directory_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networks', '-n', dest='networks_dir', type=str, required=True,
        help='Path to folder with input networks')
    parser.add_argument('--server', '-s', dest='server_dir', type=str, required=True,
        help='Path to folder, where to put the visualization folders for the networks')
    parser.add_argument('--category', '-o', type=str)
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
            my_network = network.parse(file)
            my_network.make_symmetric() # need to do this to get the number of vertices below
            if my_network is None:
                logging.warning(f'Error parsing network file {filepath}; ignoring..')
                continue

        structure_name = filename[:-3]
        makedir(f'{args.server_dir}/{structure_name}')
        makedir(f'{args.server_dir}/{structure_name}/structs')
        makedir(f'{args.server_dir}/{structure_name}/visuals')

        # Copy the network structure to the server
        network_path = f'{args.server_dir}/{structure_name}/structs/network.gr'
        if not path.exists(network_path):
            with open(network_path, 'w') as dest_file:
                with open(filepath) as file:
                    network_string = file.read()
                    dest_file.write(network_string)

        info_path = f'{args.server_dir}/{structure_name}/info.js'
        if not path.exists(info_path):
            with open(info_path, 'w') as info_file:
                info_file.write('var info =\n')
                info = {
                    'network_name': structure_name,
                    'category': args.category,
                    'network_title': structure_name,
                    'vertices': len(my_network.vertices()),
                    'edges': len(my_network.one_directional()),
                    'treedecs': {},
                    'schema': {
                        'network_name': 'Network ID',
                        'category': 'Category',
                        'solver_title': 'Solver',
                        'network_title': 'Network',
                        'treedec_title': 'Tree decomposition',

                        'vertices': 'Vertices',
                        'nodes': 'Nodes',
                        'join_nodes': 'Join nodes',
                        'edges': 'Edges',
                        'treewidth': 'Treewidth',
                        'joinwidth': 'Joinwidth'
                    }
                }
                info_file.write(json.dumps(info, indent=4))

        # Create a hard link in this network's directory to this project's index template
        index_path = f'{args.server_dir}/{structure_name}/index.html'
        if not path.exists(index_path):
            cwd = os.getcwd()
            os.link(
                path.join(cwd, 'network_index.html'),
                index_path)
