from bokeh.io import show, output_file
from bokeh.plotting import figure

runtime_rows = [
("1",65),
("2",120),
("3",116),
("6",69),
("7",65),
("8",68),
("11",216),
("12",3277),
("13",216),
("16",1018),
("17",3925),
("18",2021),
("21",67),
("22",165),
("23",119),
("26",970),
("27",6000),
("28",816),
("31",168),
("32",115),
]

input_ids = [row[0] for row in runtime_rows]
runtimes = [row[1] for row in runtime_rows]

plot = figure(x_range=input_ids, plot_height=250, title="Sequoia runtimes")
plot.vbar(x=input_ids, top=runtimes, width=0.9)

hover.tooltips = [
  ("Sample", "@names"),
  ("Pressure", "@x_values mTorr"),
  ("Roughness", "@y_values nm"),
]
plot.tools.append(hover)

plot.xgrid.grid_line_color = None
plot.y_range.start = 0

output_file("bars.html")
show(plot)
