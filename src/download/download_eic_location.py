    """
    """


import sys
import os
import requests
from pathlib import Path
import pandas as pd



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

if __name__=='__main__':
    file_facility_queries = os.path.join(config.DATA_AGSI_DIR,"Query_listing.json")

    data = pd.read_json(file_facility_queries)

    location_name_list = []
    location_coordinates_list = []

    for name in data["name"]:    
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
            location_coordinates = "NA"

        location_name_list.append(location_name)
        location_coordinates_list.append(location_coordinates)

    data["location_name"] = location_name_list
    data["location_coordinates"] = location_coordinates_list 
    data.to_json(file_facility_queries)
