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

def visualize_structures(networks_dir, structs_dir):
    if networks_dir is None:
        structure_paths = [structs_dir]
    else:
        structure_paths = []
        for network_dir in os.listdir(networks_dir):
            structure_path = path.join(networks_dir, network_dir)
            structure_paths.append(structure_path)

    for structure_path in structure_paths:
        logging.info(f'Visualizing structures in {structure_path}')
        for filename in os.listdir(structure_path):
            filepath = path.join(structs_dir, filename)
            structure_name = filename[:-3]

            if filename[-3:] == '.gr':
                with open(filepath) as struct_file:
                    structure = network.parse(struct_file)

                # create a dot string from the parsed structure
                dot_string = 'info.dot = `\n'
                dot_string += structure.visualize()
                dot_string += '`\n'
            elif filename[-3:] == '.td':
                with open(filepath) as struct_file:
                    structure = treedec.parse(struct_file)

                # create a dot string from the parsed structure
                dot_string = f'if ("{structure_name}" in info.treedecs) '
                dot_string += '{ '
                dot_string += f'info.treedecs["{structure_name}"].dot = `\n'
                dot_string += structure.visualize()
                dot_string += '`}\n'
            else:
                logging.warning(f'Ignoring file {filename} with unknown extension.')
                continue

            # write that dot string to a file
            network_dir, _ = structs_dir.split()
            visual_path = path.join(network_dir, 'visuals')
            if path.exists(visual_path):
                logging.warning(f'Overwriting file {visual_path}..')
            else:
                logging.info(f'Creating new file {visual_path}..')
            with open(visual_path, 'w') as visual_file:
                visual_file.write(dot_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networks-dir', '-n', type=str)
    parser.add_argument('--structs-dir', '-s', type=str)
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    args.networks_dir = normpath(args.networks_dir)
    args.structs_dir = normpath(args.structs_dir)

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    if exists(args.networks_dir):
        logging.info(f'Visualization whole networks directory {args.networks_dir}')
    elif exists(args.structs_dir) and exists(args.structs_dir):
        logging.info(f'Visualizing specific network at {args.structs_dir}')
        args.networks_dir = None
    else:
        logging.error(f'At least one of --networks, or --structs_dir and --visuals_dir is required!')
        exit(1)

    visualize_structures(args.networks_dir, args.structs_dir)
