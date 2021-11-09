import os
from src import main
import json
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":

    # Calling "python run.py 20210909" will ignore the dates from the config
    if len(sys.argv) == 2 and sys.argv[1].isnumeric() and len(sys.argv[1]) == 8:
        DATES = [sys.argv[1]]
    else:
        with open(f"{PROJECT_DIR}/config.json", "r") as f:
            DATES = json.load(f)["dates"]

    for date_string in DATES:
        main.run(date_string)
