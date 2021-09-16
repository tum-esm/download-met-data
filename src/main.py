import os
import subprocess

"""
Resources:
https://www.arl.noaa.gov/wp_arl/wp-content/uploads/documents/activity/quarterly/FY17_04.pdf

ecCodes: https://confluence.ecmwf.int/display/ECC
"""


project_dir = "/".join(__file__.split("/")[:-2])
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

    for year in dates.keys():
        for month in dates[year].keys():
            for day in dates[year][month]:
                subprocess.run(
                    [
                        "python3.9",
                        f"{project_dir}/src/helpers/get_era5_cds.py",
                        "--3d",
                        "-y",
                        f"{year}",
                        "-m",
                        f"{month}",
                        "-d",
                        f"{day}",
                        "--dir",
                        f"{project_dir}/data/grib",
                        "-g",
                        "--area",
                        f"{area['north']}/{area['west']}/{area['south']}/{area['east']}",
                    ]
                )

                assert "new_era52arl.cfg" in os.listdir(".")
                os.rename("new_era52arl.cfg", f"{project_dir}/data/era52arl.cfg")

                file_prefix = f"ERA5_{year}.{months[month-1]}{str(day).zfill(2)}"
                path_to_3dpl = f"{project_dir}/data/grib/{file_prefix}.3dpl.grib"
                path_to_2dpl = f"{project_dir}/data/grib/{file_prefix}.2dpl.all.grib"
                assert os.path.isfile(path_to_3dpl)
                assert os.path.isfile(path_to_2dpl)
                subprocess.run(
                    [
                        f"{era52arl_dir}/era52arl",
                        "-i",
                        path_to_3dpl,
                        "-a",
                        path_to_2dpl,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                ymd_label = f"{year}{str(month).zfill(2)}{str(day).zfill(2)}"
                os.rename(
                    "DATA.ARL",
                    f"{project_dir}/data/arl/ERA5_{ymd_label}.ARL",
                )
