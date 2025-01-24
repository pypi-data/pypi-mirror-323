#!/usr/bin/env python
# coding: utf-8

# This notebook demostrates the work flow of producing S1 snow depth and comparing them with the SNOTEL observations. S1 snow depth is calculated by spicy-snow package [https://github.com/SnowEx/spicy-snow] SNOTEL data are obtained from the [https://wcc.sc.egov.usda.gov/reportGenerator/].

# The work flow have three steps. 1. download SNOTEL data, 2. produce S1 snow depth data, 3. calculate the statistic, 4. display the comparison results.

# # 0. prepare jupyter notebook running environment
#    

# ## 0.1 Download the asf-snow package and create the asf-snow conda environment

# %%bash
# 
# git clone https://github.com/asfadmin/asf-snow.git
# 
# cd asf-snow
# 
# mamba env create -f environment.yml
# 
# conda activate asf-snow
# 
# python -m pip install -e .
# 
# conda deactivate

# ## 0.2 Start your jupyter notebook and run it

# start jupyter notebook service by command "jupyter notebook"
# click "Kernel" item in the menu, choose "asf-snow-kernel"

# In[43]:


from asf_snow.utils.snotel import download_snotel

from asf_snow.sentinel1_snow import *

from asf_snow.utils.analyze_sentinel1_snow import bbox_via_point

from asf_snow.utils.s1_snotel_corr_ts import *


# # 1. Downalod the SNOTEL data
# Input work directory, SNOTEL site, and date range, output snotel geodatafram and save it to snotelfile

# In[44]:


envt = {"workdir":'/media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731',
                "snotelsite": "1302:AK:SNTL",
                "daterange": ['2023-08-01', '2024-07-31']
              }

site_and_range = f'{envt['snotelsite'].replace(":","_")}_{envt['daterange'][0].replace("-","")}_{envt['daterange'][1].replace("-","")}.geojson'

snotelfile = Path.joinpath(Path(envt['workdir']), site_and_range)

snotelfile, snotel = download_snotel(snotelsite=envt['snotelsite'], stdate=envt['daterange'][0], eddate=envt['daterange'][1], snotelfile=snotelfile)


# # 2. Produce S1 snow Depth
# input username, password, flightdir, jobname, existjobname

# ## 2.1 Calulate the square centered at SNOTEL site
# input resolution, output bbox

# In[45]:


envt['snotelres'] = 10000.0  #unit meter

sitelon = float(snotel.iloc[0]['geometry'].x)
sitelat = float(snotel.iloc[0]['geometry'].y)
bbox = bbox_via_point(sitelon, sitelat, envt['snotelres'])


# ## 2.2 Define the input for producing S1 snow depth
# inputs: usename, password, jobname, existjobname for creating hyp3 RTC product, flight direction to choose for calculateing the snow depth.  

# In[46]:


envt['flightdir'] ='descending' # one of ascending, descending, both
envt['jobname'] ='jz_creamers_20230801_20240731_10k'
envt['existjobname'] = 'jz_creamers_20230801_20240731_10k'
envt['parameterabc'] = [2.5, 0.2, 0.55]
envt['wet_snow_thresh'] = -3.0
username='cirrusasf'
password='Cumulus*189Jzhu!'


# ## 2.3 Run process to get the S1 snow depth

# In[47]:


site_and_range = f'{envt['flightdir']}/sentinel1_{envt['snotelsite'].replace(":","_")}_{int(envt['snotelres'])}_{envt['daterange'][0].replace("-","")}_{envt['daterange'][1].replace("-","")}_{envt['flightdir']}.nc'

nc_file = Path(envt['workdir']).joinpath(site_and_range)

nc_file.parent.mkdir(parents=True, exist_ok=True)

envt_jsonfile = f'{envt['workdir']}/tmp/environment.json'

if not os.path.exists(envt_jsonfile):
    envt['step'] = 'begin'
    envt['area'] = bbox
    os.environ['ENVIRONMENT'] = json.dumps(envt)

else:
    envt = utils.read_environment(envt_jsonfile)
    os.environ['ENVIRONMENT'] = json.dumps(envt)

# set environment for share
if  username and password:
    os.environ['EARTHDATA_USERNAME'] = username
    os.environ['EARTHDATA_PASSWORD'] = password

