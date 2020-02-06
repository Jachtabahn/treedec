from bokeh.io import save, output_file
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool

runtimes_table = {
  "input_id": [
    "1",
    "2",
    "3",
    "6",
    "7",
    "8",
    "11",
    "12",
    "13",
    "16",
    "17",
    "18",
    "21",
    "22",
    "23",
    "26",
    "27",
    "28",
    "31",
    "32"
  ],
  "milliseconds": [
    65,
    120,
    116,
    69,
    65,
    68,
    216,
    3277,
    216,
    1018,
    3925,
    2021,
    67,
    165,
    119,
    970,
    6000,
    816,
    168,
    115
  ]
}

# Configure the bar chart with the Sequoia input IDs and their runtimes.
plot = figure(
  title="Sequoia runtimes",
  x_range=runtimes_table["input_id"],
  plot_height=250,
  tools="box_zoom,reset,hover",
  tooltips=[
    ("Input ID", "@input_id"),
    ("Milliseconds", "@milliseconds")
  ]
)
plot.vbar(
  x="input_id",
  top="milliseconds",
  width=0.9,
  source=ColumnDataSource(runtimes_table))
plot.xgrid.grid_line_color = None
plot.y_range.start = 0

# Write the bar chart as an HTML file.
output_file("bars.html")
save(plot)
