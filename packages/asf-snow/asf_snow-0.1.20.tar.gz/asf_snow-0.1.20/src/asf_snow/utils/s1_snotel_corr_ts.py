import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import pandas as pd
from datetime import datetime
from shapely.geometry import Point
from asf_snow.utils.analyze_sentinel1_snow import *
from asf_snow.utils.analyze_snex import *

from pathlib import Path
import argparse
from asf_snow.utils.utils import write_polygon

def read_snotel(snotelfile:str=None, snotelsite:str=None, lon:float=None, lat:float=None, stdate:str=None, eddate:str=None):
    # Creamers' field
    # Latitude:	64.87
    # Longitude:	-147.74
    if snotelfile:
        filename = str(Path(snotelfile).stem)
        if filename.find("creamers") != -1 or filename.find("fieldinglake") != -1:
            snotel = read_snotel_sd_precip_ratio_temp(snotelfile, lon, lat, {})

        else:
            snotel = read_snotel_sd_precip_temp(snotelfile, lon, lat, {})
            # convert date string to datetime64
            snotel['Time'] = pd.to_datetime(snotel['Time'])
            # only consider stdate to eddate period
            if stdate and eddate:
                mask = (snotel['Time'] >= stdate) & (snotel['Time'] <= eddate)
                snotel = snotel[mask]

        snotel = snotel.set_index(['time'])
        snotel['Time'] = snotel.index
    else:
        snotel = get_snotel(snotelsite=snotelsite, stdate=stdate, eddate=eddate)
        snotel = snotel.set_index(['Time'])
        snotel['Time'] = snotel.index
    # merge snotel1 to s1_df
    # merged = pd.merge_asof(s1_df, snotel, on="time", direction="nearest")

    snotel['date'] = snotel.index.date

    return snotel

