from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path
import xarray as xr
import rioxarray as rio
import rasterio
from folium import GeoJson
from shapely import geometry, to_geojson
import pandas as pd
import geopandas as gpd
import rasterstats as rstats
from affine import Affine
import numpy as np
import utm
from pyproj import CRS, Proj
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

#from shapely.geometry import Polygon, LineString, Point

from datetime import datetime, timedelta

import json
import matplotlib

# matplotlib.use('Agg')

import pytz
from timezonefinder import TimezoneFinder

def get_utc_offset(lon, lat):
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lng=lon, lat=lat)
    timezone = pytz.timezone(tz_str)
    return timezone

def get_utc(datetime, tz):
    return datetime + tz.utcoffset(datetime)


def get_crs(lon: float, lat: float) -> CRS:
    y, x, zone, band = utm.from_latlon(lat, lon)
    if lat < 0.0:
        south = True
    else:
        south = False

    # use PROJ string, assuming a default WGS84
    # crs = CRS.from_string(f'+proj=utm +zone=zone +south')

    # use dictionary to define the PROJ
    crs = CRS.from_dict({'proj': 'utm', 'zone': zone, 'south': south})

    return crs


def lonlat_to_xy(lon, lat, crs):
    p1 = Proj(crs, preserve_units=True)
    (y, x) = p1(lon, lat)
    return x, y


def xy_to_lonlat(x, y, crs):
    p1 = Proj(crs, preserve_units=True)
    (lon, lat) = p1(y, x, inverse=True)
    return lon, lat


def get_var(ncfile, varname):
    nc_ds = xr.open_dataset(ncfile, decode_coords="all")

    var = nc_ds[varname]

    var = var.transpose('time', 'y', 'x')

    var = var.rio.set_spatial_dims(x_dim='x', y_dim='y')

    var.attrs['affine'] = var.rio.transform()

    var.attrs['bounds'] = var.rio.bounds()

    return var

def get_ds(ncfile):
    nc_ds = xr.open_dataset(ncfile, decode_coords="all")
    nc_ds = nc_ds.transpose('time', 'y', 'x', ...)
    nc_ds = nc_ds.rio.set_spatial_dims(x_dim='x', y_dim='y')
    nc_ds.attrs['affine'] = nc_ds.snow_depth.rio.transform()
    nc_ds.attrs['bounds'] = nc_ds.snow_depth.rio.bounds()
    return nc_ds


def get_snow_depth_deltacrt(ncfile, varname):
    nc_ds = xr.open_dataset(ncfile, decode_coords="all")



def get_affine_bbox(nc_ds):
    """Get the bounding box of the nc variable
    arguments: nc dataset
    retrurns: affine
              bbox [min_lon,min_lat, max_lon, max_lat]
    """
    affine = nc_ds.rio.transform()
    bounds = nc_ds.rio.bounds()
    return affine, bounds


def bbox2polygon(bbox):
    """Convert bbox [min_lon,min_lat,max_lon, max_lat] to shapely polygon.
    arguments: bbox: [min_lon,min_lat, max_lon, max_lat], example [-113.2, 43.1, -113.1, 43.2]
    returns: polygon
    """
    p1 = geometry.Point(bbox[0], bbox[1])
    p2 = geometry.Point(bbox[2], bbox[1])
    p3 = geometry.Point(bbox[2], bbox[3])
    p4 = geometry.Point(bbox[0], bbox[3])
    pointlist = [p1, p2, p3, p4]
    poly = geometry.Polygon(pointlist)

    return poly


def write_geojson(bbox, outfile):
    poly = bbox2polygon(bbox)
    data ={"name":["The Caribou-Poker Creek and Poker Flats Research Watershed"], "geometry":[poly]}
    gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')
    gdf.to_file(outfile, driver='GeoJSON')
    return outfile

def polygon_via_point(lon: float, lat: float, resolution: float):
    crs = get_crs(lon, lat)
    y, x, zone, band = utm.from_latlon(lat, lon)

    min_x = x - resolution/2
    min_y = y - resolution/2
    max_x = x + resolution/2
    max_y = y + resolution/2

    min_lon, min_lat = xy_to_lonlat(min_x, min_y, crs)
    max_lon, max_lat = xy_to_lonlat(max_x, max_y, crs)

    bbox = [min_lon, min_lat, max_lon, max_lat]

    return bbox2polygon(bbox)

def bbox_via_point(lon: float, lat: float, resolution: float):
    crs = get_crs(lon, lat)
    y, x, zone, band = utm.from_latlon(lat, lon)

    min_x = x - resolution/2
    min_y = y - resolution/2
    max_x = x + resolution/2
    max_y = y + resolution/2

    min_lon, min_lat = xy_to_lonlat(min_x, min_y, crs)
    max_lon, max_lat = xy_to_lonlat(max_x, max_y, crs)

    bbox = [min_lon, min_lat, max_lon, max_lat]

    return bbox

def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


def zonal_analyses(nc_var, daterange: list = None, times: list = None, poly: geometry.Polygon = None):
    # load and read shp-file with geopandas
    # shp_fo = r'../path/to/shp_file.shp'

    # shp_df = gpd.read_file(str(shapefile))

    # load and read netCDF-file to dataset and get datarray for variable
    # nc_fo = r'../path/to/netCDF_file.nc'
    # nc_ds = xr.open_dataset(nc_fo)

    # nc_var = nc_var.transpose('time', 'y', 'x')

    # get affine and bbox
    affine = nc_var.attrs['affine']
    bbox = list(nc_var.attris['bounds'])

    # decide if poly is not within bbox, return None for yes
    if not bbox2polygon(bbox).contains(poly):
        return None

    # select date range
    if daterange:
        nc_var = nc_var.sel(time=slice(*daterange))

    # get all years for which we have data in nc-file
    if times:
        times = times
    else:
        times = nc_var['time'].values

    # define output list to hold calculated statistic
    output = []

    # go over each time
    for time in times:
        # get values of variable pear year
        nc_arr = nc_var.sel(time=time, method='nearest')
        nc_arr_vals = nc_arr.values
        rst = rstats.zonal_stats(poly, nc_arr_vals, affine=affine, stats="mean min max")

        output.append({'time': time, 'geometry': poly, 'stat': rst})

        print({'time': time, 'geometry': poly, 'stat': rst})

    # convert output to geoDataFrame

    parsed_output = [[item['time'], item['stat'], item['geometry']] for item in output]

    gdf = gpd.GeoDataFrame(data=parsed_output, columns=['time', 'stat', 'geometry'])

    return gdf


def close_snex_time(nc_arr, time_ct, timethresh=12):
    nc_arr_range = nc_arr.copy(deep=True)

    # select times of days close to the time of t_ct
    # if len(nc_arr.time) >= 1:
    if nc_arr.time.shape[0] == 0:
        return None
    time_arr = np.array(nc_arr.time)
    time_arr = [pd.Timestamp(time).to_pydatetime() for time in time_arr]
    num = len(time_arr)
    idx = np.zeros(num, dtype=int)
    idx[:] = -1
    for i in range(num):
        # if abs(time_ct - time_arr[i]).seconds <= timethresh * 3600:
        time_ct_second_of_day = time_ct.hour * 3600 + time_ct.minute * 60 + time_ct.second
        time_i = time_arr[i]
        time_i_second_of_day = time_i.hour * 3600 + time_i.minute * 60 + time_i.second

        if abs(time_ct_second_of_day - time_i_second_of_day) <= timethresh * 3600:
            idx[i] = i
    # eliminate the wrong index
    idx = idx[idx >= 0]
    if idx.size == 0:
        return None
    # idx is the array including the index of times we pick up in the nc_arr
    pick_times = np.array(nc_arr.time[idx.tolist()])
    pick_times = [pd.Timestamp(time).to_pydatetime() for time in pick_times]
    nc_arr = nc_arr.sel(time=pick_times)
    return nc_arr


