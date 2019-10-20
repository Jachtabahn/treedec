import treedec
import network
import logging
import argparse
import os
from os import path

def normpath(my_path):
    if my_path is None: return None
    return path.normpath(my_path)

def exists(my_path):
    if my_path is None: return False
    return path.exists(my_path)

def visualize_structures(visualization_path, network_path):
    if visualization_path is None:
        network_paths = [network_path]
    else:
        network_paths = []
        for network_dirname in os.listdir(visualization_path):
            network_path = path.join(visualization_path, network_dirname)
            network_paths.append(network_path)

    for i, network_path in enumerate(sorted(network_paths)):
        logging.info(f'Visualizing structures in {network_path}: {i+1}/{len(network_paths)}.')
        network_structures_path = path.join(network_path, 'structs')
        for structure_filename in os.listdir(network_structures_path):
            filepath = path.join(network_structures_path, structure_filename)
            structure_name = structure_filename[:-3]

            if structure_filename[-3:] == '.gr':
                with open(filepath) as struct_file:
                    structure = network.parse(struct_file)
                if structure is None:
                    logging.warning(f'Skipping invalid structure {filepath}')
                    continue

                # create a dot string from the parsed structure
                dot_string = 'info.dot = `\n'
                dot_string += structure.visualize()
                dot_string += '`\n'
            elif structure_filename[-3:] == '.td':
                with open(filepath) as struct_file:
                    structure = treedec.parse(struct_file)
                if structure is None:
                    logging.warning(f'Skipping invalid structure {filepath}')
                    continue

                # create a dot string from the parsed structure
                dot_string = f'if ("{structure_name}" in info.treedecs) '
                dot_string += '{ '
                dot_string += f'info.treedecs["{structure_name}"].dot = `\n'
                dot_string += structure.visualize()
                dot_string += '`}\n'
            else:
                logging.warning(f'Ignoring file {structure_filename} with unknown extension.')
                continue

            # write that dot string to a file
            dot_path = path.join(network_path, 'visuals', f'{structure_name}.dot.js')
            if path.exists(dot_path):
                logging.debug(f'Overwriting file {dot_path}..')
            else:
                logging.debug(f'Creating new file {dot_path}..')
            with open(dot_path, 'w') as visual_file:
                visual_file.write(dot_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--visualization-path', '-d', type=str)
    parser.add_argument('--network-path', '-n', type=str)
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    args.visualization_path = normpath(args.visualization_path)
    args.network_path = normpath(args.network_path)

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    if exists(args.visualization_path):
        logging.info(f'Visualization whole networks directory {args.visualization_path}')
    elif exists(args.network_path):
        logging.info(f'Visualizing specific network at {args.network_path}')
        args.visualization_path = None
    else:
        logging.error(f'One of --visualization-path or --network_path is required!')
        exit(1)

    visualize_structures(args.visualization_path, args.network_path)
