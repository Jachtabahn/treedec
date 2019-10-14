import treedec
import network
import logging
import argparse
import sys

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
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    stdin_lines, structure_type = determine_type(sys.stdin)

    if structure_type == 'network':
        my_network = network.parse_network(stdin_lines)
        my_network.write_dot(output_file=sys.stdout)
    elif structure_type == 'treedec':
        my_treedec = treedec.parse_treedec(stdin_lines)
        my_treedec.write_dot(output_file=sys.stdout)
    elif structure_type == None:
        logging.error('The stdin file is neither a network nor a tree decomposition! Abort.')
