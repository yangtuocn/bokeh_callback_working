from flask import Flask, render_template, request
import os

from random import random

from bokeh.layouts import row
from bokeh.models import CustomJS, ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

x = [random() for x in range(500)]
y = [random() for y in range(500)]

s1 = ColumnDataSource(data=dict(x=x, y=y))
p1 = figure(plot_width=400, plot_height=400, tools="lasso_select", title="Select Here")
p1.circle('x', 'y', source=s1, alpha=0.6)

s2 = ColumnDataSource(data=dict(x=[], y=[]))
p2 = figure(plot_width=400, plot_height=400, x_range=(0, 1), y_range=(0, 1),
            tools="", title="Watch Here")
p2.circle('x', 'y', source=s2, alpha=0.6)

s1.callback = CustomJS(args=dict(s2=s2), code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var d2 = s2.data;
        d2['x'] = []
        d2['y'] = []
        for (i = 0; i < inds.length; i++) {
            d2['x'].push(d1['x'][inds[i]])
            d2['y'].push(d1['y'][inds[i]])
        }
        s2.trigger('change');
    """)

layout = row(p1, p2)

scr, di = components(layout)

@app.route('/')
def index():
    return render_template('index.html',
                           plot_script = scr,
                           plot_div = di,
                           tweet_blockquote = '')

@app.route('/add', methods=['POST'])
def add_query():
    return render_template('index.html',
                           plot_script = scr,
                           plot_div = di,
                           tweet_blockquote = '')

@app.route('/plot', methods=['POST'])
def plot_query():
    return render_template('index.html',
                           plot_script = scr,
                           plot_div = di,
                           tweet_blockquote = '')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host = '0.0.0.0', port = port)
    # app.run()
