import bokeh.io
import bokeh.plotting
import sqlite3

# Call this script with bokeh serve bars.py --port 5001 --dev bars.py

# Fetch the rows to display from the database.
connection = sqlite3.connect("/home/habimm/treedec/data/data.db")
cursor = connection.cursor()
cursor.execute("""
  SELECT formula_name, networks.rowid, decomposer_name, AVG(milliseconds)
    FROM sequoia_runtimes JOIN sequoia_inputs JOIN networks ON
    sequoia_runtimes.input_id == sequoia_inputs.rowid AND networks.name == sequoia_inputs.network_name GROUP BY input_id
""")
inputs = cursor.fetchall()
inputs = [input for input in inputs if input[0] == "longest-cycle"]
connection.close()

network_ids = list(set(row[1] for row in inputs))
sequoia = {}
meiji2016 = {}
habimm = {}
for formula_name, network_id, decomposer_name, milliseconds in inputs:
  if decomposer_name == "sequoia":
    sequoia[network_id] = milliseconds
  elif decomposer_name == "meiji2016":
    meiji2016[network_id] = milliseconds
  elif decomposer_name == "habimm":
    habimm[network_id] = milliseconds

network_ids.sort(key = lambda network_id: sequoia[network_id] + meiji2016[network_id] + habimm[network_id] if network_id in meiji2016 else sequoia[network_id] + habimm[network_id])

# Convert the fetched rows to a dictionary with a key for each column.
runtimes_table = {
  "network_id": [str(network_id) for network_id in network_ids],
  "sequoia": [sequoia[network_id] for network_id in network_ids],
  "meiji2016": [meiji2016[network_id] if network_id in meiji2016 else None for network_id in network_ids],
  "habimm": [habimm[network_id] for network_id in network_ids]
}

# Create the bar chart with the Sequoia input IDs and their runtimes.
plot = bokeh.plotting.figure(
  title="Sequoia Runtimes",
  x_range=runtimes_table["network_id"],
  plot_height=1080,
  plot_width=1920,
  tools="box_zoom,reset,hover",
  toolbar_location=None,
  tooltips=[
    ("Habimm", "@habimm{1} ms"),
    ("Meiji 2016", "@meiji2016{1} ms"),
    ("Sequoia", "@sequoia{1} ms"),
    ("Input ID", "@network_id")]
)
plot.vbar_stack(
  ["sequoia", "meiji2016", "habimm"],
  x="network_id",
  width=0.9,
  color=["#c9d9d3", "#718dbf", "#e84d60"],
  source=runtimes_table
)
plot.yaxis.axis_label = "Runtime in milliseconds"
plot.xaxis.axis_label = "Input IDs"
plot.xaxis.major_tick_line_width = 0
plot.xaxis.axis_line_width = 0
plot.yaxis.axis_line_width = 0
plot.xgrid.grid_line_color = None
plot.y_range.start = 0

bokeh.io.curdoc().add_root(plot)
