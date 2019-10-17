import treedec
import network
import logging
import argparse
import os
from os import path

def determine_type(file):
    stdin_lines = file.read().split('\n')[:-1]
    for line in stdin_lines:
        if line[0] == 'c':
            continue
        if line[0] == 'p':
            return stdin_lines, 'network'
        if line[0] == 's':
            return stdin_lines, 'treedec'
    return stdin_lines, None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--structs-dir', '-s', required=True, type=str)
    parser.add_argument('--visuals-dir', '-d', required=True, type=str)
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    args.structs_dir = path.normpath(args.structs_dir)
    args.visuals_dir = path.normpath(args.visuals_dir)

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    for filename in os.listdir(args.structs_dir):
        filepath = f'{args.structs_dir}/{filename}'
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
        visual_path = f'{args.visuals_dir}/{structure_name}.dot.js'
        if path.exists(visual_path):
            logging.warning(f'Overwriting file {visual_path}..')
        else:
            logging.info(f'Creating new file {visual_path}..')
        with open(visual_path, 'w') as visual_file:
            visual_file.write(dot_string)
