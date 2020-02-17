import argparse
import logging
import os
import sqlite3
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument("--sequoia-path", type=str, default="/home/habimm/treedec/sequoia/src/sequoia")
parser.add_argument("--max-milliseconds", type=int, default=6000)
parser.add_argument("--update-database", action="store_const", const=True, default=False)
parser.add_argument("--start-input-id", type=int, default=1)
parser.add_argument("--verbose", "-v", action="count")
args = parser.parse_args()

log_levels = {
    None: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}
if args.verbose is not None and args.verbose >= len(log_levels):
    args.verbose = len(log_levels)-1
logging.basicConfig(format="%(message)s", level=log_levels[args.verbose])

# This SQL statement excludes 5 * 16 inputs, which involve five graphs.
# For these graphs, meiji2016 computes tree decompositions, on which Sequoia tries to access an invalid bag index.
connection = sqlite3.connect("/home/habimm/treedec/data/data.db")
cursor = connection.cursor()
cursor.execute("""
  SELECT sequoia_inputs.rowid, networks.path AS network_directory, formulae.path AS formula_path, formulae.evaluation, formulae.only_incidence, decomposer_name
    FROM sequoia_inputs JOIN formulae JOIN networks
    ON sequoia_inputs.network_name == networks.name
    AND sequoia_inputs.formula_name == formulae.name
    AND (decomposer_name == 'meiji2016' OR decomposer_name == 'habimm' OR decomposer_name == 'sequoia')
    AND comment is NULL
    AND sequoia_inputs.rowid >= ?
""", (args.start_input_id,))
inputs = cursor.fetchall()

# Abort on an invalid path.
def check_path(path):
  if not os.path.exists(path):
    print("Aborting: Path", path, "doesn\"t exist.")
    exit(1)

# Measure the runtime of Sequoia on every fetched input.
for input_id, network_directory, formula_path, evaluation_string, only_incidence, decomposer_name in inputs:

  # Construct a command line to call Sequoia.
  network_path = os.path.join(network_directory, "structs/network.graphml")
  check_path(network_path)
  sequoia_command = [
    args.sequoia_path,
    "-g",
    network_path,
    "-f",
    formula_path,
    "-e",
    evaluation_string
  ]
  if only_incidence == "true":
    sequoia_command.append("-2")
  if decomposer_name != "sequoia":
    treedec_path = os.path.join(network_directory, f"structs/{decomposer_name}.graphml")
    check_path(treedec_path)
    sequoia_command += ["-t", treedec_path]

  # Present the input ID and the command line about to be run to the user.
  print("***********************************************************************************")
  print("Input", input_id)
  print("***********************************************************************************")
  print("Run:", " ".join(sequoia_command))

  # Run the Sequoia program and measure the time from start until termination.
  start = time.time()
  try:
    with open(os.devnull, "w") as null_file:
      subprocess.run(sequoia_command, check=True, stdout=null_file, stderr=null_file, timeout=args.max_milliseconds / 1000)
  except subprocess.CalledProcessError as error:
    print("Aborting: Sequoia returned non-zero exit status", error.returncode, ".")
    exit(error.returncode)
  except subprocess.TimeoutExpired as expired:
    pass

  # Present the number of milliseconds, that Sequoia was running, to the user.
  milliseconds = int((time.time() - start) * 1000)
  if milliseconds <= args.max_milliseconds:
    print("Input", input_id, "consumed", milliseconds, "milliseconds.")
    if args.update_database:
      cursor.execute("""
        INSERT INTO sequoia_runtimes (input_id, milliseconds) VALUES (?, ?)
        """, (input_id, milliseconds))
      connection.commit()
      print("Updated the database.")
  else:
    print("Input", input_id, "consumed more than", args.max_milliseconds, "milliseconds.")
    if args.update_database:
      cursor.execute("""
        INSERT INTO sequoia_runtimes (input_id, milliseconds) VALUES (?, ?)
        """, (input_id, args.max_milliseconds))
      connection.commit()
      print("Updated the database.")
  print()

connection.close()
print("OK.")
