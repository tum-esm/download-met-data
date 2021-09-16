import os
import subprocess
import shutil

"""
Resources:
https://www.arl.noaa.gov/wp_arl/wp-content/uploads/documents/activity/quarterly/FY17_04.pdf

ecCodes: https://confluence.ecmwf.int/display/ECC
"""


project_dir = "/".join(__file__.split("/")[:-2])
data_dir = f"{project_dir}/data"
era52arl_dir = "/usr/local/hysplit/data2arl/era52arl"
dates = {2021: {9: [10, 11]}}
area = {
    "north": 60,
    "south": 40,
    "east": 20,
    "west": 0,
}


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


def run():

    area_string = f"{area['north']}/{area['west']}/{area['south']}/{area['east']}"
    cache_dir = f"{project_dir}/cache/{area_string.replace('/', '-')}"
    cache_exists = os.path.isdir(cache_dir)
    if not cache_exists:
        os.makedir(cache_dir)
        os.makedir(f"{cache_dir}/grib")
        os.makedir(f"{cache_dir}/arl")

    for year in dates.keys():
        for month in dates[year].keys():
            for day in dates[year][month]:
                ymd_string = f"{year}{str(month).zfill(2)}{str(day).zfill(2)}"

                file_prefix = f"ERA5_{year}.{months[month-1]}{str(day).zfill(2)}"
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
                        print(f"{ymd_string} - using cached grib ({model})")
                        shutil.copy(cache_file, out_file)
                        shutil.copy(cache_cfg, out_cfg)
                    else:
                        print(f"{ymd_string} - computing grib ({model})")
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
                        assert os.path.isfile(out_file)
                        shutil.copy(out_file, cache_file)

                        assert "new_era52arl.cfg" in os.listdir(".")
                        os.rename("new_era52arl.cfg", out_cfg)
                        shutil.copy(out_cfg, cache_cfg)

                filename = f"ERA5_{ymd_string}.ARL"
                out_file = f"{data_dir}/arl/{filename}"
                cache_file = f"{cache_dir}/arl/{filename}"

                if os.path.isfile(cache_file):
                    print(f"{ymd_string} - using cached arl")
                    shutil.copy(cache_file, out_file)
                else:
                    print(f"{ymd_string} - computing arl")
                    subprocess.run(
                        [
                            f"{era52arl_dir}/era52arl",
                            f"-i{data_dir}/grib/{models['3d']}",
                            f"-a{data_dir}/grib/{models['2da']}",
                        ],
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                    )
                    os.rename("DATA.ARL", out_file)
                    shutil.copy(out_file, cache_file)

    for tmp_file in ["arldata.cfg", "era52arl.cfg", "ERA52ARL.MESSAGE"]:
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)