def close_s1_time(snex, time_ct, timethresh=12):
    # snex1 = snex.copy(deep=True)
    # select times of days close to the time of t_ct
    # if len(nc_arr.time) >= 1:
    # if len(snex) == 1:
    #    return snex
    time_arr = np.array(snex['time'])
    # time_arr = [pd.Timestamp(time).to_pydatetime() for time in time_arr]
    num = len(time_arr)
    idx = np.zeros(num, dtype=int)
    idx[:] = -1
    for i in range(num):
        time_ct_second_of_day = time_ct.hour*3600 + time_ct.minute*60 + time_ct.second
        time_i = pd.Timestamp(time_arr[i]).to_pydatetime()
        time_i_second_of_day = time_i.hour*3600 + time_i.minute*60 + time_i.second

        if abs(time_ct_second_of_day - time_i_second_of_day) <= timethresh * 3600:
            idx[i] = i
    # eliminate the wrong index
    idx = idx[idx >= 0]
    # if idx.size == 0:
    #    return None
    # idx is the array including the index of times we pick up in the nc_arr
    #pick_times = np.array(snex['time'].iloc[idx.tolist()])
    #pick_times = [pd.Timestamp(time).to_pydatetime() for time in pick_times]
    #nc_arr = snex[snex['time'](time=pick_times)

    return snex.iloc[idx]


def shape_by_xy_array(x, y):
    """ construct the shapely point or linestring
    :param x: array
    :param y: array
    :return:
    """

    num = x.shape[0]

    points = [[x[i], y[i]] for i in range(num)]

    if len(points) == 1:
        return geometry.Point(points)
    else:
        return geometry.LineString(points)

def zonal_analyses_based_snex(nc_var: xr.DataArray, snex: gpd.GeoDataFrame, res: float = None,
                        timeint: int = 24, timethresh: int = 6, method: str = 'average'):
    """zonal analyses of nc_var based on time and point within snex
    arguments:
        nc_var: sentinel1 snow depth data
        snex: observation data
        timeint: for example, 24, 48, 72, 84, etc.
        timethresh: time of day close to time of day of observation.
        method: average, nearest, close

    returns: combined GeoDataFrame, it includes the zonal statistic and observation results
    """
    # get affine and bbox
    affine = nc_var.attrs['affine']
    bbox = list(nc_var.attrs['bounds'])
    poly_bbox = bbox2polygon(bbox)

    # define the list to hold the calculated statistic
    output = []

    # go over each observation time
    total_num = nc_var.values.shape[0]
    count_fund = 0
    count_nan = 0
    for index, item in snex.iterrows():
        t_ct = item['time'].to_pydatetime()
        # convert to datetime
        # t_ct = datetime.strptime(time, '%Y-%m-%dT%H:%M')
        # covert boise local standard time to utc
        #t_ct = t_ct + timedelta(hours=6)
        time = datetime.strftime(t_ct, '%Y-%m-%dT%H:%M')
        # time range
        t_st = t_ct - timedelta(hours=timeint)
        t_ed = t_ct + timedelta(hours=timeint)

        nc_timerange = nc_var.sel(time=slice(t_st, t_ed))
        if nc_timerange.shape[0] == 0:
            continue

        try:
            # get values of variable pear year
            if method == 'average':
                nc_arr = nc_timerange

            elif method == 'nearest':

                # nearest time within time interval
                nc_arr = nc_timerange.sel(time=time, method='nearest', tolerance=f'{timeint}h')
                # nc_arr = nc_timerange.sel(time=time, method='nearest', tolerance=f'{timeint}h')
            elif method == 'close':
                nc_arr = close_snex_time(nc_arr=nc_timerange, time_ct=t_ct, timethresh=timethresh)
            else:
                pass
            # check if nc_arr is None
            if nc_arr is None:
                continue
            # check if nc_arr is empty
            nc_arr_vals = nc_arr.values
            if nc_arr_vals.size == 0:
                continue
            # do spatial clip
            poly = polygon_via_point(lon=item['Longitude'], lat=item['Latitude'], resolution=res)
            poly = geometry.box(*poly.bounds)
            # decide if poly is not within bbox, return None for yes
            # if not poly_bbox.contains(poly):  # should use poly_bbox.intersects() instead contain ?
            if not poly_bbox.intersects(poly):
                continue

            # clip by poly
            jsstr = to_geojson(poly)
            geometries = [json.loads(jsstr)]
            clipped = nc_arr.rio.clip(geometries, all_touched=True)
            x = np.array(clipped.x)
            y = np.array(clipped.y)
            xx, yy = np.meshgrid(x, y)
            xx = xx.flatten()
            yy = yy.flatten()
            clipped_geometry = shape_by_xy_array(xx, yy)
            values = clipped.values
            count_fund = count_fund + 1

            if len(list(nc_arr.time.shape)) == 0:
                number_time = 1
            else:
                number_time = nc_arr.time.shape[0]

            rst1 = {'mean': np.nanmean(values), 'min': np.nanmin(values), 'max': np.nanmax(values),
                    'std': np.nanstd(values), 'count': np.count_nonzero(~np.isnan(values)),
                    'num': number_time}

            if np.isnan(rst1['mean']):
                # why are there many clipped.values with np.nan value ?
                count_nan = count_nan + 1
                print(f'none at {t_ct}')
            # rst2 = rstats.zonal_stats(poly, nc_arr_vals, affine=affine, nodata=np.nan, stats="mean min max")[0]
            rst = rst1

            output.append({'location': item['Location'], 'time': time, 'geometry': poly, 's1geometry': clipped_geometry,
                           'mean': rst['mean'], 'min': rst['min'], 'max': rst['max'], 'std': rst['std'],
                           'count': rst['count'], 'num': rst['num'], 'snex_swe': item['SWE']*0.001,
                           'snex_sd': item['snow_depth'], 'hs': item['HS']*0.01})

            print({'time': time, 'mean': rst['mean'], 'obs': item['snow_depth']})

        except:
            continue

    # return empty GeoDataFrame for an empty list output
    if not output:
        return gpd.GeoDataFrame(columns=["foo", "bar", "geometry"], crs="EPSG:4326")

    # convert output to geoDataFrame
    parsed_output = [[item['location'], item['time'], item['mean'], item['min'], item['max'], item['std'],
                      item['count'], item['num'], item['snex_swe'], item['snex_sd'], item['hs'],
                      item['geometry'], item['s1geometry']] for item in output]

    gdf = gpd.GeoDataFrame(data=parsed_output, columns=['location', 'time', 'mean', 'min', 'max', 'std', 'count',
                                                        'num', 'snex_swe', 'snex_sd', 'hs', 'geometry', 's1geometry'])

    gdf = gdf.set_crs('epsg:4326')

    print(f'number of data with NAN is {count_nan}, number of data found are {count_fund}, '
          f'number of total data are {total_num}')

    return gdf


def one_to_one(nc_arr_one_time, snex_one_time, poly_bbox, res):
    poly = polygon_via_point(lon=snex_one_time['Longitude'], lat=snex_one_time['Latitude'], resolution=res)
    poly = geometry.box(*poly.bounds)
    # decide if poly is not within bbox, return None for yes
    # if not poly_bbox.contains(poly):  # should use poly_bbox.intersects() instead contain ?
    if not poly_bbox.intersects(poly):
        return None

    # clip by poly
    jsstr = to_geojson(poly)
    geometries = [json.loads(jsstr)]
    clipped = nc_arr_one_time.rio.clip(geometries, all_touched=True)
    x = np.array(clipped.x)
    y = np.array(clipped.y)
    xx, yy = np.meshgrid(x, y)
    xx = xx.flatten()
    yy = yy.flatten()
    clipped_geometry = shape_by_xy_array(xx, yy)
    values = clipped.values

    # rst = {'mean': np.nanmean(values), 'min': np.nanmin(values), 'max': np.nanmax(values),
    #                'std': np.nanmax(values), 'count': np.count_nonzero(~np.isnan(values))
    #        }

    rst = {'location': snex_one_time['Location'], 'time': snex_one_time['Time'],
           'geometry': snex_one_time['geometry'], 's1geometry': clipped_geometry, 'mean': np.nanmean(values),
           'min': np.nanmin(values), 'max': np.nanmax(values), 'std': np.nanstd(values),
           'count': np.count_nonzero(~np.isnan(values)), 'num': 1, 'snex_swe': snex_one_time['SWE'] * 0.001,
           'snex_sd': snex_one_time['snow_depth'], 'hs': snex_one_time['HS'] * 0.01}

    return rst


