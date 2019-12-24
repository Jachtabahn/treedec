import subprocess
import argparse
import logging
import sys

# 'cp {}.graphml /var/www/html/networks/{}/structs/network.graphml'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', '-c', default='echo {}')
    parser.add_argument('--input', '-i')
    parser.add_argument('--output', '-o')
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

    for name in sys.stdin:
        stripped_name = name.strip()
        specific_command = args.command.replace('{}', stripped_name)

        stdin, stdout = None, None
        if args.input is not None:
            specific_input = args.input.replace('{}', stripped_name)
            stdin = open(specific_input)
        if args.output is not None:
            specific_output = args.output.replace('{}', stripped_name)
            stdout = open(specific_output, 'w')

        subprocess.run(specific_command.split(), stdin=stdin, stdout=stdout)

        if args.input is not None:
            stdin.close()
        if args.output is not None:
            stdout.close()
