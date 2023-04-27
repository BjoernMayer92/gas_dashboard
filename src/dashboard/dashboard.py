import dash
import plotly.graph_objects as go
import plotly.express as px 
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import dash
import dash_leaflet as dl
import dash_core_components as dcc
import dash_html_components as html
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc

from dash import html
from dash import dcc
from dash import Output, Input
from datetime import date

import sys
import numpy as np
import os
from pathlib import Path
import pandas as pd
import sqlite3


root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config

sys.path.append(os.path.join(root_dir, "src"))
import database


import sqlalchemy

engine = sqlalchemy.create_engine("sqlite:///../../data/data.db")
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()

storage_df = pd.read_sql("SELECT * FROM Storage",engine)
facility_df = pd.read_sql("SELECT * FROM Facility",engine)


# Select valid days, so day that have more than 40 entries
day_entry_count = storage_df.groupby("gasDayStart").count()
valid_days = day_entry_count[day_entry_count["id"]>40].index
storage_df = storage_df[storage_df["gasDayStart"].isin(valid_days)]

# Add new entries
storage_df["gasDayStart"] = pd.to_datetime(storage_df["gasDayStart"])
storage_df["year"] = storage_df["gasDayStart"].dt.year
storage_df["month"] = storage_df["gasDayStart"].dt.month
storage_df["day"]  = storage_df["gasDayStart"].dt.day

years = np.arange(2016,2023+1)


lat_arr = []
lon_arr = []
for facility_eic in facility_df["eic"]:


    latitude  = storage_df[storage_df["facility_eic"] ==facility_eic]["latitude"].unique()
    longitude = storage_df[storage_df["facility_eic"] ==facility_eic]["longitude"].unique()
    if (len(latitude) != 1) or (len(longitude) !=1):
        latitude  = 0
        longitude = 0
    else:
        latitude = latitude[0]
        longitude = longitude[0]
    lat_arr.append(latitude)
    lon_arr.append(longitude)

facility_df["latitude"] = lat_arr
facility_df["longitude"] = lon_arr


fig = go.Figure()

fig.update_layout(
    title="Cumulated Gas Storage Fullness Over Time",
    xaxis_title="Day of Year",
    yaxis_title="Gas Storage Fullness (%)",
    yaxis=dict(range=[0, 101]),
)

for year in years:
    storage_year_df = storage_df[storage_df["year"]==year]
    storage_year_daysum_df = storage_year_df[["workingGasVolume", "gasInStorage","gasDayStart"]].groupby("gasDayStart").sum()
    storage_year_daysum_df["full"] = storage_year_daysum_df["gasInStorage"]/storage_year_daysum_df["workingGasVolume"]*100
    
    fig.add_trace(go.Scatter(x=storage_year_daysum_df.index.strftime("%d-%b"), y=storage_year_daysum_df["full"], name=str(year)))

y_axis_left_options = []
for keyword in ["gasInStorage","injection","withdrawal","workingGasVolume","full"]:
    label = config.AGSI_EXTRACTION_KEYWORD_LABEL_DICT[keyword]
    value = keyword
    y_axis_left_options.append({"label":label, "value":value})

dropdown_facility = dcc.Dropdown( 
    id = 'facility_dd',
    options = facility_df["name"].values,
    value =  facility_df["name"].values[0],
    style={'color': 'black'})

dropdown_y_axis_left = dcc.Dropdown( 
    id = 'y-axis-left',
    options = y_axis_left_options,
    value = 'gasInStorage',
    style={'color': 'black'})


app = JupyterDash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container(
    [
        dbc.Row
        (
            [
                html.H1("Gas Storages in Germany"),
                html.Hr(),
                dbc.Col
                (
                    [
                    dl.Map
                        (
                            center=[facility_df["latitude"].mean(),facility_df["longitude"].mean()],  
                            style={'width': '45%', 'height': '500px'}, 
                            zoom=5, 
                            children=
                            [
                                dl.TileLayer(id="base-layer"),
                                dl.LayerGroup(id="marker-layer", children=
                                [
                                    dl.Marker(position=[row["latitude"], row["longitude"]], children=
                                    [
                                    dl.Tooltip(row["name"])
                                    ]) for _, row in facility_df.iterrows()
                                ]),
                            ],
                        ),
                    dcc.Graph(id="germany_ts",figure = fig,style={'width': '45%', 'height': '500px'})
                    ],
                     style = {"display":"flex","flex-direction":"row", "justify-content": "space-around"}
                ),
                html.Hr(),
                dbc.Col
                (
                    [
                        html.Div
                        (
                            [
                                dbc.Label("Facility"),
                                dropdown_facility
                            ],
                            style = {"width":"45%"}
                        ),
                        html.Div
                        (
                            [                                
                                dbc.Label("Y-axis"),
                                dropdown_y_axis_left
                            ],
                            style = {"width":"45%"}
                        ),
                    ],
                    style = {"display":"flex","flex-direction":"row", "justify-content": "space-around"}
                ),
                dcc.Graph(id="timeseries",figure = {},style={'width': '100%', 'height': '500px'})
            ]
        )
    ]
)


@app.callback(Output('timeseries', 'figure'), [
    Input(component_id = "facility_dd", component_property = "value"),
    Input(component_id = "y-axis-left", component_property = "value")])
def update_timeseries(facility_name, y_axis_left):
    print("update called")
    facility_eic = facility_df[facility_df["name"]==facility_name]["eic"].values[0]
    facility_timeseries = storage_df[storage_df["facility_eic"]==facility_eic]
    if facility_eic=="cluster":
        fig = px.line()    
    else:
        fig = px.line(facility_timeseries, x='gasDayStart', y=[y_axis_left], labels={
            "gasDayStart": "Day",
            "value": config.AGSI_EXTRACTION_KEYWORD_LABEL_DICT[y_axis_left]+" "+ config.AGSI_EXTRACTION_KEYWORD_UNIT_DICT[y_axis_left]})
    return fig
"""
@app.callback(Output(component_id = "facility_dd", component_property="value"), 
Input(component_id = "facilities", component_property = "click_feature"))
def facility_click(feature):
    if feature is not None:
        if feature["properties"]["cluster"]==True:
            return "cluster"
        else:
            facility_eic = feature["properties"]["eic"]
            return facility_eic


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
"""
    
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port='8060')  