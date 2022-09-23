import os
from pathlib import Path


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DATA_AGSI_DIR = os.path.join(DATA_DIR, "agsi")

SQL_DATABASE_FILE= os.path.join(DATA_DIR,"data.db")

SRC_DIR = os.path.join(ROOT_DIR,"src")

AGSI_METADATA_KEYWORD_LIST = ["name","injectionCapacity","withdrawalCapacity"]
AGSI_METADATA_KEYWORD_TYPE = {"name":str, "injectionCapacity": float, "withdrawalCapacity":float}

AGSI_EXTRACTION_KEYWORD_LIST = ["gasDayStart","gasInStorage","injection","withdrawal","workingGasVolume","status","trend","full"]
AGSI_EXTRACTION_KEYWORD_TYPE = {"gasDayStart":str,"gasInStorage":float, "injection":float, "injection":float,"withdrawal":float,"workingGasVolume":float,"status":str,"trend":float,"full":float}
AGSI_EXTRACTION_KEYWORD_TYPE_SQL = {"gasDayStart":"DATE","gasInStorage":"FLOAT", "injection":"FLOAT", "injection":"FLOAT","withdrawal":"FLOAT","workingGasVolume":"FLOAT","status":"CHAR","trend":"FLOAT","full":"FLOAT"}

AGSI_API_STRING= "https://agsi.gie.eu/api?"
GOOGLE_API_STRING="https://maps.googleapis.com/maps/api/place/textsearch/json?"


if __name__ == '__main__':
    print("ROOT_DIR:")
    print(ROOT_DIR)