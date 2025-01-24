import shapely
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxa
from rasterio.enums import Resampling

from datetime import datetime

from asf_analysis.s1_lidar.download_lidar import download_lidar_data

from asf_analysis.s1_lidar.make_spicy_ds import make_site_ds

from asf_analysis.s1_lidar.rmse_table import stats_table_new, stats_table_old


# 1. download the Lidar data

lidar_dir = Path('/home/jiangzhu/data/crrel/lidar2')

# lidar_dir.mkdir(parents=True, exist_ok = True)

scratch_dir = Path.joinpath(lidar_dir,"scratch")

scratch_dir.mkdir(parents=True, exist_ok=True)

# check if there are *_DEM_*, "*_VH_*, and *_SD_* files

lst1 = [f for f in lidar_dir.glob('*_DEM_*')]
lst2 = [f for f in lidar_dir.glob('*_SD_*')]
lst3 = [f for f in lidar_dir.glob('*_VH_*')]

if  len(lst1) == 0 or len(lst2) == 0 or len(lst3) == 0:
    download_lidar_data(lidar_dir)

# 2. construct the lidar ds

lidar_file = f'{lidar_dir}/lidar_ds_site.nc'

sites = {'USIDBS': 'Banner'}

site = 'USIDBS'

site_name = 'Banner'

filename_filter = '*20200218_20200219*'

if Path(lidar_file).is_file():
    lidar_ds = xr.load_dataset(lidar_file, decode_coords="all")
else:
    for site, site_name in sites.items():
        lidar_ds = make_site_ds(site, lidar_dir, filename_filter=filename_filter)
        lidar_ds.to_netcdf(lidar_file)

# cut off no-sense data

#lidar_ds = lidar_ds.where(lidar_ds < 1e9).where(lidar_ds >= 0) # not work, killed

ch = np.logical_and(lidar_ds < 1e9, lidar_ds >= 0)
lidar_ds['lidar-sd'] = lidar_ds['lidar-sd'].where(ch['lidar-sd'])
lidar_ds['lidar-vh'] = lidar_ds['lidar-vh'].where(ch['lidar-vh'])
lidar_ds['lidar-dem'] = lidar_ds['lidar-dem'].where(ch['lidar-dem'])
lidar_ds.to_netcdf(f'{lidar_dir}/lidar_ds_site_validdata.nc')

# 3. read in teh s1 data

s1file = f'{str(lidar_dir)}/spicy_ds.nc'

s1_ds = xr.load_dataset(s1file, decode_coords="all")

# 4. resample lidar ds based on S1 ds

# set nodata as np.nan
for var in lidar_ds:
    lidar_ds[var] = lidar_ds[var].rio.write_nodata(np.nan)

# resample lidar based on s1 data
lidar_ds = lidar_ds.rio.reproject_match(s1_ds, resampling = Resampling.average, nodata=np.nan)

# merge lidar to s1
# ds = ds[['lidar-sd', 'lidar-vh', 'lidar-dem', 'snow_depth', 's1', 'wet_snow']]
ds = xr.merge([s1_ds, lidar_ds], combine_attrs = 'drop_conflicts')

# add attributes to combined data
date = lidar_ds.time

ds.attrs['site'] = site_name
ds.attrs['site_abbrev'] = site
ds.attrs['lidar-flight-time'] = str(date[0].dt.strftime("%Y-%m-%d").values)
ds.attrs['processing-date'] = f'{datetime.now()}'

# output the combined data
out_nc = f'{str(scratch_dir)}/s1_lidar.nc'
try:
    ds.to_netcdf(out_nc)
except:
    print('Unable to create netcdf4 for {site_name}')

# call Zach's calculate functions

cvsfile_new = Path(f'{str(lidar_dir)}/stats_table_new.csv')

stats_table_new(scratch_dir, cvsfile_new)

cvsfile_old = Path(f'{str(lidar_dir)}/stats_table_new.csv')

stats_table_old(scratch_dir, cvsfile_old)

print('completed ...')





