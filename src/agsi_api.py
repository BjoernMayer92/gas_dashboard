import os, sys
import requests
import pandas as pd
from datetime import datetime
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm
from sqlite_queries import *
import logging
import database
logging.basicConfig(level=logging.INFO)


root_dir = Path.cwd().parents[0]
conf_dir = os.path.join(root_dir,"config")

sys.path.append(str(conf_dir))

import config
import keys

def generate_query_string(api_string: str, query_string_parameter_dict: dict)-> str:
    """ This function generates a query string for a given dictionary of queries and an api string.
    Args:
        api_string (str): Base string of the query
        query_string_parameter_dict (str): dictionary of query parameters

    Returns:
        str: Generated query string
    """
    query_string = api_string
    for query_string_parameter_name in query_string_parameter_dict:
        query_string_parameter_value = query_string_parameter_dict[query_string_parameter_name]
        query_string_parameter_pair = "=".join([query_string_parameter_name, query_string_parameter_value])
        query_string = "&".join([query_string, query_string_parameter_pair])

    return query_string


def request_query_as_json(query_string: str, api_key:str=keys.AGSI)->dict:
    """This function takes a query string and the api key to perform the actual request and returns the result as a json dictionary.

    Args:
        query_string (str): Full query string
        api_key (str, optional): API key. Defaults to keys.AGSI:str.

    Returns:
        dict: JSON formated result of the query
    """
    header = {}
    header["x-key"] = keys.AGSI
    
    resp = requests.get(query_string, headers=header)
    data = resp.json()

    return data

def decompose_query_string(query_string:str) -> dict:
    """ THis function takes an api query string and returns a dictionary containing the properties of the query

    Args:
        query_string (str): Query string to be decomposed.

    Returns:
        dict: Dictionary containing the parameters of the query.
    """
    query_string_parameter_string_list = query_string.split("&")[1:]
    query_string_parameter_dict = {}

    for query_string_parameter_string in query_string_parameter_string_list:
        query_string_parameter_name, query_string_parameter_value  = query_string_parameter_string.split("=")
        query_string_parameter_dict[query_string_parameter_name] = query_string_parameter_value;
    
    return query_string_parameter_dict



def populate_companies_and_facilities_from_eic_listing(session, data_eic_listing, company_type="SSO", type="Europe", country_name="Germany"):
    """ This function populates the database with

    Args:
        session (_type_): _description_
        data_eic_listing (_type_): _description_
        company_type (str, optional): _description_. Defaults to "SSO".
        type (str, optional): _description_. Defaults to "Europe".
        country_name (str, optional): _description_. Defaults to "Germany".
    """
    logging.info("query_eic_listing")

    company_list = data_eic_listing[company_type][type][country_name]
        
    for company in company_list:
        company_eic = company["eic"]
        company_name = company["name"]
        company_short_name = company["short_name"]
        company_country = company["data"]["country"]["code"]
        company_type = company["data"]["type"]
        company_image = company["image"]

        new_company = database.Company(eic = company_eic,
                                        name = company_name,
                                        short_name = company_short_name,
                                        country = company_country,
                                        type = company_type,
                                        image = company_image)
        
        session.add(new_company)
        session.commit()


        facility_list = company["facilities"]
        
        for facility in facility_list:
            facility_eic = facility["eic"]
            facility_name = facility["name"]
            facility_type = facility["type"]
            facility_country = facility["country"]["code"]
            
            if (facility_type=="Storage Facility") & (not ("prior" in facility_name)):
                new_facility = database.Facility( eic = facility_eic,
                                                 name = facility_name, 
                                                 type = facility_type,
                                                 country = facility_country,
                                                 company_eic = company_eic)
                session.add(new_facility)
                session.commit()

        
def update_facility_storage(session, facility_dict):
    country = facility_dict.country
    company = facility_dict.company_eic
    facility_eic = facility_dict.eic

    ## Get First Page
    query_dict = {"country": country, "company": company, "facility": facility_eic}
    query_string = generate_query_string(config.AGSI_API_STRING,query_dict)

    first_page_data = request_query_as_json(query_string)
    first_date = first_page_data["data"][0]["gasDayStart"]
    last_page = first_page_data["last_page"]
    
    ## Get Last Page
    query_dict = {"country": country, "company": company, "facility": facility_eic, "page":str(last_page)}
    query_string = generate_query_string( config.AGSI_API_STRING,query_dict)
    last_page_data = request_query_as_json(query_string)
    last_date = last_page_data["data"][-1]["gasDayStart"]


    first_datetime = datetime.strptime(first_date,"%Y-%m-%d")
    last_datetime = datetime.strptime(last_date,"%Y-%m-%d")

    daterange = pd.date_range(last_datetime, first_datetime)
    for date in tqdm(daterange):
        date = date.strftime("%Y-%m-%d")
        storage_data = session.query(database.Storage).filter_by(facility_eic = facility_eic, gasDayStart=date).all()
        if storage_data == []:
            insert_storage_data_point(session, country= country, company=company, facility_eic=facility_eic, date=date)


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
    query_string = generate_query_string( config.AGSI_API_STRING,query_dict)

    attempts= 0
    while attempts < 3:
        try:
            data = request_query_as_json(query_string)["data"][0]

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