import dash
import plotly.graph_objects as go
import plotly.express as px 
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import dash_leaflet as dl
import dash_leaflet.express as dlx
import json
from dash_extensions.javascript import assign

from dash import html
from dash import dcc
from dash import Output, Input
from datetime import datetime, date, timedelta


import sys
import os
from pathlib import Path
import pandas as pd
import sqlite3


root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], meta_tags= [{"name":"viewport","content":"width=device-width, initial-scale=1"}])

load_figure_template("darkly")

con = sqlite3.connect(config.SQL_DATABASE_FILE)

facilities = pd.read_sql_query("SELECT * from facility", con)
timeseries = pd.read_sql_query("SELECT * from storage", con)



icon_path= os.path.join(config.DATA_DIR,"assets","gas.png")


with open(os.path.join(config.DATA_DIR, "assets","facility_location.geojson"),"r") as file:
    facilities_location_json = json.load(file)

facilities_location_geojson =  dl.GeoJSON(data=facilities_location_json, id="facilities",cluster=True,  zoomToBoundsOnClick=True,
                   superClusterOptions={"radius": 100})



y_axis_left_options = []
for keyword in ["gasInStorage","injection","withdrawal","workingGasVolume","full","injectionCapacity","withdrawalCapacity"]:
    label = config.AGSI_EXTRACTION_KEYWORD_LABEL_DICT[keyword]
    value = keyword
    y_axis_left_options.append({"label":label, "value":value})



dropdown_y_axis_left = dcc.Dropdown( 
    id = 'y-axis-left',
    options = y_axis_left_options,
    value = 'gasInStorage',
    style={'color': 'black'})


facility_options = []
for row,facility in facilities.iterrows():
    label = facility["name"]
    value = facility["eic"]
    facility_options.append({"label":label, "value":value})


dropdown_facility = dcc.Dropdown( 
    id = 'facility_dd',
    options = facility_options,
    value =  facility_options[3]["value"],
    style={'color': 'black'})

max_date = date(2022, 9, 24)
min_date = date(2011, 1, 1)

date_range_picker =  dcc.DatePickerRange(
        id='date_range_picker',
        min_date_allowed = min_date,
        max_date_allowed = max_date,        
        end_date=max_date,
        start_date = min_date
    )


app.layout = dbc.Container(
    [
        html.H1("Gas Storages in Germany"),
        html.Hr(),
        dbc.Row( 
            [
                dbc.Col(dl.Map(center=(51.1642292, 10),children=[dl.TileLayer(),facilities_location_geojson],id="map",style={'width': '100%', "height":'50vh', 'margin': "auto", "display": "block"}), md=4),
                dbc.Col(dcc.Graph(id="timeseries",figure = {}),   md=8),
            ],
            align="center", style= {"height":"50vh"}
        ),
        html.Hr(),
        dbc.Row([
            dbc.Col( md=4),
            dbc.Col(html.Div([
                html.Div([html.Label("Dataset"),dropdown_y_axis_left], style={"width": "33%", "display":"block","flex-direction":"col"}),
                html.Div([html.Label("Facility"), dropdown_facility], style= {"width": "33%"}),
                ], style = {"display":"flex","flex-direction":"row", "justify-content": "space-around"}), md=8),
        ]
        ),
        dbc.Row([
            dbc.Col(md=4),
            dbc.Col(html.Div([
                html.Div([html.Label("Start Date", style={"display":"block"}), date_range_picker], style={"width": "33%", "display":"block","flex-direction":"col"}),
                html.Div(style= {"width":"33%"})
            ], style = {"display":"flex", "flex-direction": "row", "justify-content":"space-around"}))
        ])
    ],
    fluid=True,
    className="dbc"
)


@app.callback(Output(component_id = "facility_dd", component_property="value"), 
Input(component_id = "facilities", component_property = "click_feature"))
def facility_click(feature):
    if feature is not None:
        if feature["properties"]["cluster"]==True:
            return "cluster"
        else:
            facility_eic = feature["properties"]["eic"]
            return facility_eic

@app.callback(Output('timeseries', 'figure'), [
    Input(component_id = "facility_dd", component_property = "value"),
    Input(component_id = "y-axis-left", component_property = "value" ),
    Input(component_id = "date_range_picker", component_property = "start_date"),
    Input(component_id = "date_range_picker", component_property = "end_date")])

def update_timeseries(facility_eic, y_axis_left, start_date, end_date):

    facility_timeseries = timeseries[timeseries["facility_eic"]==facility_eic]
    if facility_eic=="cluster":
        fig = px.line()    
    else:
        cropped_timeseries = facility_timeseries[(facility_timeseries['gasDayStart'] > start_date) & (facility_timeseries["gasDayStart"] <= end_date)]
        fig = px.line(cropped_timeseries, x='gasDayStart', y=[y_axis_left], labels={
            "gasDayStart": "Day",
            "value": config.AGSI_EXTRACTION_KEYWORD_LABEL_DICT[y_axis_left]+" "+ config.AGSI_EXTRACTION_KEYWORD_UNIT_DICT[y_axis_left]})

    return fig

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port='8060')  