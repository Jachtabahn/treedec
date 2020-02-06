import subprocess
import os
import time

SEQUOIA_PATH = "/home/habimm/treedec/sequoia/src/sequoia"

inputs = [
  (
    1,
    "/var/www/html/networks/fuzix_devio_kprintf",
    "/home/habimm/treedec/sequoia/formulae/d2-dominating-set.mso",
    "Bool",
    False,
    ""
  ),
  (
    2,
    "/var/www/html/networks/fuzix_devio_kprintf",
    "/home/habimm/treedec/sequoia/formulae/clique.mso",
    "MaxCardSet",
    False,
    "meiji2016"
  ),
  (
    3,
    "/var/www/html/networks/fuzix_devio_kprintf",
    "/home/habimm/treedec/sequoia/formulae/hamiltonian-cycle.mso",
    "Bool",
    True,
    "habimm"
  ),
  (
    4,
    "/var/www/html/networks/fuzix_process_getproc",
    "/home/habimm/treedec/sequoia/formulae/steiner.mso",
    "Bool",
    False,
    "habimm"
  ),
  (
    5,
    "/var/www/html/networks/McGeeGraph",
    "/home/habimm/treedec/sequoia/formulae/3col.mso",
    "Bool",
    False,
    "meiji2016"
  ),
  (
    6,
    "/var/www/html/networks/McGeeGraph",
    "/home/habimm/treedec/sequoia/formulae/longest-cycle.mso",
    "Bool",
    True,
    ""
  )
]

def check_path(path):
  if not os.path.exists(path):
    print('Aborting: Path', path, 'doesn\'t exist.')
    exit(1)

for input_id, network_directory, formula_path, evaluation_string, only_incidence, decomposer_name in inputs:
  network_path = os.path.join(network_directory, "structs/network.graphml")
  check_path(network_path)

  sequoia_command = [
    SEQUOIA_PATH,
    "-g",
    network_path,
    "-f",
    formula_path,
    "-e",
    evaluation_string
  ]

  if only_incidence:
    sequoia_command.append("-2")

  if decomposer_name:
    treedec_path = os.path.join(network_directory, f"structs/{decomposer_name}.graphml")
    check_path(treedec_path)
    sequoia_command += ["-t", treedec_path]

  print("***********************************************************************************")
  print("Input", input_id)
  print("***********************************************************************************")
  print("Run:", " ".join(sequoia_command))

  max_milliseconds = 6000
  start = time.time()
  try:
    with open(os.devnull, "w") as null_file:
      subprocess.run(sequoia_command, check=True, stdout=null_file, stderr=null_file, timeout=max_milliseconds / 1000)
  except subprocess.CalledProcessError as error:
    print("Aborting: Sequoia returned non-zero exit status", error.returncode, ".")
    exit(error.returncode)
  except subprocess.TimeoutExpired as expired:
    pass

  milliseconds = int((time.time() - start) * 1000)
  if milliseconds <= max_milliseconds:
    print("Input", input_id, "consumed", milliseconds, "milliseconds.")
  else:
    print("Input", input_id, "consumed more milliseconds than", max_milliseconds)
  print()

print("OK.")
