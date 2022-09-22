
import sys
import os
import requests
from pathlib import Path
import pandas as pd
import sqlite3



root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config
import keys

extraction_keyword_list = config.AGSI_EXTRACTION_KEYWORD_LIST
metadata_keyword_list = config.AGSI_METADATA_KEYWORD_LIST
api_string = config.AGSI_API_STRING
sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi

sql_database_file = config.SQL_DATABASE_FILE
conn = sqlite3.connect(sql_database_file)
conn_cursor = conn.cursor()

if __name__=='__main__':
    file_facility_queries = os.path.join(config.DATA_AGSI_DIR,"Query_listing.json")

    data = pd.read_json(file_facility_queries)

    location_name_list = []
    location_coordinates_lat_list = []
    location_coordinates_lon_list = []


    table_info = conn_cursor.execute("PRAGMA TABLE_INFO(eic_listing)").fetchall()
    table_cols = list(map( lambda x: x[1], table_info))

    if not("location_name" in table_cols):
        conn_cursor.execute("alter table eic_listing add column '{}' 'str'".format("location_name"))
    if not ("lat" in table_cols):
        conn_cursor.execute("alter table eic_listing add column '{}' 'float'".format("lat"))
    if not ("lon" in table_cols):
        conn_cursor.execute("alter table eic_listing add column '{}' 'float'".format("lon"))
    
    for name in conn_cursor.execute('SELECT name FROM eic_listing') : 
        name = name[0]
        print(name)
        query_string_parameter_dict = {"input":name, "key":keys.GOOGLE}

        query_string = agsi.generate_query_string(config.GOOGLE_API_STRING, query_string_parameter_dict = query_string_parameter_dict)

        resp = requests.get(query_string)
        resp_json = resp.json()

        status = resp_json["status"]
        if status=="OK":
            location_coordinates  = resp_json["results"][0]["geometry"]["location"]
            location_name = resp_json["results"][0]["name"]
        else: 
            location_name  = "NA"
            location_coordinates = {"lat":"NA","lng":"NA"}  

        conn_data_cursor = conn.cursor()
        sql = ''' UPDATE eic_listing
              SET lat = ? ,
                  lon = ? ,
                  location_name = ?
              WHERE name = ?'''

        conn_data_cursor.execute(sql,[location_coordinates["lat"],location_coordinates["lng"], location_name, name])
        conn.commit()
       