def zonal_analyses_based_sentinel1(nc_var: xr.DataArray, snex: gpd.GeoDataFrame, res: float = None,
                        timeint: int = 24, timethresh: int = 6, method: str = 'average'):
    """zonal analyses of nc_var based on time and point within snex
    arguments:
        nc_var: sentinel1 snow depth data
        snex: observation data
        timeint: for example, 24, 48, 72, 84, etc.
        timethresh: time of day close to time of day of observation.
        method: average, nearest, close.
    returns: combined GeoDataFrame, it includes the zonal statistic and observation results
    """
    # convert the Time column to the datetime column
    snex['time'] = pd.to_datetime(snex['Time'])

    # get affine and bbox
    affine = nc_var.attrs['affine']
    bbox = list(nc_var.attrs['bounds'])
    poly_bbox = bbox2polygon(bbox)

    # define the list to hold the calculated statistic
    output = []

    # go over each sentinel1 data
    total_num = nc_var.values.shape[0]
    count_fund = 0
    count_nan = 0
    for i in range(len(nc_var)):
        item = nc_var[i]
        time = pd.Timestamp(item.time.values).to_pydatetime()
        # covert boise local standard time to utc
        time = time + timedelta(hours=6)
        # time = datetime.strftime(t_ct, '%Y-%m-%dT%H:%M')
        # time range
        t_st = time - timedelta(hours=timeint)
        t_ed = time + timedelta(hours=timeint)

        snex_arr = snex[(snex['time'] >= np.datetime64(t_st)) & (snex['time'] <= np.datetime64(t_ed))]
        # check empty arr
        if snex_arr.empty:
            continue
        # three methods: average, nearest, close

        snex_tmp = snex_arr.copy(deep=True)

        if 'average' in method:
            count_fund = count_fund + snex_tmp.shape[0]
            try:
                # go over every time of snex data
                for index, snex_item in snex_tmp.iterrows():
                    rst = one_to_one(item, snex_item, poly_bbox, res)
                    if np.isnan(rst['mean']):
                        # why are there many clipped.values with np.nan value ?
                        count_nan = count_nan + 1
                        print(f'none at {time}')

                    output.append(rst)
            except:
                continue

        elif 'nearest' in method:
            try:
                snex2 = snex_tmp.set_index('time', inplace=False, drop=False)
                # get the index of nearest to time
                i = np.argmin(np.abs(snex2.index - time))
                count_fund = count_fund + 1
                rst = one_to_one(item, snex2.iloc[i], poly_bbox, res)
                output.append(rst)
                if np.isnan(rst['mean']):
                    count_nan = count_nan + 1
            except:
                continue

        elif 'close' in method:
            snex_tmp = close_s1_time(snex=snex_tmp, time_ct=time, timethresh=timethresh)
            count_fund = count_fund + len(snex_arr)
            for index, snex_item in snex_tmp.iterrows():
                rst = one_to_one(item, snex_item, poly_bbox, res)
                if np.isnan(rst['mean']):
                    # why are there many clipped.values with np.nan value ?
                    count_nan = count_nan + 1
                    print(f'none at {time}')

                output.append(rst)
        else:
            pass

    # return empty GeoDataFrame for an empty list output
    # if not output:
    #    return gpd.GeoDataFrame(columns=["foo", "bar", "geometry"], crs="EPSG:4326")

    # convert output to geoDataFrame
    parsed_output = [[item['location'], item['time'], item['mean'], item['min'], item['max'], item['std'],
                      item['count'], item['num'], item['snex_swe'], item['snex_sd'], item['hs'],
                      item['geometry'], item['s1geometry']] for item in output]

    gdf = gpd.GeoDataFrame(data=parsed_output, columns=['location', 'time', 'mean', 'min', 'max', 'std', 'count',
                                                        'num', 'snex_swe', 'snex_sd', 'hs', 'geometry', 's1geometry'])

    gdf = gdf.set_crs('epsg:4326')

    print(f'number of data with NAN is {count_nan}, number of data found are {count_fund}, '
          f'number of total data are {total_num}')

    return gdf

def one_s1_to_one_snotel(nc_arr_one_time, snex_one_time, poly_bbox, res):
    poly = polygon_via_point(lon=snex_one_time['Longitude'], lat=snex_one_time['Latitude'], resolution=res)
    poly = geometry.box(*poly.bounds)
    # decide if poly is not within bbox, return None for yes
    # if not poly_bbox.contains(poly):  # should use poly_bbox.intersects() instead contain ?
    if not poly_bbox.intersects(poly):
        return None

    # clip by poly
    jsstr = to_geojson(poly)
    geometries = [json.loads(jsstr)]
    clipped = nc_arr_one_time.rio.clip(geometries, all_touched=True)
    x = np.array(clipped.x)
    y = np.array(clipped.y)
    xx, yy = np.meshgrid(x, y)
    xx = xx.flatten()
    yy = yy.flatten()
    clipped_geometry = shape_by_xy_array(xx, yy)
    values = clipped.values

    # rst = {'mean': np.nanmean(values), 'min': np.nanmin(values), 'max': np.nanmax(values),
    #                'std': np.nanmax(values), 'count': np.count_nonzero(~np.isnan(values))
    #        }

    rst = {'time': snex_one_time['time'],
           'geometry': snex_one_time['geometry'], 's1geometry': clipped_geometry, 'mean': np.nanmean(values),
           'min': np.nanmin(values), 'max': np.nanmax(values), 'std': np.nanstd(values),
           'count': np.count_nonzero(~np.isnan(values)), 'num': 1, 'snex_sd': snex_one_time['snow_depth']}

    return rst

def one_s1_ds_to_one_snotel(nc_ds_one_time, snex_one_time, poly_bbox, res):
    poly = polygon_via_point(lon=snex_one_time['Longitude'], lat=snex_one_time['Latitude'], resolution=res)
    poly = geometry.box(*poly.bounds)
    # decide if poly is not within bbox, return None for yes
    # if not poly_bbox.contains(poly):  # should use poly_bbox.intersects() instead contain ?
    if not poly_bbox.intersects(poly):
        return None

    # clip by poly
    jsstr = to_geojson(poly)
    geometries = [json.loads(jsstr)]
    clipped = nc_ds_one_time.rio.clip(geometries, all_touched=True)
    x = np.array(clipped.x)
    y = np.array(clipped.y)
    xx, yy = np.meshgrid(x, y)
    xx = xx.flatten()
    yy = yy.flatten()
    clipped_geometry = shape_by_xy_array(xx, yy)
    val_sd = clipped.snow_depth.values
    val_cr = clipped.deltaCRt.values

    rst = {'time': snex_one_time['time'],
           'geometry': snex_one_time['geometry'], 's1geometry': clipped_geometry,
           'mean': np.nanmean(val_sd), 'min': np.nanmin(val_sd), 'max': np.nanmax(val_sd),'std': np.nanstd(val_sd),
           'meancr': np.nanmean(val_cr), 'mincr': np.nanmin(val_cr), 'maxcr': np.nanmax(val_cr),
           'stdcr': np.nanstd(val_cr),
           'count': np.count_nonzero(~np.isnan(val_sd)), 'num': 1, 'snex_sd': snex_one_time['snow_depth']}

    return rst


# def zonal_analyses_s1_snotel_based_s1

