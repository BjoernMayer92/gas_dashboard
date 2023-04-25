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

    if os.path.exists(sql_database_file):
        os.remove(sql_database_file)    
    
    database.create_database(sql_database_file)

    query_string_eic_listing = "https://agsi.gie.eu/api/about"
    data_eic_listing = agsi.request_query_as_json(query_string_eic_listing, api_key=keys.AGSI)
    
    engine = create_engine("sqlite:///{}".format(sql_database_file))
    Session = sessionmaker(bind=engine)
    session = Session()

    agsi.populate_companies_and_facilities_from_eic_listing(session, data_eic_listing)
    
    facilities = session.query(database.Facility).all()
    print(facilities)
    
    facility = facilities[0]

    country = facility.country
    company = facility.company_eic
    facility_eic = facility.eic

    

    def insert_storage_data_point(session,country, company, facility_eic, date):
        data_dict = query_storage_data_point(country= country, company=company, facility_eic = facility_eic, date=date)
        new_storage = database.Storage(gasDayStart = datetime.strptime(data_dict["gasDayStart"],"%Y-%m-%d"),
                gasInStorage = data_dict["gasInStorage"],
                injection = data_dict["injection"],
                withdrawal = data_dict["withdrawal"],
                workingGasVolume = data_dict["workingGasVolume"],
                injectionCapacity = data_dict["injectionCapacity"],
                withdrawalCapacity = data_dict["withdrawalCapacity"],
                status= data_dict["status"],
                trend = data_dict["trend"],
                full = data_dict["full"],
                latitude = data_dict["latitude"],
                longitude = data_dict["longitude"],
                facility_eic = facility_eic
                )
        session.add(new_storage)
        
        session.commit()

    def query_storage_data_point(country, company, facility_eic, date):
        query_dict = {"country": country, "company": company, "facility": facility_eic,"date":date}
        query_string = agsi.generate_query_string( config.AGSI_API_STRING,query_dict)

        attempts= 0
        while attempts < 3:
            try:
                data = agsi.request_query_as_json(query_string)["data"][0]

                data_dict = {}

                for extraction_keyword in config.AGSI_EXTRACTION_KEYWORD_LIST:
                    value = data[extraction_keyword]
                    if value=="-":
                        value = np.nan
                    data_dict[extraction_keyword] = config.AGSI_EXTRACTION_KEYWORD_TYPE[extraction_keyword](value)
                return data_dict
            except Exception as e:
                print(e)
                attempts += 1
        


         
    ## Get First Page
    query_dict = {"country": country, "company": company, "facility": facility_eic}
    query_string = agsi.generate_query_string( config.AGSI_API_STRING,query_dict)

    first_page_data = agsi.request_query_as_json(query_string)
    first_date = first_page_data["data"][0]["gasDayStart"]
    last_page = first_page_data["last_page"]
    
    ## Get Last Page
    query_dict = {"country": country, "company": company, "facility": facility_eic, "page":str(last_page)}
    query_string = agsi.generate_query_string( config.AGSI_API_STRING,query_dict)
    last_page_data = agsi.request_query_as_json(query_string)
    last_date = last_page_data["data"][-1]["gasDayStart"]


    first_datetime = datetime.strptime(first_date,"%Y-%m-%d")
    last_datetime = datetime.strptime(last_date,"%Y-%m-%d")

    daterange = pd.date_range(last_datetime, first_datetime)
    for date in tqdm(daterange):
        date = date.strftime("%Y-%m-%d")
        storage_data = session.query(database.Storage).filter_by(facility_eic = facility_eic, gasDayStart=date).all()
        if storage_data == []:
            insert_storage_data_point(session, country= country, company=company, facility_eic=facility_eic, date=date)

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