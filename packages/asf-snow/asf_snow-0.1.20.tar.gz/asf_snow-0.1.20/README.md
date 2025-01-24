# asf-snow
Evaluation of Snow depths for the CRREL Arctic Trafficability with the spicy-snow python module (https://github.com/SnowEx/spicy-snow). The spicy-snow uses volumetric scattering at C-band to calculate snow depths from Sentinel-1 imagery using Lieven et al.'s 2021 technique.



List of Programs

sentinel1_snow.py, produces Sentinel1-derived snow depth product according to the spatial area and time range

compare_sentinel1_snow_depth_to_snex.py, calculate the statistic of sentinel1 and SNEX snow depth data

analyze_snex.py, includes codes to read different kinds of SNEX csv files

analyze_sentinel1_snow.py, include all kinds of draw plot functions

combine_multiple_statistic_results.py, combine multiple monthly statistic files, and draw the histogram plot



compare_sentinel1_snow_depth_to_snex_lidar.py, calculate the statistic of sentinel1 and Lidar snow depth data, and draw the scatter plot


compare_sentinel1_snow_depth_to_snotel.py, calculate statistic of Sentinel1 and SNOTEL snow depth time series

draw_s1_snotel_plot.py, draw Sentinel1-derived snow depth and SNOTEL snow depth curves, the difference curve, and histograms of s1 and SNOTEL snow depth

investigate_s1_snotel.py, analysze S1 and SNOTEL snow depth and draw plots


Example scripts

# produce s1 snow depth product

python sentinel1_snow.py --username xxxxxxxx --password xxxxxxxx --area -147.76 64.85 -147.72 64.88 --daterange 2022-08-01 2023-07-31 --workdir /home/jiangzhu/data/crrel/SNOTEL/creamers/20220801_20230731 --jobname jz_creamers_20220801_20230731_n1 --existjobname jz_creamers_20220801_20230731_n1 --outnc /home/jiangzhu/data/crrel/SNOTEL/creamers/20220801_20230731/sentinel1_creamers_20220801_20230731.nc



# analysis the s1 and snotel data
 
investigate_s1_snotel --s1file /media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/sentinel1_creamers_20230801_20240731.nc --snotelfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/creamers_20230801_20240731_sd_precip_temp_ratio.txt --lon -147.74532 --lat 64.86575  --aoigeojsonfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/creamers.geojson --outfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/sentinel1_creamers_20230801_20240731_aoi_all_test.png

investigate_s1_snotel --s1file /media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/sentinel1_creamers_20230801_20240731.nc --snotelfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/creamers_20230801_20240731_sd_precip_temp_ratio.txt --lon -147.74532 --lat 64.86575  --res 500 --outfile /media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/sentinel1_creamers_20230801_20240731_poi_500_all_test.png


# estimate the wet snow threshold impact on wet snow mask

compare_wet_thresholds.py