def zonal_analyses_s1_snotel_based_s1(nc_var: xr.DataArray, snex: gpd.GeoDataFrame, res: float = None,
                                   timeint: int = 24, timethresh: int = 6, method: str = 'average'):
    """zonal analyses of nc_var based on time and point within snex
    arguments:
        nc_var: sentinel1 snow depth data
        snex: observation data
        timeint: for example, 24, 48, 72, 84, etc.
        timethresh: time of day close to time of day of observation.
        method: average, nearest, close.
    returns: combined GeoDataFrame, it includes the zonal statistic and observation results
    """
    # get affine and bbox
    affine = nc_var.attrs['affine']
    bbox = list(nc_var.attrs['bounds'])
    poly_bbox = bbox2polygon(bbox)

    # define the list to hold the calculated statistic
    output = []

    # go over each sentinel1 data
    total_num = nc_var.values.shape[0]
    count_fund = 0
    count_nan = 0
    for i in range(len(nc_var)):
        item = nc_var[i]
        time = pd.Timestamp(item.time.values).to_pydatetime()
        # both s1 and SNOTEL time are in utc
        t_st = time - timedelta(hours=timeint)
        t_ed = time + timedelta(hours=timeint)
        snex_arr = snex[(snex['time'] >= np.datetime64(t_st)) & (snex['time'] <= np.datetime64(t_ed))]
        # check empty arr
        if snex_arr.empty:
            continue
        # three methods: average, nearest, close

        snex_tmp = snex_arr.copy(deep=True)

        if 'average' in method:
            count_fund = count_fund + snex_tmp.shape[0]
            try:
                # go over every time of snex data
                for index, snex_item in snex_tmp.iterrows():
                    rst = one_s1_to_one_snotel(item, snex_item, poly_bbox, res)
                    if np.isnan(rst['mean']):
                        # why are there many clipped.values with np.nan value ?
                        count_nan = count_nan + 1
                        print(f'none at {time}')

                    output.append(rst)
            except:
                continue

        elif 'nearest' in method:
            try:
                snex2 = snex_tmp.set_index('time', inplace=False, drop=False)
                # get the index of nearest to time
                i = np.argmin(np.abs(snex2.index - time))
                count_fund = count_fund + 1
                rst = one_to_one(item, snex2.iloc[i], poly_bbox, res)
                output.append(rst)
                if np.isnan(rst['mean']):
                    count_nan = count_nan + 1
            except:
                continue

        elif 'close' in method:
            snex_tmp = close_s1_time(snex=snex_tmp, time_ct=time, timethresh=timethresh)
            count_fund = count_fund + len(snex_arr)
            for index, snex_item in snex_tmp.iterrows():
                rst = one_to_one(item, snex_item, poly_bbox, res)
                if np.isnan(rst['mean']):
                    # why are there many clipped.values with np.nan value ?
                    count_nan = count_nan + 1
                    print(f'none at {time}')

                output.append(rst)
        else:
            pass

    # return empty GeoDataFrame for an empty list output
    # if not output:
    #    return gpd.GeoDataFrame(columns=["foo", "bar", "geometry"], crs="EPSG:4326")

    # convert output to geoDataFrame
    parsed_output = [[item['time'], item['mean'], item['min'], item['max'], item['std'],
                      item['count'], item['num'], item['snex_sd'],
                      item['geometry'], item['s1geometry']] for item in output]

    gdf = gpd.GeoDataFrame(data=parsed_output, columns=['time', 'mean', 'min', 'max', 'std',
                                                        'count', 'num', 'snex_sd',
                                                        'geometry', 's1geometry'])

    gdf = gdf.set_crs('epsg:4326')

    print(f'number of data with NAN is {count_nan}, number of data found are {count_fund}, '
          f'number of total data are {total_num}')

    return gdf

def zonal_analyses_s1_snotel_dry_wet_based_s1(nc_var: xr.Dataset, snex: gpd.GeoDataFrame, res: float = None,
                                   timeint: int = 24, timethresh: int = 6, method: str = 'average'):
    """zonal analyses of nc_var based on time and point within snex
    arguments:
        nc_var: sentinel1 dataset
        snex: observation data
        timeint: for example, 24, 48, 72, 84, etc.
        timethresh: time of day close to time of day of observation.
        method: average, nearest, close.
    returns: combined GeoDataFrame, it includes the zonal statistic and observation results
    """
    # get affine and bbox
    affine = nc_var.attrs['affine']
    bbox = list(nc_var.attrs['bounds'])
    poly_bbox = bbox2polygon(bbox)

    # define the list to hold the calculated statistic
    output = []

    # go over each sentinel1 data
    total_num = nc_var.time.values.shape[0]
    count_fund = 0
    count_nan = 0
    for i in range(len(nc_var.time)):
        item = nc_var.sel(time=nc_var.time[i])
        time = pd.Timestamp(item.time.values).to_pydatetime()
        # both s1 and SNOTEL time are in utc
        t_st = time - timedelta(hours=timeint)
        t_ed = time + timedelta(hours=timeint)
        snex_arr = snex[(snex['time'] >= np.datetime64(t_st)) & (snex['time'] <= np.datetime64(t_ed))]
        # check empty arr
        if snex_arr.empty:
            continue
        # three methods: average, nearest, close

        snex_tmp = snex_arr.copy(deep=True)

        if 'average' in method:
            count_fund = count_fund + snex_tmp.shape[0]
            try:
                # go over every time of snex data
                for index, snex_item in snex_tmp.iterrows():
                    rst = one_s1_ds_to_one_snotel(item, snex_item, poly_bbox, res)
                    if np.isnan(rst['mean']):
                        # why are there many clipped.values with np.nan value ?
                        count_nan = count_nan + 1
                        print(f'none at {time}')

                    output.append(rst)
            except:
                continue

        elif 'nearest' in method:
            try:
                snex2 = snex_tmp.set_index('time', inplace=False, drop=False)
                # get the index of nearest to time
                i = np.argmin(np.abs(snex2.index - time))
                count_fund = count_fund + 1
                rst = one_to_one(item, snex2.iloc[i], poly_bbox, res)
                output.append(rst)
                if np.isnan(rst['mean']):
                    count_nan = count_nan + 1
            except:
                continue

        elif 'close' in method:
            snex_tmp = close_s1_time(snex=snex_tmp, time_ct=time, timethresh=timethresh)
            count_fund = count_fund + len(snex_arr)
            for index, snex_item in snex_tmp.iterrows():
                rst = one_to_one(item, snex_item, poly_bbox, res)
                if np.isnan(rst['mean']):
                    # why are there many clipped.values with np.nan value ?
                    count_nan = count_nan + 1
                    print(f'none at {time}')

                output.append(rst)
        else:
            pass

    # return empty GeoDataFrame for an empty list output
    # if not output:
    #    return gpd.GeoDataFrame(columns=["foo", "bar", "geometry"], crs="EPSG:4326")

    # convert output to geoDataFrame
    parsed_output = [[item['time'], item['mean'], item['min'], item['max'], item['std'],
                      item['meancr'], item['mincr'], item['maxcr'], item['stdcr'],
                      item['count'], item['num'], item['snex_sd'],
                      item['geometry'], item['s1geometry']] for item in output]

    gdf = gpd.GeoDataFrame(data=parsed_output, columns=['time', 'mean', 'min', 'max', 'std',
                                                        'meancr', 'mincr', 'maxcr', 'stdcr', 'count',
                                                        'num', 'snex_sd', 'geometry',
                                                        's1geometry'])

    gdf = gdf.set_crs('epsg:4326')

    print(f'number of data with NAN is {count_nan}, number of data found are {count_fund}, '
          f'number of total data are {total_num}')

    return gdf



def draw_barplot(x, y):

    plt.bar(x, y)


def draw_line_plot(x, data_dic):
    fig, ax = plt.subplots()
    ax.plot(x, data_dic['min'], label='min', color='black')
    ax.plot(x, data_dic['mean'], label='mean', color='blue')
    ax.plot(x, data_dic['max'], label='max', color='red')
    ax.plot(x, data_dic['obs'], label='obs SWE', color='green')
    ax.legend()
    ax.set_title(f'Zonal Statistic of snow depth for {data_dic['location']}')
    ax.set_xlabel("Observation Date, date")
    ax.set_ylabel("snow depth, m")
    plt.show()


def draw_combined_gdf(gdf, res, timeint, timethresh, base, method, outfile, precip):

    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]

    corr = gdf['mean'].corr(gdf['hs'])

    # draw gdf on the plot

    minv = np.array(gdf['min'])

    meanv = np.array(gdf['mean'])

    maxv = np.array(gdf['max'])

    stderror = np.array(gdf['std'])

    times = np.array(gdf['time'])

    obs = np.array(gdf['snex_swe'])

    # times1 = [datetime.strptime(item, '%Y-%m-%dT%H:%M') for item in times]

    times1 = [pd.Timestamp(item) for item in times]

    days = [(item - times1[0]).total_seconds()/(24*3600.0) for item in times1]

    # convert times to datetime

    xtks = np.arange(days[0], np.round(days[-1]) + 2, 5)

    xtkslb = [str(int(item)) for item in xtks]

    start_time = times1[0].strftime("%Y%m%d")

    loc = gdf['location'].iloc[0]

    data_dic = {'location': loc, 'min': minv, 'mean': meanv, 'max': maxv, 'obs': obs}

    fig, ax = plt.subplots()

    fig.set_figwidth(30)

    # ax.plot(days, data_dic['min'], label='min', color='black')
    # ax.plot(days, data_dic['mean'], label='mean', color='blue')
    ax.plot(days, gdf['mean'], label='mean', color='blue')

    ax.errorbar(days, gdf['mean'], yerr=stderror, color='blue')
    
    # ax.plot(days, data_dic['max'], label='max', color='red')

    # ax.plot(days, gdf['snex_swe'], label='obs SWE', color='green')

    ax.plot(days, gdf['snex_sd'], label='obs snow depth', color='red')

    # ax.plot(days, gdf['hs'], label='obs snow height', color='black')

    ax.set_xticks(xtks, labels=xtkslb)

    ax.legend()

    corr = float("{:.2f}".format(corr))

    ax.text(0.8, 0.8, f'correlation: {corr}', color='red', transform=ax.transAxes)

    ax.set_title(f'{base}-based {method} Zonal Statistic of Snow Depth for {loc} with {str(int(res))} m and'
                  f' {int(timeint)} hours time interval with {int(timethresh)} hours threshold with precip {precip}')
    ax.set_xlabel(f'Observation day, days from staring {start_time}')
    ax.set_ylabel("snow depth, m")

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)

    plt.show()


