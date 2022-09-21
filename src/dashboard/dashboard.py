import dash
import plotly.graph_objects as go
from dash import html
from dash import dcc


import sys
import os
from pathlib import Path
import pandas as pd



root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config

file_facility_queries = os.path.join(config.DATA_AGSI_DIR,"Query_listing.json")

data=pd.read_json(file_facility_queries)

app = dash.Dash(__name__)


fig = go.Figure(data=go.Scattergeo(
    lon = data["lon"],
    lat = data['lat'],
    text= data['location_name'],
    mode='markers',
))

fig.update_layout(
    geo_scope='europe'
)

app.layout = html.Div(children=[
    html.H1(children='Gas Storages in Germany'),
    html.Div(children='''
        This data was provided by the USGS.
    '''),

    html.Div(children=[
    dcc.Graph(
        id='example-map',
        figure=fig
    ),
    dcc.Graph(
        id='Timeseries',
        figure={}
    )
], style={"display":"flex",})
], style={"width":"100vw","height":"100vh"})


if __name__ == '__main__':
    app.run_server(debug=True)
