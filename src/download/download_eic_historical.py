import sys
import os
import json
from pathlib import Path

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

if __name__ == '__main__':
    file_eic_listing = os.path.join(config.DATA_AGSI_DIR, "EIC_listing.json")

    with open(file_eic_listing , 'r') as file:
        data_eic_listing = json.load(file)

    facility_query_string_list = agsi.generate_query_string_list(data_eic_listing, api_string=api_string)

    for facility_query_string in facility_query_string_list:
        facility_dict = agsi.decompose_query_string(facility_query_string)
        facility_filename = "_".join([facility_dict["country"], facility_dict["company"], facility_dict["facility"]])+".json"
        facility_file = os.path.join(config.DATA_AGSI_DIR,facility_filename)

        print("Downloading Historical Data for "+str(facility_filename)+" :")

        facility_dataseries = agsi.curl_data_from_query(facility_query_string, extraction_keyword_list, metadata_keyword_list)
        facility_dataseries.to_json(facility_file)