def draw_diff_error_count_plot(gdf, res, timeint, timethresh, base, method, outfile, precip):
    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]

    corr = gdf['mean'].corr(gdf['hs'])

    # draw gdf on the plot

    minv = np.array(gdf['min'])

    meanv = np.array(gdf['mean'])

    maxv = np.array(gdf['max'])

    stderror = np.array(gdf['std'])

    times = np.array(gdf['time'])

    snow_depth_diff = gdf['hs'] - gdf['mean']

    # times1 = [datetime.strptime(item, '%Y-%m-%dT%H:%M') for item in times]

    times1 = [pd.Timestamp(item) for item in times]

    days = [(item - times1[0]).total_seconds() / (24 * 3600.0) for item in times1]

    # convert times to datetime

    xtks = np.arange(days[0], np.round(days[-1]) + 2, 5)

    xtkslb = [str(int(item)) for item in xtks]

    start_time = times1[0].strftime("%Y%m%d")

    loc = gdf['location'].iloc[0]

    # data_dic = {'location': loc, 'min': minv, 'mean': meanv, 'max': maxv, 'obs': obs}

    # fig, ax = plt.subplots()
    fig, [ax0, ax1,  ax2] = plt.subplots(nrows=3, ncols=1)
    fig.set_figwidth(30)
    fig.set_figheight(30)


    # ax.plot(days, data_dic['min'], label='min', color='black')
    # ax.plot(days, data_dic['mean'], label='mean', color='blue')
    # ax0.plot(days, gdf['snex_sd'] - gdf['mean'], label='snow depth difference', color='blue')

    # mean, obs
    ax0.plot(days, gdf['mean'], label='mean', color='blue')
    ax0.errorbar(days, gdf['mean'], yerr=stderror, color='blue')
    ax0.plot(days, gdf['snex_sd'], label='obs snow depth', color='red')
    ax0.set_xticks(xtks, labels=xtkslb)
    ax0.legend()

    corr = float("{:.2f}".format(corr))

    ax0.text(0.8, 0.8, f'correlation: {corr}', color='red', transform=ax0.transAxes)

    ax0.set_title(f'{base}-based {method} Zonal Statistic of Snow Depth for {loc} with {str(int(res))} m and'
                  f' {int(timeint)} hours time interval with {int(timethresh)} hours threshold with precip {precip}')
    ax0.set_xlabel(f'Observation day, days from staring {start_time}')
    ax0.set_ylabel("snow depth, m")

    # differnec with mean standard error bar
    ax1.errorbar(days, gdf['snex_sd'] - gdf['mean'], yerr=gdf['std'], label='Difference with mean standard error', color='red')

    ax1.set_xticks(xtks, labels=xtkslb)
    ax1.legend()

    corr = float("{:.2f}".format(corr))
    ax1.text(0.8, 0.8, f'correlation: {corr}', color='red', transform=ax1.transAxes)

    ax1.set_title(f'{base}-based {method} Zonal Statistic of Snow Depth for {loc} with {str(int(res))} m and'
                  f' {int(timeint)} hours time interval with {int(timethresh)} hours threshold with precip {precip}')

    ax1.set_xlabel(f'Observation day, days from staring {start_time}')

    ax1.set_ylabel("snow depth, m")

    # Number of pixels of mean
    ax2.plot(days, gdf['count'], label='Number of pixels', color='green')
    ax2.set_xticks(xtks, labels=xtkslb)
    ax2.set_xlabel(f'Observation day, days from staring {start_time}')
    ax2.legend()

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)

    plt.show()


def draw_diff_error_count_plot_index(gdf, res, timeint, timethresh, base, method, outfile, precip):
    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]
    gdf = gdf[(gdf['mean'] >= 0.0) & (gdf['hs'] >= 0.0)]
    corr = gdf['mean'].corr(gdf['hs'])

    # draw gdf on the plot

    minv = np.array(gdf['min'])

    meanv = np.array(gdf['mean'])

    maxv = np.array(gdf['max'])

    stderror = np.array(gdf['std'])

    loc = gdf['location'].iloc[0]

    fig, [ax0, ax1,  ax2] = plt.subplots(nrows=3, ncols=1)
    fig.set_figwidth(30)
    fig.set_figheight(30)

    # mean, obs
    s1_mean = "{:.2f}".format(gdf['mean'].mean())
    s1_std = "{:.2f}".format(gdf['mean'].std())
    obs_mean = "{:.2f}".format(gdf['snex_sd'].mean())
    obs_std = "{:.2f}".format(gdf['snex_sd'].std())

    ax0.plot(gdf.index, gdf['mean'], label=f'sentinel1 snow depth, mean {s1_mean},'
                                           f' std {s1_std} ', color='blue')
    ax0.errorbar(gdf.index, gdf['mean'], yerr=stderror, color='blue')
    ax0.plot(gdf.index, gdf['snex_sd'], label=f'snex snow depth, mean {obs_mean},'
                                              f'std {obs_std}', color='red')
    # ax0.set_xticks(xtks, labels=xtkslb)
    ax0.legend()

    corr1 = float("{:.2f}".format(corr))

    ax0.text(0.5, 0.9, f' Correlation {corr1}, Number of observations {len(gdf)}', color='red', transform=ax0.transAxes)

    ax0.set_title(f'{base}-based {method} Zonal Statistic of Snow Depth for {loc} with {str(int(res))} m and'
                  f' {int(timeint)} hours time interval with {int(timethresh)} hours threshold with precip {precip}')
    ax0.set_xlabel(f'Sequence of Observations')
    ax0.set_ylabel("snow depth, m")

    # differnec with mean standard error bar
    diff = gdf['mean'] - gdf['hs']
    #diff_mean = "{:.2f}".format(diff.mean())
    diff_mean = round(diff.mean(), 2)
    #diff_std = "{:.2f}".format(diff.std())
    diff_std = round(diff.std(), 2)
    ax1.errorbar(gdf.index, diff, yerr=stderror, label='Difference with mean standard error', color='red')

    #ax1.set_xticks(xtks, labels=xtkslb)
    ax1.legend()

    corr1 = float("{:.2f}".format(corr))

    ax1.text(0.6, 0.9, f'Correlation {corr1}, mean of difference {diff_mean}, std {diff_std}', color='red',
             transform = ax1.transAxes)

    ax1.set_title(f'The difference of Snow Depth Depth for {loc} with {str(int(res))} m and'
                  f' {int(timeint)} hours time interval with {int(timethresh)} hours threshold with precip {precip}')

    ax1.set_xlabel(f'Sequence of Observations')

    ax1.set_ylabel("snow depth, m")

    # Number of pixels of mean
    ax2.plot(gdf.index, gdf['count'], label='Number of pixels', color='green')
    # ax2.set_xticks(xtks, labels=xtkslb)
    ax2.set_xlabel(f'Sequence of Observations')
    ax2.legend()

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)

    plt.show()

