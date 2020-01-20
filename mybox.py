import pandas
import bokeh.plotting

input_ids = ['274', '275']

measurements = [
32004,
13004,
15809,
14114,
13656,
13252,
13855,
13554,
13503,
14556,
14654,
14907,
15808,
15059,
15407,
14303,
14607,
13004,
12901,
12951,
12702,
15256,
14557,
13256,
14555,
12698,
14357,
12802,

3927,
4226,
3878,
4280,
3826,
4379,
3926,
3928,
3576,
4327,
4281,
3830,
4179,
4228,
3527,
3926,
3926,
3524,
3927,
3926,
4025,
3575,
4127,
3925,
3925,
3574,
4126]

measurement_groups = [
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',
'274',

'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275',
'275'
]

dataframe = pandas.DataFrame({'score': measurements, 'group': measurement_groups})

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
    cat = group.name
    return group[(group.score > upper.loc[cat]['score']) | (group.score < lower.loc[cat]['score'])]['score']
out = groups.apply(outliers).dropna()

if not out.empty:
    outx = []
    outy = []
    # for keys in out.index:
    #     outx.append(keys[0])
    #     outy.append(out.loc[keys[0]].loc[keys[1]])
    for outlier_value in out.values[0]:
        outx.append('a')
        outy.append(outlier_value)

# extreme_highs = [measurements[i] for i in range(len(measurements)) if measurements[i] > upper.loc[0]['score']]
# extreme_lows = [measurements[i] for i in range(len(measurements)) if measurements[i] < lower.loc[0]['score']]

# if extreme_highs:
#     print('These measurements are extremely high:', extreme_highs)
# if extreme_lows:
#     print('These measurements are extremely low:', extreme_lows)

upper.score = [min([x, y]) for (x, y) in zip(list(my_max.loc[:, 'score']), upper.score)]
lower.score = [max([x, y]) for (x, y) in zip(list(my_min.loc[:, 'score']), lower.score)]

boxplot = bokeh.plotting.figure(background_fill_color='#efefef', x_range=input_ids)
boxplot.segment(input_ids, upper.score, input_ids, third_quarter.score, line_color='black')
boxplot.segment(input_ids, lower.score, input_ids, first_quarter.score, line_color='black')

boxplot.vbar(input_ids, .7, median.score, third_quarter.score, fill_color='#E08E79', line_color='black')
boxplot.vbar(input_ids, .7, first_quarter.score, median.score, fill_color='#3B8686', line_color='black')

boxplot.rect(input_ids, lower.score, .2, .01, line_color='black')
boxplot.rect(input_ids, upper.score, .2, .01, line_color='black')

# if not out.empty:
#     boxplot.circle(outx, outy, size=6, color='#F68630', fill_alpha=0.6)

boxplot.ygrid.grid_line_color = 'white'
boxplot.grid.grid_line_width = 2
boxplot.xaxis.major_label_text_font_size = '12pt'

bokeh.plotting.output_file('boxplot.html', title='boxplot.py example')
bokeh.plotting.show(boxplot)

