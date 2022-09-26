import os, sys
import requests
import pandas as pd
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm
import sqlite_functions
from sqlite_queries import *

root_dir = Path.cwd().parents[0]
conf_dir = os.path.join(root_dir,"config")

sys.path.append(str(conf_dir))

import keys

def generate_query_string(api_string, query_string_parameter_dict):
    """_summary_

    Args:
        api_string (_type_): _description_
        query_string_parameter_dict (_type_): _description_

    Returns:
        _type_: _description_
    """
    query_string = api_string
    for query_string_parameter_name in query_string_parameter_dict:
        query_string_parameter_value = query_string_parameter_dict[query_string_parameter_name]
        query_string_parameter_pair = "=".join([query_string_parameter_name, query_string_parameter_value])
        query_string = "&".join([query_string, query_string_parameter_pair])

    return query_string

def decompose_query_string(query_string):
    """_summary_

    Args:
        query_string (_type_): _description_

    Returns:
        _type_: _description_
    """
    query_string_parameter_string_list = query_string.split("&")[1:]
    query_string_parameter_dict = {}

    for query_string_parameter_string in query_string_parameter_string_list:
        query_string_parameter_name, query_string_parameter_value  = query_string_parameter_string.split("=")
        query_string_parameter_dict[query_string_parameter_name] = query_string_parameter_value;
    
    return query_string_parameter_dict



def query_eic_listing(conn, data_eic_listing, country_name="Germany"):
    """_summary_

    Args:
        data_eic_listing (_type_): _description_

    Returns:
        _type_: _description_
    """

    table_cursor = conn.cursor()
    
    table_cursor.execute(create_company_table_query)
    table_cursor.execute(create_facility_table_query)


    
    company_list = data_eic_listing["SSO"]["Europe"][country_name]
    
    
    company_cursor = conn.cursor()
    
    for company in company_list:
        company_eic = company["eic"]
        company_name = company["name"]
        company_short_name = company["short_name"]
        company_url = company["url"]
        company_country = company["data"]["country"]["code"]
        company_type = company["data"]["type"]
        company_image = company["image"]

        company_cursor.execute(insert_company_query, (company_eic, company_name,company_short_name, company_url, company_type, company_country, company_image))
        conn.commit()    
        
        facility_list = company["facilities"]
        facility_cursor = conn.cursor()
        
        for facility in facility_list:
            facility_eic = facility["eic"]
            facility_name = facility["name"]
            facility_type = facility["type"]
            facility_country = facility["country"]["code"]
            
            if (facility_type=="Storage Facility") & (not ("historical" in facility_name)):
                facility_cursor.execute(insert_facility_query, (facility_eic, facility_name, facility_type,facility_country, company_eic))
                conn.commit()

def query_facility_locations(facilities_df, conn, api_string, manual_data): 
    """_summary_

    Args:
        facilities_df (_type_): _description_
        conn (_type_): _description_
        api_string (_type_): _description_
        manual_data (_type_): _description_
    """
    
    sqlite_functions.add_cols(conn, table_name ="facilities", col_dict={"google_location_name":"str","lat":"float","lon":"float"})

    for index,facility in facilities_df.iterrows(): 
    
        name = facility["name"]
        eic = facility["eic"]

        query_string_parameter_dict = {"input":name, "key":keys.GOOGLE}
        query_string = generate_query_string(api_string, query_string_parameter_dict = query_string_parameter_dict)
        
        resp = requests.get(query_string)
        resp_json = resp.json()
        
        status = resp_json["status"]
        if status=="OK":
            location_coordinates  = resp_json["results"][0]["geometry"]["location"]
            location_name = resp_json["results"][0]["name"]
        elif (eic in list(manual_data["eic"].keys())):
            location_name  = manual_data["eic"][eic]["location_name"]
            location_coordinates = {"lat":manual_data["eic"][eic]["coordinates"]["lat"],"lng":manual_data["eic"][eic]["coordinates"]["lon"]}  
        else:
            location_name  = "NA"
            location_coordinates = {"lat":"NA","lng":"NA"}  

        conn_data_cursor = conn.cursor()
        conn_data_cursor.execute(insert_location_query,(location_coordinates["lat"], location_coordinates["lng"], location_name,eic))

    conn.commit()


def request_query_as_json(query_string, api_key=keys.AGSI):
    """_summary_

    Args:
        query_string (_type_): _description_
        api_key (_type_, optional): _description_. Defaults to keys.AGSI.

    Returns:
        _type_: _description_
    """
    header = {}
    header["x-key"] = keys.AGSI
    
    resp = requests.get(query_string, headers=header)
    data = resp.json()

    return data




def curl_data_from_query_in_db(conn, query_string, table_name, extraction_keyword_list, extraction_keyword_type):
    """_summary_

    Args:
        query_string (_type_): _description_
        extraction_keyword_list (_type_): _description_
        metadata_keyword_list (_type_): _description_

    Returns:
        _type_: _description_
    """
    

    initial_request_data = request_query_as_json(query_string)
    number_of_pages = initial_request_data["last_page"]
    
    
    # Query all pages
    for page_number in tqdm(range(number_of_pages)):
        query_string_page="&".join([query_string,"page="+str(page_number+1)])
        
        page_dictionary = request_query_as_json(query_string_page)
         
        for datapoint in page_dictionary["data"]:
            datapoint_list = []
            for keyword in extraction_keyword_list: 
                data_tmp = datapoint[keyword]
                if data_tmp== "-":
                    data_tmp= np.nan
                datapoint_list.append(extraction_keyword_type[keyword](data_tmp))
            
            sqlite_functions.insert_row(conn, table_name, col_name_list = extraction_keyword_list, data = datapoint_list)

    conn.commit()


def query_facility_historical_timeseries(facilities_df,conn, agsi_api_string, agsi_extraction_keyword_list, agsi_extraction_keyword_type):
    
    for index, facility in tqdm(facilities_df.iterrows()):
    
        country = facility["country"]
        company_eic = facility["company_eic"]
        facility_eic = facility["eic"]

        query_dict = {"country":country, "company": company_eic, "facility":facility_eic}
        query_string = generate_query_string(agsi_api_string,query_dict)
        
        initial_request_data = request_query_as_json(query_string)
        number_of_pages = initial_request_data["last_page"]

        
        cursor = conn.cursor()
        cursor.execute(create_timeseries_table_query.format(facility_eic))
        conn.commit()


        insert_timeseries_query_facility_string = insert_timeseries_query.format(facility_eic)

        insert_cursor = conn.cursor()


        for page in tqdm(range(1,number_of_pages+1), leave=False):
            query_page_dict = {"country":country, "company": company_eic, "facility":facility_eic, "page":str(page)}
            query_page_string = generate_query_string(agsi_api_string,query_page_dict)

            data_page = request_query_as_json(query_page_string)

            for data_timestamp in data_page["data"]:
                data_dict = {}
                
                for extraction_keyword in agsi_extraction_keyword_list:
                    
                    value = data_timestamp[extraction_keyword]
                    if value=="-":
                        value = np.nan
                    data_dict[extraction_keyword] = agsi_extraction_keyword_type[extraction_keyword](value)

                insert_cursor.execute(insert_timeseries_query_facility_string,tuple(data_dict.values()))
