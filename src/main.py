import os
import subprocess
import shutil
import json

"""
Resources:
https://www.arl.noaa.gov/wp_arl/wp-content/uploads/documents/activity/quarterly/FY17_04.pdf

ecCodes: https://confluence.ecmwf.int/display/ECC
"""


project_dir = "/".join(__file__.split("/")[:-2])


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

    with open(f"{project_dir}/config.json", "r") as f:
        config = json.load(f)
        ERA52ARL = config["era52arl"]
        AREA = config["area"]
        DST = config["dst"]

    area_string = f"{AREA['north']}/{AREA['west']}/{AREA['south']}/{AREA['east']}"
    cache_dir = f"{project_dir}/cache/{area_string.replace('/', '-')}"
    cache_exists = os.path.isdir(cache_dir)
    data_dir = DST
    for appendix in ["", "/grib", "/arl"]:
        assert os.path.isdir(cache_exists + appendix)
        assert os.path.isdir(data_dir + appendix)

    year, month, day = int(date_string[:4]), int(date_string[4:6]), int(date_string[6:])
    file_prefix = f"ERA5_{year}.{months[int(month)-1]}{str(day).zfill(2)}"
    models = {
        "3d": f"{file_prefix}.3dpl.grib",
        "2da": f"{file_prefix}.2dpl.all.grib",
    }

    for model in models:
        out_file = f"{data_dir}/grib/{models[model]}"
        cache_file = f"{cache_dir}/grib/{models[model]}"
        out_cfg = f"era52arl.cfg"
        cache_cfg = f"{cache_dir}/era52arl.cfg"

        if os.path.isfile(cache_file) and os.path.isfile(cache_cfg):
            print(f"{date_string} - using cached grib ({model})")
            shutil.copy(cache_file, out_file)
            shutil.copy(cache_cfg, out_cfg)
        else:
            print(f"{date_string} - computing grib ({model})")
            subprocess.run(
                [
                    "python3.9",
                    f"{project_dir}/src/helpers/get_era5_cds.py",
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
            if not os.path.isfile(out_file):
                print(f"{date_string} - data not available")
                remove_tmp_files()
                return

            shutil.copy(out_file, cache_file)
            assert "new_era52arl.cfg" in os.listdir(".")
            os.rename("new_era52arl.cfg", out_cfg)
            shutil.copy(out_cfg, cache_cfg)

    filename = f"ERA5.{date_string}.ARL"
    out_file = f"{data_dir}/arl/{filename}"
    cache_file = f"{cache_dir}/arl/{filename}"

    if os.path.isfile(cache_file):
        print(f"{date_string} - using cached arl")
        shutil.copy(cache_file, out_file)
    else:
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
        os.rename("DATA.ARL", out_file)
        shutil.copy(out_file, cache_file)

    if os.path.isfile(out_file):
        print(f"{date_string} - finished")
    else:
        print(f"{date_string} - era52arl execution failed")
    remove_tmp_files()
