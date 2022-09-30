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

    agsi.query_facility_historical_timeseries(facilities_df, conn, config.AGSI_API_STRING, config.AGSI_EXTRACTION_KEYWORD_LIST, config.AGSI_EXTRACTION_KEYWORD_TYPE)
