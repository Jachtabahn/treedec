import argparse
import os
import time
import logging
import subprocess

def continuous_run(command_list, input_filepath, output_filepath, expected_filepath, timeout):
    try:
        with open(input_filepath) as input_file:
            with open(output_filepath, 'w') as output_file:
                solver_process = subprocess.run(
                    command_list,
                    stdin=input_file,
                    stdout=output_file,
                    stderr=subprocess.DEVNULL,
                    check=True,
                    timeout=timeout)
    except subprocess.TimeoutExpired:
        logging.warning('TIMEOUT!')
        return
    except subprocess.CalledProcessError:
        logging.warning('ERROR!')
        return

    # check whether output file matches the target file
    with open(output_filepath) as actual_file:
        output = actual_file.read()

    with open(expected_filepath) as expected_file:
        expected = expected_file.read()

    if output == expected:
        logging.warning('OK')
    else:
        logging.warning('WRONG!')

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
    logging.basicConfig(format='%(asctime)s - %(message)s', level=log_levels[args.verbose])

    command = 'python tw-exact.py -g ClebschGraph -t treewidths.json'
    command_list = command.split()
    input_filepath = '../easy/ClebschGraph.gr'
    output_filepath = 'actual.out'
    expected_filepath = 'expected.out'
    timeout = 10

    while 1:
        continuous_run(command_list, input_filepath, output_filepath, expected_filepath, timeout)
        time.sleep(1)