def get_sub_data(imgs, snotel, st_mmdd=None, ed_mmdd=None):
    if st_mmdd and ed_mmdd:
        st_year = int(imgs.time[0].dt.year)
        ed_year = int(imgs.time[-1].dt.year)
        st_datetime64 = np.datetime64(datetime.strptime(f'{st_year}-11-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        ed_datetime64 = np.datetime64(datetime.strptime(f'{ed_year}-04-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        ch = (imgs.time>st_datetime64).data & (imgs.time<ed_datetime64).data
        imgs1 =imgs.sel(time=imgs.time[ch])
    else:
        imgs1 = imgs

    snotel1 = snotel.iloc[snotel.index.get_indexer(imgs1.time, method='nearest')]

    # imgs1['snotel_sd'] = snotel1['snow_depth']
    # imgs1['temp_avg'] = snotel1['temp_avg']

    return imgs1, snotel1

def get_sub_imgs(imgs, st_mmdd=None, ed_mmdd=None):
    if st_mmdd and ed_mmdd:
        st_year = int(imgs.time[0].dt.year)
        ed_year = int(imgs.time[-1].dt.year)
        st_datetime64 = np.datetime64(datetime.strptime(f'{st_year}-11-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        ed_datetime64 = np.datetime64(datetime.strptime(f'{ed_year}-04-01 00:00:00', '%Y-%m-%d %H:%M:%S'))
        ch = (imgs.time>st_datetime64).data & (imgs.time<ed_datetime64).data
        imgs1 =imgs.sel(time=imgs.time[ch])
    else:
        imgs1 = imgs

    return imgs1


def calc_s1_snotel_correlation(imgs, snotel, st_mmdd=None, ed_mmdd=None,  y=None, x=None, average:float=None, res:float=None):
    imgs, snotel = get_nearest_pairs_within_threshold(imgs, snotel, thres_hours=12)

    # calculate the snow covering period only determined by st_mmd and ed_mmdd, typical st_mmdd and ed_mmdd are 11-01 and 04-01
    imgs1 = get_sub_imgs(imgs, st_mmdd=st_mmdd, ed_mmdd=ed_mmdd)

    s1_sd =  imgs1.snow_depth
    sd = imgs1.snotel_sd
    diff_sd = s1_sd - sd
    # following do not ignore the nan
    diff_mean = diff_sd.mean(dim =['time'], skipna=True)
    diff_std = diff_sd.std(dim=['time'], skipna=True)

    y,x,t = imgs1.snow_depth.shape
    corr = xr.corr(imgs1.snow_depth, imgs1.snotel_sd.expand_dims(y=y,x=x), dim=['time'])

    '''
    # calculate mean, std, and corr ignore the nan
    tn, yn, xn = imgs1.snow_depth.shape
    for y in range(yn):
        for x in range(xn):
            diff_mean.data[y,x ] = np.nanmean(s1_sd.data[:,y,x] - sd.data)
            diff_std.data[y,x] = np.nanstd(s1_sd.data[:,y,x] - sd.data)
            corr.data[y,x] = ma.corrcoef(ma.masked_invalid(s1_sd.data[:,y,x]), ma.masked_invalid(sd.data)).data[0,1]
    '''

    imgs['diff_mean'] = diff_mean
    imgs['diff_std'] = diff_std
    imgs['corr'] = corr

    return imgs


def write_to_netcdf(images:xr.Dataset, ncfile):

    images.to_netcdf(ncfile)


def get_nearest_pairs_within_threshold(imgs, snotel, thres_hours=12):
    # get the same points in time series
    snotel = snotel.drop_duplicates()
    snotel = snotel.sort_index()

    snotel = snotel.iloc[snotel.index.get_indexer(imgs.time, method='nearest')]
    snotel.loc[:, "time"] = imgs.time.data
    snotel = snotel.reset_index()
    ch1 = snotel.Time > imgs.time - np.timedelta64(thres_hours, 'h')
    ch2 = snotel.Time < imgs.time + np.timedelta64(thres_hours, 'h')
    ch = ch1 & ch2
    snotel = snotel[ch]
    snotel = snotel.set_index('time')
    imgs = imgs.sel(time=imgs.time.data[ch])
    imgs['snotel_sd'] = snotel['snow_depth']
    imgs['temp_avg'] = snotel['temp_avg']

    return imgs, snotel

def adjust_xlbs(ax, num=10):
    xtks = ax.get_xticks()
    xlbs = ax.get_xticklabels()
    if len(xtks) > num:
        xtks = xtks[::2]
        xlbs = xlbs[::2]

    ax.set_xticks(xtks, xlbs)


def draw_lines(imgs, snotel, outfile, y=None, x=None, average:float=None, res:float=None):

    imgs, snotel = get_nearest_pairs_within_threshold(imgs, snotel, thres_hours=12)

    snotel['time'] = snotel.index
    
    if average:
        # mean, std, and corr are based on time series of snow covering 11/1 to 4/1
        s1_sd = imgs.snow_depth.mean(dim=['y','x'])
        sd = snotel['snow_depth']
        # sd_nearest = sd.iloc[sd.index.get_indexer(s1_sd.time, method='nearest')]
        diff_sd = s1_sd - sd
        diff_mean = "{:.2f}".format(float(diff_sd.mean().data))
        diff_std = "{:.2f}".format(float(diff_sd.std().data))

        # calculate the corr within 11/1 to 4/1
        imgs1 = get_sub_imgs(imgs, st_mmdd='11-01', ed_mmdd='04-01')
        s1_sd1 = imgs1.snow_depth.mean(dim=['y', 'x'])

        s1_sd1 = np.array(s1_sd1)
        sd1 = np.array(imgs1.snotel_sd)

        diff_corr1 = "{:.2f}".format(float(ma.corrcoef(ma.masked_invalid(sd1), ma.masked_invalid(s1_sd1))[0,1]))

        # pay attention, VV and VH are in dB. you can not directly do mean, must convert to power unit to do mean
        vv = np.log10((10**imgs.sel(band='VV').s1).mean(dim=['y','x']))
        vh = np.log10((10**imgs.sel(band='VH').s1).mean(dim=['y','x']))
        cr = (10**imgs.sel(band='VH').s1 / 10**imgs.sel(band='VV').s1).mean(dim=['y','x'])
        cr  = imgs.deltaCR.mean(dim=['y','x'])
        deltavv = imgs.deltaVV.mean(dim=['y','x'])
        deltagamma = imgs.deltaGamma.mean(dim=['y','x'])
        wet_snow = imgs.wet_snow.mean(dim=['y','x'])
        wet_flag = imgs.wet_flag.mean(dim=['y','x'])
        perma_wet = imgs.perma_wet.mean(dim=['y','x'])
        alt_wet_flag = imgs.alt_wet_flag.mean(dim=['y','x'])
        wet_snow_flag = imgs.wet_snow_flag.mean(dim=['y','x'])
        fcf = imgs.fcf.mean(dim=['y','x']).mean()

    else:
        # mean, std, and corr are based on time series of snow covering 11/1 to 4/1
        s1_sd = imgs.snow_depth[:,y,x]
        sd = imgs.snotel_sd
        diff_sd = s1_sd - sd
        diff_mean = "{:.2f}".format(float(diff_sd.mean().data))
        diff_std = "{:.2f}".format(float(diff_sd.std().data))

        # calculate diff_corr1 for 11/1 to 4/1
        imgs1  = get_sub_imgs(imgs, st_mmdd='11-01', ed_mmdd='04-01')
        s1_sd1_arr = np.array(imgs1.snow_depth[:,y,x])
        sd1_arr = np.array(imgs1.snotel_sd)
        diff_corr1 = "{:.2f}".format(float(ma.corrcoef(ma.masked_invalid(sd1_arr), ma.masked_invalid(s1_sd1_arr))[0, 1]))

        ch = ~imgs.sel(band='VV').s1[:, y, x].isnull()
        vv = imgs.sel(band='VV').s1[:, y, x]
        vh = imgs.sel(band='VH').s1[:, y, x]
        cr = 10**imgs.sel(band='VH').s1[:, y, x] / 10**imgs.sel(band='VV').s1[:, y, x]
        cr = imgs.deltaCR[:, y, x]
        deltavv = imgs.deltaVV[:, y, x]
        deltagamma = imgs.deltaGamma[:, y, x]
        wet_snow = imgs.wet_snow[:, y, x]
        wet_flag = imgs.wet_flag[:, y, x]
        perma_wet = imgs.perma_wet[:, y, x]
        alt_wet_flag = imgs.alt_wet_flag[:, y,  x]
        # for time series of pixel at x, y, the value range 0 to 1
        wet_snow_flag = imgs.wet_snow_flag[:, y, x]
        fcf = imgs.fcf[:, y,x].mean()

    # do not show wet_snow_flag with time < 01-15
    ed_year = int(wet_snow_flag.time[-1].dt.year)
    date = np.datetime64(datetime.strptime(f'{ed_year}-01-15 00:00:00', '%Y-%m-%d %H:%M:%S'))
    wet_snow_flag[wet_snow_flag.time < date] = 0.

    time = imgs.time

    stdate = pd.to_datetime(time[0].data)
    stymd = stdate.strftime('%Y%m%d')
    eddate = pd.to_datetime(time[-1].data)
    edymd = eddate.strftime('%Y%m%d')
    date_range_str = f'{stymd}-{edymd}'

    # time_snowcover = imgs1.time


    #draw line plot

    # set global parameters for the figure

    params = {'legend.fontsize': 24, 'legend.handlelength': 2,
                  'axes.titlesize': 24,
                  'axes.labelsize': 24,
                  'xtick.labelsize': 22,
                  'ytick.labelsize': 22,
                  }
    plt.rcParams.update(params)

    '''
    # set global parameters for the figure
    params = {'legend.fontsize': 24, 'legend.handlelength': 2,
              'axes.titlesize': 24,
              'axes.labelsize': 22,
              'xtick.labelsize': 22,
              'ytick.labelsize': 22
              }
    plt.rcParams.update(params)
    '''

    # fig, ax = plt.subplots(nrows=5, ncols=1,constrained_layout = True)

    fig, ax = plt.subplots(nrows=6, ncols=1, constrained_layout=True)
    fig.set_figwidth(30)
    fig.set_figheight(30)
    # fig.set_size_inches(10.5, 10.5, forward=True)

    # fig.tight_layout()

    if imgs.attrs['orbit'] != 'all':
        orbit = str(int(imgs.attrs['orbit']))
    else:
        orbit = imgs.attrs['orbit']

    if average:
        if res:
            title = f'{date_range_str} SNOTEL and Averaged Snow Depth of S1 with orbit {orbit} in flight direction {imgs.attrs['flightDirection']} for {imgs.attrs['poi']} at Lon {imgs.attrs['lon']} and Lat {imgs.attrs['lat']} with res {res} m'
        else:
            title = f'{date_range_str} SNOTEL and Averaged Snow Depth of S1 with orbit {orbit} in flight direction {imgs.attrs['flightDirection']} for {imgs.attrs['poi']} at Lon {imgs.attrs['lon']} and Lat {imgs.attrs['lat']}'
    else:
        title = f'{date_range_str} SNOTEL and Snow Depth of S1 with orbit {orbit} in flight direction {imgs.attrs['flightDirection']} at the {imgs.attrs['poi']} with Lon {imgs.attrs['lon']} and Lat {imgs.attrs['lat']}'

    # fig.suptitle(title, fontsize=24)
    fig.suptitle(title, fontsize=24)

    # draw s1 and SNOTEL snow depth on the same panel

    ax[0].plot(time, s1_sd, 'o', label=f'Sentinel1 snow depth, r={diff_corr1}, S1 - SNOTEL mean {diff_mean}, diff_std {diff_std}', color='red')
    ax[0].plot(time, snotel['snow_depth'], 'x', label='SNOTEL snow depth, m', color='blue')
    #ax[0].plot(time, vh, 'o', label=f'VV in db', color='green')
    #ax[0].plot(time, cr, '^', label=f'VH/VV', color='blue')
    ax[0].legend()
    adjust_xlbs(ax[0])

    # draw vv in db
    # ax[1].plot(time, vh, 'x', label=f'Vh in db, fcf={"{:.2f}".format(fcf)}', color='blue')
    # ax[1].plot(time, vv, 'o', label=f'VV in db, fcf={"{:.2f}".format(fcf)}', color='red')
    # ax[1].plot(time, cr, '^', label=f'cr, fcf={"{:.2f}".format(fcf)}', color='black')

    ax[1].plot(time, cr, 'x', label=f'deltaCR, fcf={"{:.2f}".format(fcf)}', color='blue')
    ax[1].plot(time, deltavv, 'o', label=f'deltaVV', color='red')
    ax[1].plot(time, deltagamma, '^', label=f'deltaGamma', color='black')

    ax[1].legend()
    adjust_xlbs(ax[1])

    # draw average temperature
    line32 = np.zeros_like(snotel['time'], dtype=float)
    line32[:] = 32.0
    ax[2].plot(time, snotel['temp_avg'], 'x', label=f'avg temperature', color='blue')
    ax[2].plot(time, line32, label='32 F', color='black')

    # ax[1].plot(time, wet_snow, 'o', label=f'wet snow', color='blue')
    ax[2].legend()
    adjust_xlbs(ax[2])

    # perma_wet
    ax[3].plot(time, perma_wet, 'o', label=f'perma wet', color='green')
    ax[3].legend()
    adjust_xlbs(ax[3])
    # wet flag
    ax[4].plot(time, wet_flag, 'o', label=f'wet_flag', color='black')
    ax[4].legend()
    adjust_xlbs(ax[4])

    # wet_snow_flag
    ax[5].plot(time, wet_snow_flag*100.0, 'o', label=f'wet snow flag', color='pink')
    ax[5].set_ylim(0, 110)
    ax[5].legend()
    adjust_xlbs(ax[5])
    
    # Add point values
    for i, j in zip(time, wet_snow_flag*100.0):
        if j > 20.0:
            ts = pd.to_datetime(str(i.data))
            t = ts.strftime('%m/%d')
            ax[5].text(i, j, f'{t}\n{"{:.2f}".format(j)}', fontsize=12, ha='center', va='top')

    fig.savefig(outfile)
    # plt.xticks(xtks, xlbs)
    plt.show()

    return

def lonlat_to_colrow(geotransform, lon, lat):
    """
    Converts longitude and latitude coordinates to column and row indices using a geotransform.

    Args:
        geotransform: The geotransform of the raster dataset.
        lon: The longitude coordinate.
        lat: The latitude coordinate.

    Returns:
        A tuple of the column and row indices.
    """

    x_origin, pixel_width, _, y_origin, _, pixel_height = geotransform

    col = int((lon - x_origin) / pixel_width)
    row = int((y_origin - lat) / abs(pixel_height))

    return col, row

def point(lon, lat, geojsonfile):
    point = Point(lon, lat)


def readgeojson(geojsfile):

    f = open(geojsfile)

    jsstr = json.load(f)

    return geometry.shape(jsstr)


def get_gt(nc_ds):
    v = nc_ds.spatial_ref.GeoTransform.split(' ')
    gt = tuple([float(j) for j in v])
    return gt


def main():
    '''
    s1file = "/media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/both/sentinel1_creamers_20230801_20240731_1k_both_n2d0_std.nc"

    snotelfile = "/media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/creamers_20230801_20240731_sd_precip_temp_ratio.txt"

    snotellon = -147.74

    snotellat = 64.87

    average = True

    lon=
    lat=
    outfile = "/media/jiangzhu/Elements/crrel/SNOTEL/creamers/20230801_20240731/both/ts_vv_n2d0_std_avg.png"

    If user doe not input lon and lat for POI, the defaylt POI is at snotellon, snotellat.
    If average is True, the result is for the time series of the zonal averages of the images

    '''



    def _t_or_f(arg):
        ua = str(arg).upper()
        if 'TRUE'.startswith(ua):
            return True
        elif 'FALSE'.startswith(ua):
            return False
        else:
            pass  #error condition maybe?

    parser = argparse.ArgumentParser()
    parser.add_argument('--s1file', type=str, required=True)

    parser.add_argument('--snotelfile', type=str, default=None)
    parser.add_argument('--snotellon', type=float, default=None)
    parser.add_argument('--snotellat', type=float, default=None)

    parser.add_argument('--snotelsite', type=str, help='1302:AK:SNTL', default=None)
    parser.add_argument('--stdate', type=str, help='2023-08-01', default=None)
    parser.add_argument('--eddate', type=str, help='2024-07-31', default=None)

    parser.add_argument('--avg', type=_t_or_f)
    parser.add_argument('--res', type=float, default=None)
    parser.add_argument('--lon', type=float, default=None)
    parser.add_argument('--lat', type=float, default=None)

    parser.add_argument('--x', type=int, default=None)
    parser.add_argument('--y', type=int, default=None)

    parser.add_argument('--outfile', type=str, default=None)

    args = parser.parse_args()

    nc_ds = xr.open_dataset(args.s1file, decode_coords="all")

    nc_ds = nc_ds.transpose('time','band','y','x',...)

    nc_ds = nc_ds.sortby('time')

    # write boundary as polygon
    s1_poly = bbox2polygon(list(nc_ds.snow_depth.rio.bounds()))
    write_polygon(s1_poly, args.outfile.replace(".png", "_s1.geojson"))

    orbit_numbers = np.unique(nc_ds.relative_orbit)

    if args.snotelfile:
        snotel = read_snotel(snotelfile=args.snotelfile, lon=args.snotellon,lat=args.snotellat)
    else:
        snotel = read_snotel(snotelsite=args.snotelsite, stdate=args.stdate, eddate=args.eddate)

    # convert args.lon, args.lat to col/x and row/y
    gt = get_gt(nc_ds)

    if args.x and args.y:
        x = args.x
        y = args.y
        lon = nc_ds.x[x]
        lat = nc_ds.y[y]
    elif args.lon and args.lat:
        x, y = lonlat_to_colrow(gt, args.lon, args.lat)
        lon = args.lon
        lat = args.lat
    else:
        x, y = lonlat_to_colrow(gt, args.snotellon, args.snotellat)
        lon = args.snotellon
        lat = args.snotellat

    nc_ds.attrs['lon'] = lon
    nc_ds.attrs['lat'] = lat
    nc_ds.attrs['orbit'] = 'all'

    # if average, clip the nc_ds with lon, lat, and res
    if args.avg and args.res:
        poly = polygon_via_point(lon=lon, lat=lat, resolution=args.res)
        jsstr = to_geojson(poly)
        geometries = [json.loads(jsstr)]
        nc_ds = nc_ds.rio.clip(geometries, all_touched=True)
        # write boundary as polygon
        s1_poly_clipped = bbox2polygon(list(nc_ds.snow_depth.rio.bounds()))
        write_polygon(s1_poly_clipped, args.outfile.replace(".png", "_s1_clipped.geojson"))

        # get x and y
        gt = get_gt(nc_ds)
        x, y = lonlat_to_colrow(gt, lon, lat)

    # draw combination of all orbits
    snowcover = calc_s1_snotel_correlation(nc_ds, snotel, st_mmdd='11-01', ed_mmdd='04-01')
    outfile = args.outfile.replace(".png",".nc")
    write_to_netcdf(snowcover, outfile)

    draw_lines(nc_ds, snotel, outfile=args.outfile, y=y, x=x, average=args.avg, res=args.res)

    '''
    # draw each orbit
    for orbit in orbit_numbers:
        imgs  = nc_ds.sel(time=nc_ds.time[nc_ds.relative_orbit==orbit])
        imgs.attrs['orbit'] = orbit
        outfile1 = args.outfile.replace(".png",f'_{int(orbit)}.png')
        draw_lines(imgs, snotel, outfile1, y=y, x=x, average=args.avg, res=args.res)
    '''
if __name__=='__main__':
    main()
