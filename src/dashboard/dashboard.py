import dash
import plotly.graph_objects as go
import plotly.express as px 
import dash_bootstrap_components as dbc



from dash import html
from dash import dcc
from dash import Output, Input

import sys
import os
from pathlib import Path
import pandas as pd



root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config

file_facility_queries = os.path.join(config.DATA_AGSI_DIR,"Query_listing.json")

data = pd.read_json(file_facility_queries)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


fig =px.scatter_geo(data,
    lon = "lon",
    lat = "lat",
    hover_name = "name",
    hover_data = ["country","company","facility"])

fig.update_layout(
    geo_scope='europe'
)

app.layout = html.Div(
children=[
    html.H1(children='Gas Storages in Germany'),
    html.Div(children='''
        This data was provided by the AGSI.
    '''),

    html.Div(children=[
    dcc.Graph(style={'width': '30%', 'height': '90vh'},
        id='map',
        figure=fig
    ),
    dcc.Graph(style={'width': '70%', 'height': '90vh'},
        id='timeseries',
        figure={}
    )
], style={"display":"flex"})
], style={"width":"100vw","height":"100vh"})

@app.callback(Output('timeseries', 'figure'),Input('map', 'hoverData'))
def update_y_timeseries(hoverData):
    country = hoverData["points"][0]["customdata"][0]
    company = hoverData["points"][0]["customdata"][1]
    facility = hoverData["points"][0]["customdata"][2]

    timeseries_filename = "_".join([country,company,facility])+".json"
    timeseries_path = config.DATA_AGSI_DIR
    
    timeseries_df = pd.read_json(os.path.join(timeseries_path, timeseries_filename))

    fig = px.line(timeseries_df, x='gasDayStart', y=['full'])

    return fig

    print(timeseries_df)
if __name__ == '__main__':
    app.run_server(debug=True)
