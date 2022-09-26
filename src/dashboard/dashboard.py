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
from datetime import date

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

facilities = pd.read_sql_query("SELECT * from facilities", con)
timeseries = pd.read_sql_query("SELECT * from data", con)

print(facilities)



icon_path= os.path.join(config.DATA_DIR,"assets","gas.png")

#draw_icon = assign("""function(feature, latlng){
#const gas = L.icon({iconUrl: `https://img.icons8.com/ios-filled/344/gas.png`, iconSize: [64, 48]});
#return L.marker(latlng, {icon: gas});
#}""")


with open(os.path.join(config.DATA_DIR, "assets","facility_location.geojson"),"r") as file:
    facilities_location_json = json.load(file)
#options=dict(pointToLayer=draw_icon)
facilities_location_geojson =  dl.GeoJSON(data=facilities_location_json, id="facilities")





"""
map =px.scatter_geo(facilities,
    lon = "lon",
    lat = "lat",
    hover_name = "name",
    hover_data = ["country","company_eic","eic"])

map.update_layout(
    geo_scope='world',
    margin=dict(l=0, r=0, t=0, b=0),

)

map.update_geos(
    center={"lat":51.1642292, "lon":10},
    lataxis_range=[45,55],
    lonaxis_range=[5,15],
    resolution=50,
    showcoastlines=True, coastlinecolor="RebeccaPurple",
    showcountries=True,
    )


app.layout = html.Div([dl.Map(children=[
    dl.TileLayer(),
    facilities_location_geojson], 
    style={'width': '1000px', 'height': '500px'})])

"""



y_axis_left_options = []
for keyword in ["gasInStorage","injection","withdrawal","workingGasVolume","injectionCapacity","withdrawalCapacity"]:
    label = config.AGSI_EXTRACTION_KEYWORD_LABEL_DICT[keyword]
    value = keyword
    y_axis_left_options.append({"label":label, "value":value})



dropdown_y_axis_left = dcc.Dropdown( 
    id = 'y-axis-left',
        options = y_axis_left_options,
        value = 'gasInStorage')


facility_options = []
for row,facility in facilities.iterrows():
    label = facility["name"]
    value = facility["eic"]
    facility_options.append({"label":label, "value":value})


dropdown_facility = dcc.Dropdown( 
    id = 'facility_dd',
        options = facility_options,
                value = facilities.iloc[0]["eic"])


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
                dropdown_y_axis_left,
                dropdown_facility
                ]), md=8),
        ]
        )
    ],
    fluid=True,
    className="dbc"
)


@app.callback(Output(component_id = "facility_dd", component_property="value"), 
Input(component_id = "facilities", component_property = "click_feature"))
def facility_click(feature):
    if feature is not None:
        facility_eic = feature["properties"]["eic"]
        return facility_eic

@app.callback(Output('timeseries', 'figure'), [
    Input(component_id = "facility_dd", component_property = "value"),
    Input(component_id = "y-axis-left", component_property = "value" )])
def update_timeseries(facility_eic, y_axis_left):
    facility_timeseries = timeseries[timeseries["facility_eic"]==facility_eic]

    fig = px.line(facility_timeseries, x='gasDayStart', y=[y_axis_left], labels={
                     "gasDayStart": "Day",
                     "value": config.AGSI_EXTRACTION_KEYWORD_LABEL_DICT[y_axis_left]+" "+ config.AGSI_EXTRACTION_KEYWORD_UNIT_DICT[y_axis_left]})

    return fig

"""

    country = hoverData["points"][0]["customdata"][0]
    company = hoverData["points"][0]["customdata"][1]
    facility = hoverData["points"][0]["customdata"][2]

    timeseries_filename = "_".join([country,company,facility])+".json"
    timeseries_path = config.DATA_AGSI_DIR
    
    timeseries_df = pd.read_json(os.path.join(timeseries_path, timeseries_filename))

    fig = px.line(timeseries_df, x='gasDayStart', y=['workingGasVolume'])
"""

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






if __name__ == '__main__':
    app.run_server(debug=True)
