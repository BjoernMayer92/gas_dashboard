import sys
import os
import pandas as pd
from pathlib import Path

root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config

extraction_keyword_list = config.AGSI_EXTRACTION_KEYWORD_LIST
metadata_keyword_list = config.AGSI_METADATA_KEYWORD_LIST
api_string = config.AGSI_API_STRING
sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi

if __name__ == '__main__':
    file_facility_queries = os.path.join(config.DATA_AGSI_DIR,"Query_listing.json")
    facility_queries = pd.read_json(file_facility_queries)

    for facility_query_string in facility_queries["query_string"]:
        facility_dict = agsi.decompose_query_string(facility_query_string)
        facility_filename = "_".join([facility_dict["country"], facility_dict["company"], facility_dict["facility"]])+".json"
        facility_file = os.path.join(config.DATA_AGSI_DIR,facility_filename)

        print("Downloading Historical Data for "+str(facility_filename)+" :")
        
        facility_dataseries = agsi.curl_data_from_query(facility_query_string, extraction_keyword_list, metadata_keyword_list)
        facility_dataseries.to_json(facility_file)