def draw_s1_snotel_diff_error_count_plot(gdf, res, timeint, timethresh, base, method, outfile, precip, loc):
    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]
    gdf = gdf[(gdf['mean'] >= 0.0) & (gdf['snex_sd'] >= 0.0)]

    corr = gdf['mean'].corr(gdf['snex_sd'])

    ym = np.array(gdf['mean'])
    xm = np.array(gdf['snex_sd'])

    r = np.corrcoef(ym,xm)
    corr = r[0,1]
    rmse = np.sqrt(((xm - ym) ** 2).mean())
    mbe = np.mean(ym - xm)


    # draw gdf on the plot

    minv = np.array(gdf['min'])

    meanv = np.array(gdf['mean'])

    maxv = np.array(gdf['max'])

    stderror = np.array(gdf['std'])


    fig, [ax0, ax1,  ax2] = plt.subplots(nrows=3, ncols=1)
    fig.set_figwidth(30)
    fig.set_figheight(30)

    # mean, obs
    s1_mean = "{:.2f}".format(gdf['mean'].mean())
    s1_std = "{:.2f}".format(gdf['mean'].std())
    obs_mean = "{:.2f}".format(gdf['snex_sd'].mean())
    obs_std = "{:.2f}".format(gdf['snex_sd'].std())
    corr1 = float("{:.2f}".format(corr))
    rmse1 = "{:.2f}".format(rmse)
    mbe1 = "{:.2f}".format(mbe)


    x = gdf.index

    xtks = x

    xtklbs = gdf.time[x].dt.strftime('%m/%d')

    # get every 10th
    xtks = xtks[0::10]

    xtklbs = xtklbs[0::10]

    ax0.plot(x, gdf['mean'], label=f'S1 Snow Depth, mean {s1_mean},'
                                           f' std {s1_std} ', color='blue')
    ax0.errorbar(x, gdf['mean'], yerr=stderror, color='blue')

    ax0.plot(x, gdf['snex_sd'], label=f'SNOTEL Snow Depth, mean {obs_mean},'
                                              f'std {obs_std}', color='red')

    ax0.set_xticks(xtks, xtklbs)

    ax0.legend()

    ax0.text(0.3, 0.9, f'RMSE {rmse1}, R {corr1}, MBE {mbe1}, Number of observations {len(gdf)}', color='red', transform=ax0.transAxes)

    ax0.set_title(f'{base.capitalize()}-based Zonal Statistic of {method.capitalize()} S1 Snow Depth with {str(int(res))} m and'
                  f' {int(timeint)} Hours Time Interval and SNOTEL Snow Depth for {loc}')
    ax0.set_xlabel(f'Sequence of Observations')
    ax0.set_ylabel("snow depth, m")

    # differnec with mean standard error bar
    diff = gdf['mean'] - gdf['snex_sd']
    #diff_mean = "{:.2f}".format(diff.mean())
    diff_mean = round(diff.mean(), 2)
    #diff_std = "{:.2f}".format(diff.std())
    diff_std = round(diff.std(), 2)
    ax1.errorbar(x, diff, yerr=stderror, label='Difference with Mean Standard Error', color='red')

    ax1.set_xticks(xtks, xtklbs)
    ax1.legend()

    corr1 = float("{:.2f}".format(corr))

    ax1.text(0.6, 0.9, f'Correlation {corr1}, Mean of Difference {diff_mean}, STD {diff_std}', color='red',
             transform = ax1.transAxes)

    ax1.set_title(f'The Difference of S1 Snow Depth Depth with {str(int(res))} m and'
                  f' {int(timeint)} Hours Time Interval and SNOTEL Snow Depth for {loc}')

    ax1.set_xlabel(f'Sequence of Observations')

    ax1.set_ylabel("Snow Depth, m")

    # Number of pixels of mean
    ax2.plot(x, gdf['count'], label='Number of pixels', color='green')
    # ax2.set_xticks(xtks, labels=xtkslb)
    ax2.set_xlabel(f'Sequence of Observations')
    ax2.set_xticks(xtks, xtklbs)
    ax2.legend()

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)

    plt.show()


def draw_s1_sd_cr_snotel_plot(gdf, res, timeint, timethresh, base, method, outfile, precip, loc):
    # draw S1 snow depth, delataCR in ratio, and SNOTEL snow depth in the same figure
    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]
    gdf = gdf[(gdf['mean'] >= 0.0) & (gdf['snex_sd'] >= 0.0)]

    corr = gdf['mean'].corr(gdf['snex_sd'])

    ym = np.array(gdf['mean'])
    xm = np.array(gdf['snex_sd'])

    r = np.corrcoef(ym,xm)
    corr = r[0,1]
    rmse = np.sqrt(((xm - ym) ** 2).mean())
    mbe = np.mean(ym - xm)


    # draw gdf on the plot

    minv = np.array(gdf['min'])

    meanv = np.array(gdf['mean'])

    maxv = np.array(gdf['max'])

    stderror = np.array(gdf['std'])


    fig, [ax0, ax1,  ax2] = plt.subplots(nrows=3, ncols=1)
    fig.set_figwidth(30)
    fig.set_figheight(30)

    # xticks and xtick labels
    x = gdf.index
    xtks = x
    xtklbs = gdf.time[x].dt.strftime('%m/%d')
    # get every 10th
    xtks = xtks[0::10]
    xtklbs = xtklbs[0::10]

    # statistic
    obs_mean = "{:.2f}".format(gdf['snex_sd'].mean())
    obs_std = "{:.2f}".format(gdf['snex_sd'].std())
    corr1 = float("{:.2f}".format(corr))
    rmse1 = "{:.2f}".format(rmse)
    mbe1 = "{:.2f}".format(mbe)

    # ax0, draw s1 snow depth
    # s1 statistic
    s1_mean = "{:.2f}".format(gdf['mean'].mean())
    s1_std = "{:.2f}".format(gdf['mean'].std())


    ax0.plot(x, gdf['mean'], label=f'S1 Depth, mean {s1_mean},'
                                           f' std {s1_std} ', color='blue')
    # ax0.text(0.3, 0.9, f'Correlation between S1 and SNOTEL snow depths {corr1}', color='red')
    ax0.set_xticks(xtks, xtklbs)
    ax0.legend()
    ax0.text(0.1, 0.9, f'RMSE {rmse1}, R {corr1}, MBE {mbe1}, Number of observations {len(gdf)}', color='red', transform=ax0.transAxes)

    ax0.set_title(f'{base.capitalize()}-based Zonal Statistic of {method.capitalize()} S1 Snow Depth with {str(int(res))} m and'
                  f' {int(timeint)} Hours Time Interval for {loc}')
    ax0.set_xlabel(f'Sequence of Observations')
    ax0.set_ylabel("S1 Snow Depth")

    # draw delta CR in ratio

    # s1 deltacr statistic
    s1_cr_mean = "{:.2f}".format(gdf['mean'].mean())
    s1_cr_std = "{:.2f}".format(gdf['mean'].std())
    corr = gdf['meancr'].corr(gdf['snex_sd'])
    ax1.plot(x, gdf['meancr'], label=f'S1 DeltaCR, mean {s1_cr_mean},'
                                      f'std {s1_cr_std}', color='red')
    ax1.set_xticks(xtks, xtklbs)
    ax1.legend()
    corr1 = float("{:.2f}".format(corr))
    ax1.text(0.1, 0.9, f'Correlation between deltaCR and SNOTEL Snow Depth {corr1}', color='red', transform=ax1.transAxes)
    ax1.set_title(f'S1 deltaCR for {loc}')
    ax1.set_xlabel(f'Sequence of Observations')
    ax1.set_ylabel("Delta Cross Ratio")

    # draw SNOTEL snow depth
    corr = gdf['mean'].corr(gdf['snex_sd'])
    ax2.plot(x, gdf['snex_sd'], label=f'SNOTEL Snow Depth, mean {obs_mean},'
                                      f'std {obs_std}', color='red')
    ax2.set_xticks(xtks, xtklbs)
    ax2.legend()
    corr1 = float("{:.2f}".format(corr))
    ax2.text(0.1, 0.9, f'Correlation between S1 and SNOTEL snow depths {corr1}', color='red', transform=ax2.transAxes)
    ax2.set_title(f'SNOTEL Snow Depth for {loc}')
    ax2.set_xlabel(f'Sequence of Observations')
    ax2.set_ylabel("Snow Depth, m")
    ax2.legend()

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)

    plt.show()


