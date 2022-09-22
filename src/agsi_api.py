import os, sys
import requests
import pandas as pd
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm

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



def generate_query_string_list(data_eic_listing, api_string, country_name="Germany"):
    """_summary_

    Args:
        data_eic_listing (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    company_list = data_eic_listing["SSO"]["Europe"][country_name]
    query_string_parameter_list = []
    query_string_parameter_dict = {}

    for company in company_list:
        query_string_parameter_dict["company"] = company["eic"]
        facility_list = company["facilities"]
        for facility in facility_list:
            query_string_parameter_dict["facility"] = facility["eic"]
            query_string_parameter_dict["country"] = facility["country"]["code"]
            query_string = generate_query_string(api_string, query_string_parameter_dict)
            
            query_string_parameter_list.append([
                query_string_parameter_dict["country"],
                query_string_parameter_dict["company"],
                query_string_parameter_dict["facility"],
                facility["name"],
                query_string
                ])



    return pd.DataFrame(query_string_parameter_list, columns = ["country","company","facility","name","query_string"])

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

def curl_data_from_query(query_string, extraction_keyword_list, extraction_keyword_type, metadata_keyword_list):
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
    
    # Extract Metadata from first entry
    metadata_dict = {}
    initial_request_data_first_entry = initial_request_data["data"][0]

    for metadata_keyword in metadata_keyword_list:
        metadata_dict[metadata_keyword] = initial_request_data_first_entry[metadata_keyword]
        
    # Query all pages
    page_dictionary_list = []
    for page_number in tqdm(range(number_of_pages)):
        query_string_page="&".join([query_string,"page="+str(page_number+1)])
        page_dictionary_list.append(request_query_as_json(query_string_page))
    
    # Extract entries from the pages
    dataseries_list = []
    for page_dictionary in page_dictionary_list: 
        for datapoint in page_dictionary["data"]:
            datapoint_list = []
            for keyword in extraction_keyword_list: 
                data_tmp = datapoint[keyword]
                if data_tmp== "-":
                    data_tmp= np.nan
                datapoint_list.append(extraction_keyword_type[keyword](data_tmp))
            dataseries_list.append(datapoint_list)
    
    dataseries_df = pd.DataFrame(dataseries_list, columns = extraction_keyword_list)
    dataseries_df.attrs = metadata_dict
    return dataseries_df
    