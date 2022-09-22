import sys
import os
import json
from pathlib import Path
import sqlite3

root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config
import keys

sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi

sql_database_file = config.SQL_DATABASE_FILE
conn = sqlite3.connect(sql_database_file)
conn_cursor = conn.cursor()



if __name__ == '__main__':
    query_string_eic_listing = "https://agsi.gie.eu/api/about"

    file_eic_listing = os.path.join(config.DATA_AGSI_DIR, "EIC_listing.json")
    data_eic_listing = agsi.request_query_as_json(query_string_eic_listing, api_key=keys.AGSI)

    with open(file_eic_listing , 'w') as file:
        json.dump(data_eic_listing, file)

    facility_query_parameter_df = agsi.generate_query_string_list(data_eic_listing, api_string=config.AGSI_API_STRING)
    
    file_facility_queries = os.path.join(config.DATA_AGSI_DIR,"Query_listing.json")
    
    #facility_query_parameter_df.to_json(file_facility_queries)
    facility_query_parameter_df.to_sql("eic_listing",con=conn)