def draw_s1_sd_snotel_plot(gdf, res, timeint, timethresh, base, method, outfile, precip, loc):
    # draw S1 snow depth and SNOTEL snow depth in the same figure
    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]
    gdf = gdf[(gdf['mean'] >= 0.0) & (gdf['snex_sd'] >= 0.0)]

    corr = gdf['mean'].corr(gdf['snex_sd'])

    ym = np.array(gdf['mean'])
    xm = np.array(gdf['snex_sd'])

    r = np.corrcoef(ym,xm)
    corr = r[0,1]
    rmse = np.sqrt(((xm - ym) ** 2).mean())
    mbe = np.mean(ym - xm)


    # draw gdf on the plot

    minv = np.array(gdf['min'])

    meanv = np.array(gdf['mean'])

    maxv = np.array(gdf['max'])

    stderror = np.array(gdf['std'])


    fig, [ax0, ax1,  ax2] = plt.subplots(nrows=3, ncols=1)
    fig.set_figwidth(30)
    fig.set_figheight(30)

    # xticks and xtick labels
    x = gdf.index
    xtks = x
    xtklbs = gdf.time[x].dt.strftime('%m/%d')
    # get every 10th
    xtks = xtks[0::10]
    xtklbs = xtklbs[0::10]

    # statistic
    obs_mean = "{:.2f}".format(gdf['snex_sd'].mean())
    obs_std = "{:.2f}".format(gdf['snex_sd'].std())
    corr1 = float("{:.2f}".format(corr))
    rmse1 = "{:.2f}".format(rmse)
    mbe1 = "{:.2f}".format(mbe)

    # ax0, draw s1 snow depth
    # s1 statistic
    s1_mean = "{:.2f}".format(gdf['mean'].mean())
    s1_std = "{:.2f}".format(gdf['mean'].std())


    ax0.plot(x, gdf['mean'], label=f'S1 Depth, mean {s1_mean},'
                                           f' std {s1_std} ', color='blue')
    # ax0.text(0.3, 0.9, f'Correlation between S1 and SNOTEL snow depths {corr1}', color='red')
    ax0.set_xticks(xtks, xtklbs)
    ax0.legend()
    ax0.text(0.1, 0.9, f'RMSE {rmse1}, R {corr1}, MBE {mbe1}, Number of observations {len(gdf)}', color='red', transform=ax0.transAxes)

    ax0.set_title(f'{base.capitalize()}-based Zonal Statistic of {method.capitalize()} S1 Snow Depth with {str(int(res))} m and'
                  f' {int(timeint)} Hours Time Interval for {loc}')
    ax0.set_xlabel(f'Sequence of Observations')
    ax0.set_ylabel("S1 Snow Depth")

    '''
    # draw delta CR in ratio

    # s1 deltacr statistic
    s1_cr_mean = "{:.2f}".format(gdf['mean'].mean())
    s1_cr_std = "{:.2f}".format(gdf['mean'].std())
    corr = gdf['meancr'].corr(gdf['snex_sd'])
    ax1.plot(x, gdf['meancr'], label=f'S1 DeltaCR, mean {s1_cr_mean},'
                                      f'std {s1_cr_std}', color='red')
    ax1.set_xticks(xtks, xtklbs)
    ax1.legend()
    corr1 = float("{:.2f}".format(corr))
    ax1.text(0.1, 0.9, f'Correlation between deltaCR and SNOTEL Snow Depth {corr1}', color='red', transform=ax1.transAxes)
    ax1.set_title(f'S1 deltaCR for {loc}')
    ax1.set_xlabel(f'Sequence of Observations')
    ax1.set_ylabel("Delta Cross Ratio")

    '''
    # draw SNOTEL snow depth
    corr = gdf['mean'].corr(gdf['snex_sd'])
    ax2.plot(x, gdf['snex_sd'], label=f'SNOTEL Snow Depth, mean {obs_mean},'
                                      f'std {obs_std}', color='red')
    ax2.set_xticks(xtks, xtklbs)
    ax2.legend()
    corr1 = float("{:.2f}".format(corr))
    ax2.text(0.1, 0.9, f'Correlation between S1 and SNOTEL snow depths {corr1}', color='red', transform=ax2.transAxes)
    ax2.set_title(f'SNOTEL Snow Depth for {loc}')
    ax2.set_xlabel(f'Sequence of Observations')
    ax2.set_ylabel("Snow Depth, m")
    ax2.legend()

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)

    plt.show()


def draw_histgram(gdf, res, timeint, timethresh, base, method, outfile, precip, loc):
    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]

    corr = gdf['mean'].corr(gdf['snex_sd'])

    # loc = gdf['location'].iloc[0]
    # draw gdf on the plot
    n_bins = 10
    colors = ['green', 'blue', 'lime', 'red']
    # fig, ax = plt.subplots()
    # fig.set_figwidth(30)
    fig, [(ax0, ax1), (ax2, ax3)] = plt.subplots(nrows=2, ncols=2)
    fig.set_figwidth(30)
    fig.set_figheight(30)

    fig.suptitle(f'{base.capitalize()}-based {method.capitalize()} Zonal Statistic of Snow Depth with {str(int(res))} m and'
                  f' {int(timeint)} Hours Time Interval for {loc}')

    diff = gdf['snex_sd'] - gdf['mean']

    # ax0.hist(diff, bins=n_bins, histtype='bar', color=colors[0], label=f'Total Count {len(gdf['snex_sd'])}')

    ax0.hist(diff, bins=n_bins, histtype='bar', weights=np.ones(len(diff)) / len(diff), label=f'Total Count {len(diff)}' )

    # Set the formatter
    ax0.yaxis.set_major_formatter(PercentFormatter(1))

    ax0.legend(prop={'size': 10})
    ax0.set_title('Difference of Snow Depth')
    ax0.set_xlabel(f'Difference of Snow Depth, m')
    ax0.set_ylabel("Count")


    ax1.hist(gdf['std'], n_bins, histtype='barstacked', stacked=True,  color=colors[1])
    ax1.set_title('Standard Error of Sentinel1 Snow Depth')
    ax1.set_xlabel(f'Snow Depth Standard Error, m')
    ax1.set_ylabel("Count")

    ax2.hist(gdf['count'], n_bins, histtype='barstacked', stacked=True,  color=colors[2])
    ax2.set_title('Number of Pixels for Average of Sentinel1 Snow Depth')
    ax2.set_xlabel(f'Number of Pixels')
    ax2.set_ylabel("Count")

    ax3.hist(gdf['num'], n_bins, histtype='barstacked', stacked=True,  color=colors[3])
    ax3.set_title('Number of Images for Average')
    ax3.set_xlabel(f'Number of images for Average of Sentinel1 Snow Depth')
    ax3.set_ylabel("Count")
    ax3.legend()
    num_bins = 10
    #n, bins, patches = ax.hist(gdf['snex_sd'] - gdf['mean'], num_bins,
    #                           density=1,
    #                           color='green',
    #                           alpha=0.7)

    #num = len(gdf['snex_sd'] - gdf['mean'])
    #ax.hist(gdf['snex_sd'] - gdf['mean'])
    #y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
    #     np.exp(-0.5 * (1 / sigma * (bins - mu)) ** 2))
    #ax.plot(bins, y, '--', color='black')

    #ax.legend()
    # ax.set_xlabel('X-Axis')
    # ax.set_ylabel('Y-Axis')

    #corr = float("{:.2f}".format(corr))

    #ax.text(0.8, 0.8, f'correlation: {corr}, total number of difference {num}', color='red', transform=ax.transAxes)


    #ax.set_title(f'Histgram of Difference of snex - sentinel1 Snow Depth with {str(int(res))} m and {int(timeint)} hours with {int(timethresh)} hours with precip'
    #             f' {precip} {base} based {method} Zonal Statistic of Snow Depth for {gdf['location'].iloc[0]}')
    #ax.set_xlabel(f'snow depth difference values, m')
    #ax.set_ylabel("Frequency")

    plt.show()

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)

    plt.show()


