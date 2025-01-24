from pathlib import Path
import sys
import os
import glob
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

import numpy as np
import numpy.ma as ma
import xarray
import rioxarray as rio
from rasterio.enums import Resampling
from osgeo import gdal
from asf_snow.utils.utils import *
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import mpl_scatter_density # adds projection='scatter_density'
from matplotlib.colors import LinearSegmentedColormap

from asf_snow.utils.analyze_sentinel1_snow import *
from asf_snow.utils.analyze_snex import *

import pickle

# compare the snow depth derived with sentinel1 to NASA SnowEx experiment Lidar snow depth data
# example arguments
# ncfile = "/home/jiangzhu/data/crrel/sentinel1_snowEx21_ts_snow_pits_v1/sentinel1.nc"
# lidarfile = "/home/jiangzhu/data/crrel/SnowEx20-21_QSI_Lidar_Snow_Depth_0d5m_UTM_Grid_V1/SNEX20_QSI_SD_0.5M_USIDBS_20200218_20200219.tif"
# varname = "snow_depth"
# res = 100  # zonal analysis square size

def get_geotransform(data:xarray):
    gt_str = data.spatial_ref.GeoTransform
    gt = [float(item) for item in gt_str.split(' ')]
    return gt

def get_bounds(gt, xsize, ysize):
    xn = gt[0] + gt[1]*xsize
    yn = gt[3] + gt[5]*ysize
    return [gt[0], yn, xn, gt[3]]


def resample(src: xarray.DataArray,  ref: xarray.DataArray):
    # use gdawrap to resample

    dst_xsize = ref.shape[2]

    dst_ysize = ref.shape[1]

    dst_bound = ref.rio.bounds()

    #kwargs = {"width": dst_xsize, "height": dst_ysize, "outputBounds": dst_bound, "format": "GTiff"}

    src.rio.to_raster('/tmp/src.tif')

    #ds = gdal.Warp('/tmp/sample.tif', '/tmp/src.tif', **kwargs)

    #dst = rio.open_rasterio("/tmp/sample.tif")
    if os.path.exists('/tmp/sample.tif'):
        os.system('/bin/rm /tmp/sample.tif')
    # cmd = f'gdalwarp -te {dst_bound[0]}  {dst_bound[1]} {dst_bound[2]} {dst_bound[3]} -ts {dst_xsize} {dst_ysize} /tmp/src.tif /tmp/sample.tif'

    cmd = f'gdalwarp -r average -te {dst_bound[0]}  {dst_bound[1]} {dst_bound[2]} {dst_bound[3]} -ts {dst_xsize} {dst_ysize} /tmp/src.tif /tmp/sample.tif'
    # gdalwarp -te 637308.612295736 4894974.424383238 652555.8674305859 4911581.307364508 -ts 157 171 lidar.tif lidar_sample_te_ts.ti

    os.system(cmd)

    dst = rio.open_rasterio('/tmp/sample.tif')

    return dst

def calc_rmse(x, y):
    xm = ma.masked_invalid(x)
    ym = ma.masked_invalid(y)
    return np.sqrt(((xm - ym) ** 2).mean())


def calc_corr(y,x):
    """
    calculate the r and mbe
    :param y: ground true
    :param x: measurement
    :return: r, mbe
    """
    x = ma.masked_invalid(x)
    y = ma.masked_invalid(y)
    # if x and y are 2D, flatten them
    if x.ndim == 2:
        x = x.flatten()
        y = y.flatten()
    # get rid of nan data
    invalid_msk = x.mask | y.mask

    x = x[~invalid_msk]
    y = y[~invalid_msk]

    # calculate the correlation coefficent
    r = np.corrcoef(y,x)

    # calculate the mean bias error
    mbe = np.mean(y - x)
    return r[0,1], mbe

def str2datetime64(dtstr, format="%Y-%m-%d %H:%M:%S.%f"):
    dt = datetime.strptime(dtstr, format)
    dt64 = np.datetime64(dt)
    return dt64


def get_datetime_range(xml):
    tree = ET.parse(xml)

    root = tree.getroot()

    metadata  = root.findall('./GranuleURMetaData')

    rangedatetime = metadata[0].findall('./RangeDateTime')

    ed_date = rangedatetime[0].find('RangeEndingDate').text
    ed_time = rangedatetime[0].find('RangeEndingTime').text
    st_date = rangedatetime[0].find('RangeBeginningDate').text
    st_time = rangedatetime[0].find('RangeBeginningTime').text

    ed_str = f'{ed_date} {ed_time}'

    ed_dt64 = str2datetime64(ed_str)

    st_str = f'{st_date} {st_time}'

    st_dt64 = str2datetime64(st_str)

    return st_str, ed_str

def str2datetime(str, format="%Y-%m-%d %H:%M:%S.%f"):
    return datetime.strptime(str, format)


