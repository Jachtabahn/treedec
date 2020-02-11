import bokeh.io
import bokeh.plotting
import sqlite3

# Call this script with bokeh serve bars.py --port 5001 --dev bars.py

# Fetch the rows to display from the database.
connection = sqlite3.connect("/home/habimm/treedec/data/data.db")
cursor = connection.cursor()
cursor.execute("""
  SELECT input_id, milliseconds, decomposer_name
    FROM sequoia_runtimes JOIN sequoia_inputs ON
    sequoia_runtimes.input_id == sequoia_inputs.rowid
    AND milliseconds < 6000
""")
inputs = cursor.fetchall()
connection.close()

inputs = [input for input in inputs if input[2] == 'habimm']

# Convert the fetched rows to a dictionary with a key for each column.
decomposer_color = {
  "": "red",
  "habimm": "green",
  "meiji2016": "blue"
}
runtimes_table = {
  "input_id": [str(input_id) for input_id, _, _ in inputs],
  "milliseconds": [milliseconds for _, milliseconds, _ in inputs],
  "color": [decomposer_color[decomposer_name] for _, _, decomposer_name in inputs]
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
