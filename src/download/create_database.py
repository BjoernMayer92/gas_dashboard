import sys
import os
import json
from pathlib import Path
import sqlite3
import requests
import numpy as np
import pandas as pd

root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")
from tqdm import tqdm

sys.path.append(str(conf_dir))

import config
import keys

sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi

sql_database_file = config.SQL_DATABASE_FILE

from sqlite_queries import *
import sqlite_functions

metadata_keyword_list = config.AGSI_METADATA_KEYWORD_LIST

if __name__ == '__main__':

    if os.path.exists(sql_database_file):
        os.remove(sql_database_file)    
    conn = sqlite3.connect(sql_database_file)

    query_string_eic_listing = "https://agsi.gie.eu/api/about"
    data_eic_listing = agsi.request_query_as_json(query_string_eic_listing, api_key=keys.AGSI)


    agsi.query_eic_listing(conn, data_eic_listing)

    facilities_df = pd.read_sql("SELECT * FROM facilities", conn)
    
    with open(os.path.join(config.DATA_DIR,"eic_locations.json"), 'r') as f:
        manual_data = json.load(f)

    agsi.query_facility_locations(facilities_df, conn, api_string = config.GOOGLE_API_STRING, manual_data=manual_data)

    facilities_df = pd.read_sql("SELECT * FROM facilities", conn)
    print(facilities_df)

    agsi.query_facility_historical_timeseries()
    for index, facility in tqdm(facilities_df.iterrows()):
        
        country = facility["country"]
        company_eic = facility["company_eic"]
        facility_eic = facility["eic"]

        query_dict = {"country":country, "company": company_eic, "facility":facility_eic}
        query_string = agsi.generate_query_string(config.AGSI_API_STRING,query_dict)
        
        initial_request_data = agsi.request_query_as_json(query_string)
        initial_request_data_first_entry = initial_request_data["data"][0]

        number_of_pages = initial_request_data["last_page"]

        create_timeseries_table_query="""
        CREATE TABLE IF NOT EXISTS '{}' (
            gasDayStart DATE PRIMARY KEY,
            gasInStorage FLOAT,
            injection FLOAT,
            withdrawal FLOAT,
            workingGasVolume FLOAT,
            injectionCapacity FLOAT,
            withdrawalCapacity FLOAT,
            status TEXT,
            trend FLOAT,
            full FLOAT
        )
        """

        cursor = conn.cursor()
        
        cursor.execute(create_timeseries_table_query.format(facility_eic))
        conn.commit()

        insert_timeseries_query = """ 
        INSERT INTO '{}' (gasDayStart, gasInStorage, injection, withdrawal, workingGasVolume, injectionCapacity, withdrawalCapacity, status, trend, full)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        insert_timeseries_query_facility_string = insert_timeseries_query.format(facility_eic)

        insert_cursor = conn.cursor()


        for page in tqdm(range(1,number_of_pages+1), leave=False):
            query_page_dict = {"country":country, "company": company_eic, "facility":facility_eic, "page":str(page)}
            query_page_string = agsi.generate_query_string(config.AGSI_API_STRING,query_page_dict)

            data_page = agsi.request_query_as_json(query_page_string)

            for data_timestamp in data_page["data"]:
                data_dict = {}
                
                for extraction_keyword in config.AGSI_EXTRACTION_KEYWORD_LIST:
                    
                    value = data_timestamp[extraction_keyword]
                    if value=="-":
                        value = np.nan
                    data_dict[extraction_keyword] = config.AGSI_EXTRACTION_KEYWORD_TYPE[extraction_keyword](value)

                insert_cursor.execute(insert_timeseries_query_facility_string,tuple(data_dict.values()))
