import dash
import plotly.graph_objects as go
import plotly.express as px 
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


from dash import html
from dash import dcc
from dash import Output, Input

import sys
import os
from pathlib import Path
import pandas as pd
import sqlite3


root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

load_figure_template("darkly")

con = sqlite3.connect(config.SQL_DATABASE_FILE)

data = pd.read_sql_query("SELECT * from eic_listing", con)

fig =px.scatter_geo(data,
    lon = "lon",
    lat = "lat",
    hover_name = "name",
    scope="europe",
    hover_data = ["country","company","facility"])

fig.update_layout(
    geo_scope='world',
    margin=dict(l=0, r=0, t=0, b=0),

)

fig.update_geos(
    center={"lat":51.1642292, "lon":10},
    lataxis_range=[45,55],
    lonaxis_range=[5,15],
    resolution=50,
    showcoastlines=True, coastlinecolor="RebeccaPurple",
    showcountries=True,
    )

app.layout = dbc.Container(
    [
        html.H1("Gas Storages in Germany"),
        html.Hr(),
        dbc.Row( 
            [
                dbc.Col(dcc.Graph(id="map",responsive=True, figure=fig), md=4),
                dbc.Col(dcc.Graph(id="timeseries"),   md=8),
            ],
            align="center",  
        ),
    ],
    fluid=True,
    className="dbc"
)



"""
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

"""

@app.callback(Output('timeseries', 'figure'),Input('map', 'hoverData'))
def update_y_timeseries(hoverData):
    country = hoverData["points"][0]["customdata"][0]
    company = hoverData["points"][0]["customdata"][1]
    facility = hoverData["points"][0]["customdata"][2]

    timeseries_filename = "_".join([country,company,facility])+".json"
    timeseries_path = config.DATA_AGSI_DIR
    
    timeseries_df = pd.read_json(os.path.join(timeseries_path, timeseries_filename))

    fig = px.line(timeseries_df, x='gasDayStart', y=['workingGasVolume'])

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