# nc_ds = sentinel1_snow(area=bbox, dates=args.daterange, flightdir=args.flightdir, workdir=args.workdir,
#           jobname=args.jobname, existjobname=args.existjobname, outnc=nc_file,
#           parameterabc=args.parameterabc, wet_snow_thresh=args.wet_snow_thresh)


# In[48]:


if not Path(nc_file).exists():
    nc_ds = sentinel1_snow(area=bbox, dates=envt['daterange'], flightdir=envt['flightdir'], workdir=envt['workdir'],
           jobname=envt['jobname'], existjobname=envt['existjobname'], outnc=nc_file,
           parameterabc=envt['parameterabc'], wet_snow_thresh=envt['wet_snow_thresh'])
else:
    # to_netcdf and read it back, the coords variables change, and crs is missing, need to restore them back
    nc_ds = xr.open_dataset(nc_file)

# set crs to nc_ds as needed
try:
    crs = nc_ds.rio.crs
except:
    try:
        nc_ds = nc_ds.set_coords(("spatial_ref","projection"))
        nc_ds.rio.write_crs('epsg:4326', inplace=True)
    except:
        pass


# In[49]:


# add some attrs to the xarray.dataset
nc_ds.attrs['sitelon'] = sitelon
nc_ds.attrs['sitelat'] = sitelat
nc_ds.attrs['orbit'] = 'all'


# In[50]:


# write the bounds of nc_ds into geojson file
s1_poly = bbox2polygon(list(nc_ds.snow_depth.rio.bounds()))
geojson_file = str(nc_file).replace(".nc", ".geojson")
write_polygon(s1_poly, geojson_file)


# In[51]:


geojson_file = str(nc_file).replace(".nc", ".geojson")


# # 3. Compare S1 snow depth with SNOTEL data

# ## 3.1 Inputs for the correlation
# inputs: 
# The longitude and latitude of the pixel of interest (POI) that you want to investigate,
# avg (True/False) determines if you want to compare the average of pixles within the square centered at the POI or the POI with SNOTEL data,
# res is the length of square in meter.

# In[52]:


poi = {'pixel1': [-147.7681, 64.8541]}
envt['avg']=True
envt['res']=1000.0


# ## 3.2 Obtain the shapefile of the sqaure and clip the S1 data

# In[53]:


geojson_file_pixel = geojson_file.replace(".geojson", f'_{list(poi.keys())[0]}.geojson')

if envt['avg'] and envt['res']:
    poly = polygon_via_point(lon=poi['pixel1'][0], lat=poi['pixel1'][1], resolution=envt['res'])
    jsstr = to_geojson(poly)
    geometries = [json.loads(jsstr)]
    nc_ds_pixel = nc_ds.rio.clip(geometries, all_touched=True)
    
    # write boundary as polygon
    s1_poly_clipped = bbox2polygon(list(nc_ds_pixel.snow_depth.rio.bounds()))
    
    write_polygon(s1_poly_clipped, geojson_file_pixel)
else:
    nc_ds_pixel = nc_ds.copy(deep=True)

nc_ds_pixel.attrs['lon'] = poi['pixel1'][0]
nc_ds_pixel.attrs['lat'] = poi['pixel1'][1]
nc_ds_pixel.attrs['poi'] = list(poi.keys())[0]


# ### Calculate the R, MEAN, and STD

# In[54]:


# Get x and y of poi in the clipped S1 data
gt = get_gt(nc_ds_pixel)
x, y = lonlat_to_colrow(gt, poi['pixel1'][0], poi['pixel1'][1])

# Calculate the R, mean, ans std within the time range from st_mmdd to ed_mmdd
snowcover = calc_s1_snotel_correlation(nc_ds_pixel, snotel, st_mmdd='11-01', ed_mmdd='04-01')

# save the clipped S1 data with statistic associated
outfile = geojson_file_pixel.replace(".geojson", ".nc")
write_to_netcdf(snowcover, outfile)


# # 4. Display the comparison

# In[55]:


pngfile = geojson_file_pixel.replace(".geojson", ".png")
draw_lines(nc_ds_pixel, snotel, outfile=pngfile, y=y, x=x, average=envt['avg'], res=envt['res'])


# In[ ]:


print('completed...')

