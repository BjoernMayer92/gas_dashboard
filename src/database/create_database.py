import sys
import os
import json
from pathlib import Path
import requests
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timedelta

root_dir = Path(os.path.abspath(__file__)).parents[2]
print(root_dir)
conf_dir = os.path.join(root_dir,"config")


from tqdm import tqdm

sys.path.append(str(conf_dir))

import config
import keys

sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi
import database as database

sql_database_file = config.SQL_DATABASE_FILE

from sqlite_queries import *


if __name__ == '__main__':

    if not os.path.exists(sql_database_file):
        database.create_database(sql_database_file)

    query_string_eic_listing = "https://agsi.gie.eu/api/about"
    data_eic_listing = agsi.request_query_as_json(query_string_eic_listing, api_key=keys.AGSI)
    
    engine = create_engine("sqlite:///{}".format(sql_database_file))
    Session = sessionmaker(bind=engine)
    session = Session()

    agsi.populate_companies_and_facilities_from_eic_listing(session, data_eic_listing)
    
    
    #print(last_page)


    """ 

    facilities_df = pd.read_sql("SELECT * FROM facilities", conn)
    
    with open(os.path.join(config.DATA_DIR,"eic_locations.json"), 'r') as f:
        manual_data = json.load(f)

    agsi.query_facility_locations(facilities_df, conn, api_string = config.GOOGLE_API_STRING, manual_data=manual_data)

    facilities_df = pd.read_sql("SELECT * FROM facilities", conn)
    print(facilities_df)

    agsi.query_facility_historical_timeseries(facilities_df, conn, config.AGSI_API_STRING, config.AGSI_EXTRACTION_KEYWORD_LIST, config.AGSI_EXTRACTION_KEYWORD_TYPE)
    """