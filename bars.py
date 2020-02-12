import bokeh.io
import bokeh.plotting
import sqlite3

# Call this script with bokeh serve bars.py --port 5001 --dev bars.py

# Fetch the rows to display from the database.
connection = sqlite3.connect("/home/habimm/treedec/data/data.db")
cursor = connection.cursor()
cursor.execute("""
  SELECT input_id, AVG(milliseconds), COUNT(*), network_name, network_id, formula_name, decomposer_name
    FROM sequoia_runtimes JOIN sequoia_inputs ON
    sequoia_runtimes.input_id == sequoia_inputs.rowid GROUP BY input_id
""")
inputs = cursor.fetchall()
connection.close()

sequoia_problems = {(input[3], input[4]): [] for input in inputs}
for input in inputs:
  sequoia_problems[(input[3], input[4])].append(input)

for problem, problem_inputs in list(sequoia_problems.items()):
  if len(problem_inputs) != 3:
    del sequoia_problems[problem]

inputs_list = list(sequoia_problems.values())
inputs = sum(inputs_list, [])

inputs = [input for input in inputs if input[4] == "hamiltonian-cycle"]

# inputs.sort(key = lambda row: row[1])

# Convert the fetched rows to a dictionary with a key for each column.
decomposer_color = {
  "": "red",
  "habimm": "green",
  "meiji2016": "blue"
}
runtimes_table = {
  "input_id": [str(input_id) for input_id, _, _, _, _, _ in inputs],
  "milliseconds": [milliseconds for _, milliseconds, _, _, _, _ in inputs],
  "color": [decomposer_color[decomposer_name] for _, _, _, _, _, decomposer_name in inputs]
}

# Create the bar chart with the Sequoia input IDs and their runtimes.
plot = bokeh.plotting.figure(
  title="Sequoia runtimes",
  x_range=runtimes_table["input_id"],
  plot_height=1080,
  plot_width=1920,
  tools="box_zoom,reset,hover",
  toolbar_location=None,
  tooltips=[
    ("Input ID", "@input_id"),
    ("Milliseconds", "@milliseconds")
  ]
)
plot.vbar(
  x="input_id",
  top="milliseconds",
  color="color",
  width=0.9,
  source=bokeh.plotting.ColumnDataSource(runtimes_table))
plot.yaxis.axis_label = "Runtime in milliseconds"
plot.xaxis.axis_label = "Input IDs"
plot.xaxis.major_tick_line_width = 0
plot.xaxis.axis_line_width = 0
plot.yaxis.axis_line_width = 0
plot.xgrid.grid_line_color = None
plot.y_range.start = 0

bokeh.io.curdoc().add_root(plot)
