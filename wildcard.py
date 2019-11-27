import sys
import subprocess
from os import path
import json
import time
import argparse
import logging

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', '-c', required=True)
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('input_paths', type=str, nargs='+')
    args = parser.parse_args()

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    # './src/sequoia -f examples/clique.mso -e MaxCardSet -g'
    command_list = args.command.split(' ')

    for _, filepath in enumerate(args.input_paths):
        start = time.time()
        print('Working on ' + filepath)
        subprocess.run(command_list + [filepath],
            check=True)
        runtime = time.time() - start
        print(filepath + ',' + str(runtime), file=sys.stderr)
        sys.stderr.flush()
