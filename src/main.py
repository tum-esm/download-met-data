import os
import subprocess
import shutil
import json

"""
Resources:
https://www.arl.noaa.gov/wp_arl/wp-content/uploads/documents/activity/quarterly/FY17_04.pdf

ecCodes: https://confluence.ecmwf.int/display/ECC
"""


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def remove_tmp_files():
    for tmp_file in [
        "arldata.cfg",
        "era52arl.cfg",
        "ERA52ARL.MESSAGE",
        "get_era5_message.txt",
    ]:
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)


def run(date_string):

    with open(f"{PROJECT_DIR}/config.json", "r") as f:
        config = json.load(f)
        ERA52ARL = config["era52arl"]
        AREA = config["area"]
        DST = config["dst"]

    area_string = f"{AREA['north']}/{AREA['west']}/{AREA['south']}/{AREA['east']}"
    cache_dir = f"{PROJECT_DIR}/cache/{area_string.replace('/', '-')}"
    data_dir = DST
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)
        os.mkdir(cache_dir + "/grib")
        os.mkdir(cache_dir + "/arl")
    for appendix in ["", "/grib", "/arl"]:
        assert os.path.isdir(cache_dir + appendix)
        assert os.path.isdir(data_dir + appendix)

    year, month, day = int(date_string[:4]), int(date_string[4:6]), int(date_string[6:])
    file_prefix = f"ERA5_{year}.{months[int(month)-1]}{str(day).zfill(2)}"
    models = {
        "3d": f"{file_prefix}.3dpl.grib",
        "2da": f"{file_prefix}.2dpl.all.grib",
    }

    arl_filename = f"ERA5.{date_string}.ARL"
    arl_out_file = f"{data_dir}/arl/{arl_filename}"
    arl_cache_file = f"{cache_dir}/arl/{arl_filename}"

    if os.path.isfile(arl_cache_file):
        print(f"{date_string} - using cached arl")
        shutil.copy(arl_cache_file, arl_out_file)
        return

    for model in models:
        grib_out_file = f"{data_dir}/grib/{models[model]}"
        grib_cache_file = f"{cache_dir}/grib/{models[model]}"
        grib_out_cfg = f"era52arl.cfg"
        grib_cache_cfg = f"{cache_dir}/era52arl.cfg"

        if os.path.isfile(grib_cache_file) and os.path.isfile(grib_cache_cfg):
            print(f"{date_string} - using cached grib ({model})")
            shutil.copy(grib_cache_file, grib_out_file)
            shutil.copy(grib_cache_cfg, grib_out_cfg)
        else:
            print(f"{date_string} - computing grib ({model})")
            subprocess.run(
                [
                    f"{PROJECT_DIR}/.venv/bin/python",
                    f"{PROJECT_DIR}/src/helpers/get_era5_cds.py",
                    f"--{model}",
                    "-y",
                    f"{year}",
                    "-m",
                    f"{month}",
                    "-d",
                    f"{day}",
                    "--dir",
                    f"{data_dir}/grib",
                    "-g",
                    "--area",
                    area_string,
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            if not os.path.isfile(grib_out_file):
                print(f"{date_string} - data not available")
                remove_tmp_files()
                return

            shutil.copy(grib_out_file, grib_cache_file)
            assert "new_era52arl.cfg" in os.listdir(".")
            os.rename("new_era52arl.cfg", grib_out_cfg)
            shutil.copy(grib_out_cfg, grib_cache_cfg)

    # if arl is not in cache -> run era52arl
    if not os.path.isfile(arl_cache_file):
        print(f"{date_string} - computing arl")
        subprocess.run(
            [
                ERA52ARL,
                f"-i{data_dir}/grib/{models['3d']}",
                f"-a{data_dir}/grib/{models['2da']}",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        os.rename("DATA.ARL", arl_out_file)
        shutil.copy(arl_out_file, arl_cache_file)

        if os.path.isfile(arl_out_file):
            print(f"{date_string} - finished")
        else:
            print(f"{date_string} - era52arl execution failed")

    remove_tmp_files()
