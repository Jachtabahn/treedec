import pandas
import bokeh.plotting
import bokeh.layouts
import sqlite3

connection = sqlite3.connect('/home/habimm/treedec/sequoia/Sequoia.db')
cursor = connection.cursor()

cursor.execute('''
    SELECT input_id, sequoia FROM runtimes
''')

runtime_rows = cursor.fetchall()
connection.close()

ids_set = [274, 275, 276, 466, 467, 468, 181, 182, 183, 451, 452, 453, 655, 656, 657]

runtime_id_strings = []
runtimes = []
for input_id, runtime in runtime_rows:
    # if input_id not in ids_set: continue
    runtime_id_strings.append(str(input_id))
    runtimes.append(runtime)
input_id_strings = list(set(runtime_id_strings))
input_id_strings.sort()

dataframe = pandas.DataFrame({'score': runtimes, 'group': runtime_id_strings})

groups = dataframe.groupby('group')
my_min =            groups.quantile(0, interpolation='lower')
first_quarter =     groups.quantile(0.25, interpolation='lower')
median =            groups.quantile(0.5, interpolation='lower')
third_quarter =     groups.quantile(0.75, interpolation='lower')
my_max =            groups.quantile(1, interpolation='lower')
span = third_quarter - first_quarter
upper = third_quarter + 1.5*span
lower = first_quarter - 1.5*span

def outliers(group):
    input_id = group.name
    return group[(group.score > upper.loc[input_id]['score']) | (group.score < lower.loc[input_id]['score'])]['score']
out = groups.apply(outliers).dropna()

if not out.empty:
    outx = []
    outy = []
    for keys in out.index:
        outx.append(keys[0])
        outy.append(out.loc[keys[0]].loc[keys[1]])

for input_id in input_id_strings:
    extreme_highs = [runtimes[i] for i in range(len(runtimes)) \
        if runtime_id_strings[i] == input_id and runtimes[i] > upper.loc[input_id]['score']]
    extreme_lows = [runtimes[i] for i in range(len(runtimes)) \
        if runtime_id_strings[i] == input_id and runtimes[i] < lower.loc[input_id]['score']]

    if extreme_highs:
        print(f'Input {input_id} has extremely high runtimes:', extreme_highs)
    if extreme_lows:
        print(f'Input {input_id} has extremely low runtimes:', extreme_lows)

upper.score = [min([x, y]) for (x, y) in zip(list(my_max.loc[:, 'score']), upper.score)]
lower.score = [max([x, y]) for (x, y) in zip(list(my_min.loc[:, 'score']), lower.score)]

num_boxplots = len(input_id_strings)
boxplots_per_figure = 3

batches = []
for boxplot_index in range(0, num_boxplots, boxplots_per_figure):
    start = boxplot_index
    end = min(boxplot_index + boxplots_per_figure, num_boxplots)

    batch = bokeh.plotting.figure(background_fill_color='#efefef', x_range=input_id_strings[start:end], plot_width=1200, plot_height=1800)

    batch.segment(input_id_strings, upper.score, input_id_strings, third_quarter.score, line_color='black')
    batch.segment(input_id_strings, lower.score, input_id_strings, first_quarter.score, line_color='black')

    batch.vbar(input_id_strings, .7, median.score, third_quarter.score, fill_color='#E08E79', line_color='black')
    batch.vbar(input_id_strings, .7, first_quarter.score, median.score, fill_color='#3B8686', line_color='black')

    batch.rect(input_id_strings[start:end], upper.score[start:end], .2, .01, line_color='black')
    batch.rect(input_id_strings[start:end], lower.score[start:end], .2, .01, line_color='black')

    if not out.empty:
        batch.circle(outx, outy, size=6, color='#F68630', fill_alpha=0.6)

    batch.ygrid.grid_line_color = 'white'
    batch.grid.grid_line_width = 2
    batch.xaxis.major_label_text_font_size = '12pt'

    batches.append(batch)

bokeh.plotting.output_file('all_boxplots.html', title='All Sequoia runtime boxplots')
all_boxplots = bokeh.layouts.row(*batches)
bokeh.plotting.show(all_boxplots)
