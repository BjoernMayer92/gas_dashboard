import os
from pathlib import Path


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DATA_AGSI_DIR = os.path.join(DATA_DIR, "agsi")

SRC_DIR = os.path.join(ROOT_DIR,"src")

AGSI_METADATA_KEYWORD_LIST = ["name","url","injectionCapacity","withdrawalCapacity"]
AGSI_EXTRACTION_KEYWORD_LIST = ["gasDayStart","gasInStorage","injection","withdrawal","workingGasVolume","status","trend","full"]
AGSI_API_STRING= "https://agsi.gie.eu/api?"

if __name__ == '__main__':
    print("ROOT_DIR:")
    print(ROOT_DIR)