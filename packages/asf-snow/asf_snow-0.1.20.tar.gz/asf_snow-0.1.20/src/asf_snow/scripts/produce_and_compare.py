# produce 202011 to 202104 statistic with different zonal, time range, time close, precipitation, and method conditions,
# and compare it with NASA snowEx observation data.

import os

from asf_snow.utils.combine_multiple_statistic_results import combine_multiple_statistic_results

from asf_snow.utils.compare_sentinel1_snow_depth_to_snex import *

from asf_snow.utils.analyze_sentinel1_snow import draw_combined_gdf, draw_scatter_plot

os.chdir('/home/jiangzhu/projects/work/crrel/asf-snow/src/asf_snow/utils')

varname = 'snow_depth'
location = 'Boise'
res = 500
timeint = 36
timethresh = 6
base = 'snex'
method = "close"
precip = 'y'
snexfile = '/home/jiangzhu/data/crrel/snowEx21_ts_snow_pits_v1/SNEX21_TS_SP_Summary_SWE_v01.csv'

ncfilelst = [
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20201101_1130/sentinel1_20201101_1130.nc',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20201201_1231/sentinel1_20201201_1231.nc',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210101_0131/sentinel1_20210101_0131.nc',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210201_0228/sentinel1_20210201_0228.nc',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210301_0331/sentinel1_20210301_0331.nc',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210401_0430/sentinel1_20210401_0430.nc',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210501_0531/sentinel1_20210501_0531.nc',
]

# list of the statistic file for every month
outfilelst = []

for ncfile in ncfilelst:

    file = compare_sentinel1_snow_depth_to_snex(ncfile, varname, snexfile, location, res, timeint,
                                                timethresh, base, method, precip)
    outfilelst.append(file)

# write the outfilelst

out_dir = str(Path(file).parent.parent)

affix = f'_{int(res)}_{timeint}h_{timethresh}h_{base}_{method}_{precip}'

outfilelist = f'{out_dir}/boise_202011_202104{affix}.txt'

with open(outfilelist, 'w') as f:
    for line in outfilelst:
        f.write(f"{line}\n")

# combine the statistic files in the outfilelst

combined = combine_multiple_statistic_results(outfilelst)

# draw combined

outgeojson = f'{out_dir}/sentinel1_202011_202104_{res}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_boise_river_basin.geojson'

outpngfile = f'{out_dir}/sentinel1_202011_202104_{res}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_boise_river_basin.png'

if combined is not None:

    if not combined.empty:

        combined.to_file(outgeojson, driver='GeoJSON')

        draw_combined_gdf(combined, res=res, timeint=timeint, timethresh=timethresh, base=base, method=method,
                          outfile=outpngfile, precip=precip)

print("completed ...")
