import os
from pathlib import Path


ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DATA_AGSI_DIR = os.path.join(DATA_DIR, "agsi")

if __name__ == '__main__':
    print("ROOT_DIR:")
    print(ROOT_DIR)