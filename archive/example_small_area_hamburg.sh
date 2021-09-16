#!/bin/sh
# Example bash script for retrieving ERA5 for a small area.
# Author: Alice Crawford   Organization: NOAA/OAR/ARL 

# Example for downloading and converting ERA5 data on pressure levels
# for a relatively small area.

# read the simulation date
year=2021
month=9
day=$(seq 9 12)
#day=31
#year=$(awk -F\/ '{print $3}' Date.dat)
#month=$(awk -F\/ '{print $1}' Dte.dat)
#day=$(awk -F\/ '{print $2}' Date.dat)

#Location of get_era5_cds.py
PDL="/Users/dostuffthatmatters/Documents/work/bachelor-thesis/download-cds-data/archive"

#small area to retrieve
# upper left lat/ upper left lon / lower right lat / lower right lon
# NORTH/WEST/SOUTH/EAST
area="60/00/40/20"

#directory to write files to
#outdir_nc='/home/xinxu/dss/ERA5/nc/'
outdir_arl='/Users/dostuffthatmatters/Documents/work/bachelor-thesis/download-cds-data/data/arl/'
outdir_gb='/Users/dostuffthatmatters/Documents/work/bachelor-thesis/download-cds-data/data/grib/'

for line in $day
do
	yy=$year
	echo "year=$yy"
	mm=$month
	echo "month=$mm"
	dd=$line
  echo "RETRIEVING year $yy month $mm day $dd"

	# Grib file download
  # retrieves pressure level files
  python3.9 ${PDL}/get_era5_cds.py --3d -y $yy -m $mm -d $dd --dir $outdir_gb -g --area $area
  # retrieves surface data files with all variables
  python3.9 ${PDL}/get_era5_cds.py --2da -y $yy -m $mm -d $dd --dir $outdir_gb -g --area $area

done
# use the cfg file created for the conversion.
mv new_era52arl.cfg era52arl.cfg

#-----------------------------------------
# convert data to ARL format

# In practice you may want to run the following 
# in a separate script, after you have confirmed that
# all the data downloaded properly.
#-----------------------------------------

MDL=/usr/local/hysplit/data2arl/era52arl
limit=10

for line in $day
do

	echo "line=$line"
	yy=$year
	echo "year=$yy"


	mm=$month
	echo "month=$mm"

	month_name=$(awk -F\/ '{print $1}' month_name.dat)
	mm_month=$(echo $month_name | awk '{print $(echo '$mm')}'| sed -n '1p')

	if  [ "$mm" -lt "$limit" ]; then
	    mm_m=$(printf "%01d"$(echo $mm))
	else
	    mm_m=$(echo $mm)
	fi


	dd=$line
	echo "day=$dd"

	if  [ "$dd" -lt "$limit" ]; then
	    dd_day=$(printf "%01d"$(echo $dd))
	else
	    dd_day=$(echo $dd)
	fi

  echo "Converting year $yy month $mm_month day $dd_day"


	echo '---------------------------------------------------------------------------------'
  echo $MDL/era52arl -i${outdir_gb}ERA5_${yy}.${mm_month}${dd_day}.3dpl.grib -a${outdir_gb}ERA5_${yy}.${mm_month}${dd_day}.2dpl.all.grib
  $MDL/era52arl -i${outdir_gb}ERA5_${yy}.${mm_month}${dd_day}.3dpl.grib -a${outdir_gb}ERA5_${yy}.${mm_month}${dd_day}.2dpl.all.grib
  mv $PDL/DATA.ARL ${outdir_arl}ERA5_${yy}${mm_m}${dd_day}.ARL
  echo 'DONE ---------------------------------------------------------------------------------'

done

