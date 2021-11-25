# Download ERA5 Data and convert the GRIB to ARL files

## What is it?

This tool downloads weather data from the ERA5 dataset (https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) from CDS (https://cds.climate.copernicus.eu/) and converts the `GRIB` files to `ARL` files using the `era52arl` tool, which is part of HYSPLIT (https://www.arl.noaa.gov/hysplit-2/).

<br/>
<br/>

## How to set it up?

Dependency management with poetry: https://python-poetry.org/docs/#installation

Set up the project interpreter:

```bash
# Create virtual environment (a local copy of python)
python3.9 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
poetry install
```

<br/>
<br/>

## How to run it?

1. Use the file `config.example.json` to create a `config.json` file in your project directory for your setup

2. Run the script
   
   1.  Either use the dates specified in `config.json` ...
        ```bash
        python3.9 run.py
        ```

   2.  ... or pass the date to use to the program as an inline parameter:
        ```bash
        python3.9 run.py 20211016
        ```


<br/>

**Request will be cached** in the `cache/` directory. Please do not remove or empty this directory.
