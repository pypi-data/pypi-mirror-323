#!/bin/bash

years=("2021-2022" "2022-2023" "2023-2024")

for i in ${years[*]}
do
	y1=$(echo $i | cut -f1 -d-)
	y2=$(echo $i | cut -f2 -d-)
	echo $y1 $y2
	
	echo "AOI, time range"
	echo "python -m pdb investigate_s1_snotel.py --s1file /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731.nc --snotelfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/creamers_${y1}0801_${y2}0731_sd_precip_temp_ratio.txt --lon -147.74532 --lat 64.86575  --aoigeojsonfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/creamers.geojson --stdate ${y1}-11-15 --eddate ${y2}-03-15 --outfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731_aoi_snow.png"

	
	python investigate_s1_snotel.py --s1file /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731.nc --snotelfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/creamers_${y1}0801_${y2}0731_sd_precip_temp_ratio.txt --lon -147.74532 --lat 64.86575  --aoigeojsonfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/creamers.geojson --stdate ${y1}-11-15 --eddate ${y2}-03-15 --outfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731_aoi_snow_season.png

	echo "AOI, all times"
	python investigate_s1_snotel.py --s1file /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731.nc --snotelfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/creamers_${y1}0801_${y2}0731_sd_precip_temp_ratio.txt --lon -147.74532 --lat 64.86575  --aoigeojsonfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/creamers.geojson --outfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731_aoi_all_times.png
	
	echo "POI, time range"
	python investigate_s1_snotel.py --s1file /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731.nc --snotelfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/creamers_${y1}0801_${y2}0731_sd_precip_temp_ratio.txt --lon -147.74532 --lat 64.86575  --res 500 --stdate ${y1}-11-15 --eddate ${y2}-03-15 --outfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731_poi_snow_season.png

	echo "POI, all times"
	python investigate_s1_snotel.py --s1file /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731.nc --snotelfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/creamers_${y1}0801_${y2}0731_sd_precip_temp_ratio.txt --lon -147.74532 --lat 64.86575  --res 500 --outfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/${y1}0801_${y2}0731/sentinel1_creamers_${y1}0801_${y2}0731_poi_all_times.png

done

