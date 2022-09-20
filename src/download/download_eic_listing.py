import sys
import os
import json
from pathlib import Path

root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config
import keys

sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi

if __name__ == '__main__':
    query_string_eic_listing = "https://agsi.gie.eu/api/about"

    file_eic_listing = os.path.join(config.DATA_AGSI_DIR, "EIC_listing.json")
    data_eic_listing = agsi.request_query_as_json(query_string_eic_listing, api_key=keys.AGSI)

    with open(file_eic_listing , 'w') as file:
        json.dump(data_eic_listing, file)