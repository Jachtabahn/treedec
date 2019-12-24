import re
import argparse
import logging
import sys

# ' ([A-Za-z0-9_,-]+)\.graphml'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pattern', '-p', default='(.*)')
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

    for line in sys.stdin:
        found = re.search(args.pattern, line)
        if found is not None:
            part = found.group(1)
            print(part)
