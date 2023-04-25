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
conf_dir = os.path.join(root_dir,"config")


from tqdm import tqdm

sys.path.append(str(conf_dir))

import config
import keys

sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi
import database as database

sql_database_file = config.SQL_DATABASE_FILE


if __name__ == '__main__':
    engine = create_engine("sqlite:///{}".format(sql_database_file))
    Session = sessionmaker(bind=engine)
    session = Session()

    facilities = session.query(database.Facility).all()
    
    for facility_dict in facilities:
        agsi.update_facility_storage(session, facility_dict)
    