def scatter_plot(x, y, outfile):
    x = ma.masked_invalid(x)
    y = ma.masked_invalid(y)
    # if x and y are 2D, flatten them
    if x.ndim == 2:
        x = x.flatten()
        y = y.flatten()
    # get rid of nan data
    invalid_msk = x.mask | y.mask

    x = x[~invalid_msk]
    y = y[~invalid_msk]

    ch = np.bitwise_and(x >= 0, y >= 0)
    x = x[ch]
    y = y[ch]

    slope, intercept = np.polyfit(x, y, deg=1)
    ye = slope*x + intercept
    slope1 = round(slope, 2)
    intercept1 = round(intercept, 2)

    rmse = round(np.sqrt(((x - y) ** 2).mean()), 2)

    r = np.corrcoef(y,x)
    coeff = r[0,1]
    coeff = round(coeff, 2)

    n = x.shape[0]

    fig, ax = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(8)

    # histogram definition
    bins = [100, 100]  # number of bins

    # histogram the data
    hh, locx, locy = np.histogram2d(x, y, bins=bins)

    # Sort the points by density, so that the densest points are plotted last
    z = np.array([hh[np.argmax(a <= locx[1:]), np.argmax(b <= locy[1:])] for a, b in zip(x, y)])
    idx = z.argsort()
    x2, y2, z2 = x[idx], y[idx], z[idx]

    fig.clf()
    sc = plt.scatter(x2, y2, c=z2, cmap='jet', marker='.')
    ax = sc._axes
    ax.set_xlabel('Lidar Snow Depth (m)')
    ax.set_ylabel('S1 Snow Depth (m)')
    ax.plot(x,ye)

    # ax.legend(loc='best')  # in order to display label, you have to use ax.legend
    ax.text(0.5, 0.95, f'RMSE {rmse}, R {coeff}, n {n}', color='black', transform = ax.transAxes)
    ax.set_xlim((0,7))
    ax.set_ylim((0,7))
    plt.colorbar(sc, label="Pixel Counts")
    ax.legend()
    plt.show()

    # create directory if not exist
    Path(outfile).parent.mkdir(exist_ok=True)

    fig.savefig(outfile)


def compare_sentinel1_snow_depth_to_lidar(ncfile, varname, lidarfile, location, res, timeint, timethresh, base, method,
                                         precip):

    work_dir = str(Path(ncfile).parent)

    # sentinel1 snow depth data
    nc_var = get_var(ncfile, varname)

    # NASA snowEx Lidar snow depth data

    lidar = rio.open_rasterio(lidarfile)

    xml = lidarfile +'.xml'

    st_dt64, ed_dt64 = get_datetime_range(xml)


    lidar = lidar.assign_attrs({'start_datetime': st_dt64, 'end_datetime': ed_dt64 })

    # reproject the lidar to WGS84
    lidar = lidar.rio.reproject('EPSG:4326')

    # remove non-sense data in the lidar dataset
    lidar = lidar.where(lidar < 1e9).where(lidar >= 0)

    # set nodata of lidar dataset as np.nan
    if type(lidar) == xr.DataArray:
        lidar = lidar.rio.write_nodata(np.nan)
    else:
        for var in lidar:
            lidar[var] = lidar[var].rio.write_nodata(np.nan)

    # clip S1 data (nc_var)
    bbox = lidar.rio.bounds()
    nc_var_clipped = nc_var.rio.clip_box(*bbox)

    # reproject both lidar based on nc_var_clipped
    lidar_sample = lidar.rio.reproject_match(nc_var_clipped, resampling=Resampling.average, nodata=np.nan)

    # merge nc_var and lidar datasets
    # ds = xr.merge([nc_var, lidar], combine_attrs='drop_conflicts')

    # pick the image from the nc_var_clipped with the time is in the range of the st_time and ed_time
    # Banner, idaho, time zoom -6 hours
    t_st = str2datetime(lidar_sample.start_datetime) - timedelta(hours=6)
    t_ed = str2datetime(lidar_sample.end_datetime) - timedelta(hours=6)

    nc_timerange = nc_var_clipped.sel(time=slice(t_st, t_ed))

    # calculate the RMSE, R, and MBE
    rmse = calc_rmse(lidar_sample[0].data, nc_timerange[0].data)

    r, mbe = calc_corr(lidar_sample[0].data, nc_timerange[0].data)

    print(f'RMSE {rmse}, r {r}, mbe {mbe}')

    # draw spot plot and save it
    outfile = f'{work_dir}/{str(Path(ncfile).stem)}_{varname}_{str(Path(lidarfile).stem)}.png'

    f = open(f'{work_dir}/store.pckl', 'wb')
    pickle.dump([lidar_sample[0].data,nc_timerange[0].data], f)
    f.close()

    scatter_plot(lidar_sample[0].data, nc_timerange[0].data, outfile)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--ncfile', type=str,  required=True)
    parser.add_argument('--varname', type=str, default='snow_depth')
    parser.add_argument('--lidarfile', type=str,  required=True)
    parser.add_argument('--location', type=str, default='Boise')
    parser.add_argument('--res', type=float, default=100)
    parser.add_argument('--timeint', type=int, default=24)
    parser.add_argument('--timethresh', type=int, default=6)
    parser.add_argument('--base', choices=['snex', 's1'], default='s1')
    parser.add_argument('--method', choices=['nearest', 'average', 'close',
                                             'nearest', 'average', 'close'])
    parser.add_argument('--precip', choices=['y', 'n'], default='y')

    args = parser.parse_args()

    compare_sentinel1_snow_depth_to_lidar(args.ncfile, varname=args.varname, lidarfile=args.lidarfile,
                                         location=args.location, res=args.res, timeint=args.timeint,
                                         timethresh=args.timethresh, base=args.base, method=args.method,
                                         precip=args.precip)

    print('completed analysis...')
