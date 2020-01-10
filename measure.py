import subprocess
import treedec
import os
import time
import argparse
import logging
import sqlite3
import re

parser = argparse.ArgumentParser()
parser.add_argument('--network-regexp', '-n', type=str, default='.*')
parser.add_argument('--solver-regexp', '-s', type=str, default='.*')
parser.add_argument('--database-path', '-d', type=str, default='../csv/data.db')
parser.add_argument('--timeout', '-t', type=int, default=60) # in seconds
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

connection = sqlite3.connect(args.database_path)
def regexp(expr, text):
    regexp = re.compile(f'^{expr}$')
    return regexp.search(text) is not None
connection.create_function('REGEXP', 2, regexp)
cursor = connection.cursor()

# Load some tree decomposition plus solver combinations from the database to compute runtimes for
# These combinations may be restricted via regular expressions
cursor.execute('''
    SELECT
        treedecs.rowid,
        network_name,
        networks.path,
        treedecs.width,
        treedecs.joinwidth,
        solver_name,
        solvers.cwd,
        solvers.command
        FROM treedecs INNER JOIN networks INNER JOIN solvers
        ON treedecs.solver_name == solvers.name AND treedecs.network_name == networks.name
        AND network_name REGEXP ?
        AND solver_name  REGEXP ?;
''', (args.network_regexp,args.solver_regexp))
network_rows = cursor.fetchall()

TEMPORARY_TREEDEC_PATH = '/tmp/treedec.td'

num_treedecs = len(network_rows)
logging.debug(f'Matched {num_treedecs} tree decompositions.')

for iteration, (treedec_id, network_name, network_path, width, joinwidth, solver_name, solver_cwd, solver_cmd) in enumerate(network_rows):
    logging.debug(f'\n----------{iteration+1}/{num_treedecs}--------------------------')
    logging.debug(f'Solving {network_name} with {solver_name}')

    # Prepare the command to create the solver process
    solver_cmd_list = solver_cmd.split()
    if solver_name == 'habimm':
        solver_cmd_list += ['--width', str(width), '--joinwidth', str(joinwidth)]

    # Call the solver and wait until it terminates
    start = time.time()
    with open(os.path.join(network_path, 'structs/network.gr')) as network_file:
        with open(os.path.join(network_path, TEMPORARY_TREEDEC_PATH), 'w') as stdout_file:
            with open(os.devnull, 'w') as null_file:
                try:
                    subprocess.run(
                        solver_cmd_list,
                        cwd=solver_cwd,
                        stdin=network_file,
                        stdout=stdout_file,
                        stderr=null_file,
                        timeout=args.timeout)
                except Exception as e:
                    logging.error(f'Solver {solver_name} failed! Aborting..')
                    logging.error(e)
                    exit(1)
                except subprocess.TimeoutExpired:
                    logging.error(f'Solver {solver_name} surpassed timeout of {args.timeout} seconds!')
                    logging.error(f'Skipping network {network_name} for solver {solver_name}..')
                    continue
    milliseconds = int((time.time() - start) * 1000)

    # Check if the new output corresponds to an equivalent tree decomposition that this solver
    # has computed once in the past
    with open(os.path.join(network_path, f'structs/{solver_name}.td')) as original_file:
        original_treedec = treedec.parse(original_file)
    with open(TEMPORARY_TREEDEC_PATH) as new_file:
        new_treedec = treedec.parse(new_file)
    if str(original_treedec) == str(new_treedec):
        logging.debug('Computed the expected tree decomposition.')
    else:
        logging.error('Computed an unexpected tree decomposition!')
        logging.error(f'Solver {solver_name} failed! Aborting..')
        exit(1)

    # Add the new runtime to the database
    # In the case of the Habimm solver, also add the used parameters to the database
    cursor.execute('INSERT INTO treedec_runtimes VALUES (?, ?)', (treedec_id, milliseconds))
    connection.commit()
    logging.debug(f'Added {milliseconds} to the treedec_runtimes table to treedec id {treedec_id}')

connection.close()
