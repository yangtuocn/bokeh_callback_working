from flask import Flask, render_template
import numpy as np
from tornado.ioloop import IOLoop

from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import autoload_server
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server

import os

DEBUG = True

flask_app = Flask(__name__)

port = int(os.environ.get("PORT", 5000))
server_url = '0.0.0.0:' + str(port)

def modify_doc(doc):
    x = np.linspace(0, 10, 1000)
    y = np.log(x) * np.sin(x)

    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = figure()
    plot.line('x', 'y', source=source)

    slider = Slider(start=1, end=10, value=1, step=0.1)

    def callback(attr, old, new):
        y = np.log(x) * np.sin(x*new)
        source.data = dict(x=x, y=y)
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))

bokeh_app = Application(FunctionHandler(modify_doc))

io_loop = IOLoop.current()

server = Server({'/bkapp': bokeh_app}, io_loop=io_loop,
                #port=port, host=yangc-dataincubator-capstone.herokuapp.com,
                #address='0.0.0.0', use-xheaders,
                allow_websocket_origin=['yangc-dataincubator-capstone.herokuapp.com'])
server.start()

@flask_app.route('/', methods=['GET'])
def bkapp_page():
    script = autoload_server(model=None,
                             url='yangc-dataincubator-capstone.herokuapp.com/bkapp') #localhost
    return render_template("embed.html", script=script)

if __name__ == '__main__':
    from tornado.httpserver import HTTPServer
    from tornado.wsgi import WSGIContainer
    from bokeh.util.browser import view

    # print('Opening Flask app with embedded Bokeh application on http://localhost:8080/')

    # This uses Tornado to server the WSGI app that flask provides. Presumably the IOLoop
    # could also be started in a thread, and Flask could server its own app directly
    http_server = HTTPServer(WSGIContainer(flask_app))
    http_server.listen(port)

    #io_loop.add_callback(view, server_url)
    io_loop.start()