def draw_scatter_plot(gdf, res, timeint):

    # get rid of rows that does not include valid mean

    gdf = gdf[~gdf['mean'].isnull()]

    corr = gdf['mean'].corr(gdf['snex_swe'])

    # draw gdf on the plot

    minv = np.array(gdf['min'])

    meanv = np.array(gdf['mean'])

    maxv = np.array(gdf['max'])

    times = np.array(gdf['time'])

    obs = np.array(gdf['snex_swe'])

    times1 = [datetime.strptime(item, '%Y-%m-%dT%H:%M') for item in times]

    days = [(item - times1[0]).total_seconds()/(24*3600.0) for item in times1]

    # convert times to datetime

    xtks = np.arange(days[0], np.round(days[-1]) + 2)

    # xtkslb = [(times1[0] + timedelta(item)).strftime("%m%d") for item in xtks]

    xtkslb = [str(int(item)) for item in xtks]

    start_time = times1[0].strftime("%Y%m%d")

    loc = gdf['location'].iloc[0]

    data_dic = {'location': loc, 'min': minv, 'mean': meanv, 'max': maxv, 'obs': obs}

    fig, ax = plt.subplots()
    # ax.plot(days, data_dic['min'], label='min', color='black')
    # ax.plot(days, data_dic['mean'], label='mean', color='blue')
    # ax.plot(days, data_dic['max'], label='max', color='red')
    # ax.plot(days, data_dic['obs'], label='obs SWE', color='green')

    ax.scatter(days, gdf['mean'], c='blue', label='mean',
               alpha=0.3, edgecolors='none')
    ax.scatter(days, gdf['snex_swe'], c='green', label='obs',
               alpha=0.3, edgecolors='none')

    ax.set_xticks(xtks, labels=xtkslb)
    ax.legend()

    corr = float("{:.2f}".format(corr))

    ax.text(0.8, 0.8, f'correlation: {corr}', color='red', transform=ax.transAxes)

    ax.set_title(f'{str(int(res))} m and time interval {timeint} Zonal Statistic of Snow Depth for {loc}')
    ax.set_xlabel(f'Observation day, days from staring {start_time}')
    ax.set_ylabel("snow depth, m")
    plt.show()


def draw_image(var, time: str):
    """
    Draw image at the time.
    :param var:
    :param time: for example '2021-03-21T13:33:18.000000000'.
    :return:
    """
    # draw the image at the time
    x, y = np.meshgrid(var.x, var.y)
    img1 = var.sel(time=time, method='nearest')
    plt.title(f'Snow Depth at Time {time[:10]}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    mgplot = plt.imshow(img1, cmap=plt.cm.RdBu)

    plt.show()


def draw_bar_plot_at_location(var, loc):
    # draw vector at the loc, loc is a list [lon,lat]
    ts1 = var.sel(y=loc[1], x=loc[0], method='nearest')

    plt.bar(ts1.time, ts1.data)

    plt.show()


def subset_dataset_via_box(var, bbox):
    # select the interesting area (AOI) based on bbox [min_lon, max_lon, min_lat, max_lat]

    min_lon = bbox[0]
    max_lon = bbox[2]
    min_lat = bbox[1]
    max_lat = bbox[3]

    # cropped_ds = ds.sel(y=slice(min_lat,max_lat), x=slice(min_lon,max_lon))

    mask_lon = (var.x >= min_lon) & (var.x <= max_lon)

    mask_lat = (var.y >= min_lat) & (var.y <= max_lat)

    cropped_ds = var.where(mask_lon & mask_lat, drop=True)

    return cropped_ds


def zonal_analyze_shapefile(ncfile, varname, shpfile):
    """Do zonal analysis of the variable in the ncfile with zone defined by shpfile.
    :param ncfile:
    :param varname:
    :param shpfile:
    :return:
    """
    nc_ds = xr.open_dataset(ncfile)

    shp_df = gpd.read_file(str(shpfile))

    mpolys = geometry.MultiPolygon([poly for poly in shp_df['geometry']])

    nc_var = nc_ds[varname]

    nc_var = nc_var.transpose('time', 'y', 'x')

    nc_var = nc_var.rio.set_spatial_dims(x_dim='x', y_dim='y')

    for poly in mpolys.geoms:

        gdf_poly = zonal_analyses(nc_var=nc_var, poly=poly)

        minv = [item[0]['min'] for item in gdf_poly['stat']]

        meanv = [item[0]['mean'] for item in gdf_poly['stat']]

        maxv = [item[0]['max'] for item in gdf_poly['stat']]

        bounds = tuple([float("{:.2f}".format(x)) for x in poly.bounds])

        data_dic = {'bounds': bounds, 'min': minv, 'mean': meanv, 'max': maxv}

        draw_line_plot(gdf_poly['time'], data_dic)

    print('completed zonal_analyses...')


# read the variable


# bT = bT.rio.set_spatial_dims(x_dim='lon', y_dim='lat')

def vertor_analyze(ncfile, varname, loc):
    """analyze the vector at the loc
    :param ncfile:
    :param varname:
    :param loc:[lon, lat]
    :return:
    """
    nc_ds = xr.open_dataset(ncfile)

    var = nc_ds[varname]

    var = var.transpose('time', 'y', 'x')

    var = var.rio.set_spatial_dims(x_dim='x', y_dim='y')

    # draw bar plot
    # loc = [43.5, -113.2]

    draw_bar_plot_at_location(var, loc)


def zonal_analyze_bbox(ncfile, varname, bbox=None, daterange=None, times=None):
    """zonal analysis of the variable with zone defined by bbox.
    :param ncfile:
    :param varname:
    :param bbox: [min_lon,min_lat, max_lon, max_lat], example [-113.2, 43.1, -113.1, 43.2].
    :return:
    """
    # select an AOI via bbox
    nc_ds = xr.open_dataset(ncfile)

    var = nc_ds[varname]

    var = var.transpose('time', 'y', 'x')

    var = var.rio.set_spatial_dims(x_dim='x', y_dim='y')

    # bbox = [-113.1, -113.2, 43.1, 43.2]

    # sub_var = subset_dataset_via_box(var, bbox)

    poly = geometry.MultiPolygon([bbox2polygon(bbox)])

    gdf_poly = zonal_analyses(nc_var=var, poly=poly)

    minv = [item[0]['min'] for item in gdf_poly['stat']]

    meanv = [item[0]['mean'] for item in gdf_poly['stat']]

    maxv = [item[0]['max'] for item in gdf_poly['stat']]

    bounds = tuple([float("{:.2f}".format(x)) for x in poly.bounds])

    data_dic = {'bounds': bounds, 'min': minv, 'mean': meanv, 'max': maxv}

    draw_line_plot(gdf_poly['time'], data_dic)


def write_geotiff(ncfile):
    '''
    var = get_var(ncfile)

    sd.rio.crs

    lat= var.y

    lat_cent = float(lat[int(len(lat)/2 - 1)])

    lon = var.x

    lon_cent = float(lon[int(len(lon)/2 - 1)])

    # crs = get_epsg_code(lon_cent,lat_cent)

    crs = var.rio.estimate_utm_crs().to_epsg()

    # Define the CRS projection

    # sd.rio.write_crs("epsg:4326", inplace=True)

    # save the GeoTIFF file:

    # sd.rio.to_raster(r"/home/jiangzhu/data/crrel/spicy-test/snow_depth.tif")

    # save the NetCDF file:

    var.to_netcdf('/home/jiangzhu/data/crrel/spicy-test/snow_depth_by_xarray.nc')

    '''


# main program

def main():
    parser = ArgumentParser()
    parser.add_argument('--ncfile', type=str,  required=True)
    parser.add_argument('--varname', type=str, default='snow_depth')
    parser.add_argument('--shpfile', type=str, default=None)
    parser.add_argument('--bbox', nargs="*", type=float, default=None)
    parser.add_argument('--location', nargs="*", type=float, default=None)
    parser.add_argument('--time', type=str, default=None)
    parser.add_argument('--daterange', nargs="*", type=str, default=None)
    parser.add_argument('--workdir', type=str, default='.')  
    
    args = parser.parse_args()

    # example
    #ncfile='/home/jiangzhu/data/crrel/sentinel1_snowEx21_ts_snow_pits_v1/sentinel1.nc'
    #varname='snow_depth'
    #shpfile=None
    #bbox=[-116.6707976743838 43.136861475176104 -114.87764927713005 44.7157595218886]
    #location=[-115, 43.5]
    #daterange=[2020-11-15, 2021-11-30]
    #time='2021-03-21T13:33:18.000000000'

    # zonal analysis with shapefile
    if args.shpfile:
        zonal_analyze_shapefile(ncfile=args.ncfile, varname=args.varname, shpfile=args.shpfile)

    # vector analysis with location
    if args.location:
        vertor_analyze(args.ncfile, args.varname, args.location)

    # zonal analysis with bbox
    if args.bbox:
        zonal_analyze_bbox(args.ncfile, args.varname, args.bbox)

    # Draw plot at time
    if args.time:
        var = get_var(args.ncfile, args.varname)
        draw_image(var=var, time=args.time)

    print("completed ...")


if __name__ == '__main__':
    main()
