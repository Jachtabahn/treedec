import argparse
import bokeh
import bokeh.plotting
import logging
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument('--present-formula', '-f', required=True)
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

# Fetch the rows to display from the database.
connection = sqlite3.connect("/home/habimm/treedec/data/data.db")
cursor = connection.cursor()
cursor.execute("""
  SELECT formula_name, networks.rowid, sequoia_inputs.rowid, decomposer_name, AVG(milliseconds), COUNT()
    FROM sequoia_runtimes JOIN sequoia_inputs JOIN networks ON
    sequoia_runtimes.input_id == sequoia_inputs.rowid AND networks.name == sequoia_inputs.network_name GROUP BY input_id
""")
inputs = cursor.fetchall()
inputs = [input for input in inputs if input[0] == args.present_formula]
connection.close()

# Find and log all decomposers in the fetched inputs.
input_attribute = {}
decomposer_names = list(set(row[3] for row in inputs))
for decomposer_name in decomposer_names:
  input_attribute[decomposer_name] = {}
logging.info(f"Found following {len(decomposer_names)} decomposers: {decomposer_names}")

# Insert all rows in a row dictionary indexed by the decomposer and the network.
for _, network_id, input_id, decomposer_name, milliseconds, count in inputs:
  input_attribute[decomposer_name][network_id] = {
    "milliseconds": milliseconds,
    "count": count,
    "input_id": input_id
  }

def get_attribute(decomposer_name, network_id, attribute, default=None):
  if network_id in input_attribute[decomposer_name]:
    return input_attribute[decomposer_name][network_id][attribute]
  else:
    return default

# Find all network IDs in the inputs and sort them by the sum of the runtimes across all decomposers.
network_ids = list(set(row[1] for row in inputs))
network_ids.sort(
  key=lambda network_id:
  get_attribute("habimm", network_id, "milliseconds", 0) + \
  get_attribute("meiji2016", network_id, "milliseconds", 0) + \
  get_attribute("sequoia", network_id, "milliseconds", 0))

# Convert the row dictionary to a dictionary with several keys for each presented bar.
input_runtimes = {}
input_runtimes["network_id"] = [str(network_id) for network_id in network_ids]
for decomposer_name in decomposer_names:
  for attribute in ["milliseconds", "count", "input_id"]:
    input_runtimes[decomposer_name + "_" + attribute] = [get_attribute(decomposer_name, network_id, attribute) for network_id in network_ids]

# Create a Bokeh plot.
plot = bokeh.plotting.figure(
  title="Sequoia Runtimes on the Formula " + args.present_formula,
  x_range=input_runtimes["network_id"],
  plot_height=1000,
  plot_width=1900,
  tools="box_zoom,reset,hover",
  toolbar_location=None,
  tooltips=[
    ("Habimm", "@habimm_milliseconds{1} ms (@habimm_count)"),
    ("Meiji 2016", "@meiji2016_milliseconds{1} ms (@meiji2016_count)"),
    ("Sequoia", "@sequoia_milliseconds{1} ms (@sequoia_count)"),
    ("Network ID", "@network_id"),
    ("Input IDs", "@habimm_input_id, @meiji2016_input_id, @sequoia_input_id")]
)
plot.xaxis.axis_label = "Network IDs"
plot.xaxis.axis_line_width = 0
plot.xaxis.major_tick_line_width = 0
plot.xgrid.grid_line_color = None
plot.y_range.start = 0
plot.yaxis.axis_label = "Runtime in milliseconds"
plot.yaxis.axis_line_width = 0

# Create a bar chart with the network IDs on the horizontal and Sequoia runtimes on the vertical axis.
plot.vbar_stack(
  # build up the bar from the bottom up to the top
  ["sequoia_milliseconds", "meiji2016_milliseconds", "habimm_milliseconds"],
  x="network_id",
  width=0.9,
  color=["#c9d9d3", "#718dbf", "#e84d60"],
  source=input_runtimes
)

# Filter those network IDs for which the Habimm network has a better runtime than anything else.
asterisks_data = {}
asterisks_data["winner_network_id"] = [
  str(network_id) for network_id in network_ids if\
  get_attribute("habimm", network_id, "milliseconds", 0) < get_attribute("meiji2016", network_id, "milliseconds", 0) and\
  get_attribute("habimm", network_id, "milliseconds", 0) < get_attribute("sequoia", network_id, "milliseconds", 0)]

# Determine the highest accumulated runtime over all networks
accumulated_runtimes = []
for network_id in network_ids:
  accu = get_attribute("habimm", network_id, "milliseconds", 0) +\
    get_attribute("meiji2016", network_id, "milliseconds", 0) +\
    get_attribute("sequoia", network_id, "milliseconds", 0)
  accumulated_runtimes.append(accu)

# Set the height for the asterisks to be slightly above the accumulated runtime of that network.
asterisks_data["height"] = [(
  get_attribute("habimm", int(network_id), "milliseconds", 0) +\
  get_attribute("meiji2016", int(network_id), "milliseconds", 0) +\
  get_attribute("sequoia", int(network_id), "milliseconds", 0)) * 4/3 for network_id in asterisks_data["winner_network_id"]]

# Render the asterisks.
asterisks_glyph = bokeh.models.Asterisk(x="winner_network_id", y="height", size=25, line_color="#f0027f", fill_color=None, line_width=2)
plot.add_glyph(bokeh.models.ColumnDataSource(asterisks_data), asterisks_glyph)

bokeh.io.curdoc().add_root(plot)
