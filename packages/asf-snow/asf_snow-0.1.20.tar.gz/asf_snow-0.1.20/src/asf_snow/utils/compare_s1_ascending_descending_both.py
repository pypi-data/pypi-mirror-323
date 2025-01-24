import sys

import numpy as np

from asf_snow.utils.analyze_sentinel1_snow import *
from asf_snow.utils.analyze_snex import *
from asf_snow.utils.utils import write_polygon
from shapely import geometry, to_geojson

import json


def readgeojson(geojsfile):

    f = open(geojsfile)

    jsstr = json.load(f)

    return geometry.shape(jsstr)


def calc_statistic(merged):
    # claculate the statistic
    corr = merged['snow_depth_y'].corr(merged['snow_depth_x'])
    corr = float("{:.2f}".format(corr))
    mean = (merged['snow_depth_y'] - merged['snow_depth_x']).mean()
    mean = float("{:.2f}".format(mean))
    std = (merged['snow_depth_y'] - merged['snow_depth_x']).std()
    std = float("{:.2f}".format(std))
    min = (merged['snow_depth_y'] - merged['snow_depth_x']).min()
    min = float("{:.2f}".format(min))
    max = (merged['snow_depth_y'] - merged['snow_depth_x']).max()
    max = float("{:.2f}".format(max))

    st = pd.to_datetime(merged.Time_x.iloc[0])
    st_date = st.strftime('%Y-%m-%d')
    ed = pd.to_datetime(merged.Time_x.iloc[-1])
    ed_date = ed.strftime('%Y-%m-%d')
    return {'corr': corr, 'mean': mean, 'std': std, 'min': min, 'max': max,'st_date': st_date, 'ed_date': ed_date}



def draw_asc_desc_lines(merged_asc, merged_desc, merged, loc, outfile):

    # merged = pd.merge_asof(s1_df, snotel, on="time", direction="nearest")
    merged_asc = merged_asc[~merged_asc['snow_depth_y'].isnull()]
    merged_desc = merged_desc[~merged_desc['snow_depth_y'].isnull()]
    merged = merged[~merged['snow_depth_y'].isnull()]

    stat_asc = calc_statistic(merged_asc)
    stat_desc = calc_statistic(merged_desc)
    stat = calc_statistic(merged)

    # set global parameters for the figure
    params = {'figure.figsize': (30, 30),
              'legend.fontsize': 20, 'legend.handlelength': 2,
              'axes.titlesize': 22,
              'axes.labelsize': 20,
              'xtick.labelsize': 20,
              'ytick.labelsize': 20
              }
    plt.rcParams.update(params)

    #if 'snow_rain_ratio' in merged.columns:
    #    fig, ax = plt.subplots(nrows=5, ncols=1)
    #else:
    #    fig, ax = plt.subplots(nrows=4, ncols=1)
    
    fig, ax = plt.subplots(nrows=5, ncols=1)

    if merged.attrs['res']:
        title = (f'SNOTEL and S1 Snow Depth Averaged over {merged.attrs['res']} m Resolution of the '
                 f'{merged.attrs['location'].capitalize()}'
                 f' during the {stat['st_date']} to {stat['ed_date']} Period')
    else:
        title = (f'SNOTEL and S1 Snow Depth Averaged over the AOI of the {merged.attrs['location'].capitalize()})'
                 f' during the {stat['st_date']} to {stat['ed_date']} Period')

    fig.suptitle(title, fontsize=24)

    # draw s1 and SNOTEL snow depth on the same panel

    fcf_ratio = float("{:.2f}".format(merged.attrs['fcf_ratio']))
    # ax[0].plot(merged['date'], merged['snow_depth_x'],
    #           label=f'SNOTEL Snow Depth, R = {stat['corr']}, FC ratio {fcf_ratio} '
    #                 f'S1-SNOTEL: min {stat['min']}, mean {stat['mean']}, max {stat['max']},'
    #                 f'std {stat['std']}', color='red')

    ax[0].plot(merged['date'], merged['snow_depth_x'],
               label=f'SNOTEL Snow Depth, R = {stat['corr']}', color='blue')
    ax[0].plot(merged['date'], merged['snow_depth_y'],
               label=f'S1 Snow Depth, xsize={merged.attrs['xsize']},'
                     f' ysize={merged.attrs['ysize']}', color='black')
    ax[0].plot(merged_asc['date'], merged_asc['snow_depth_y'], label=f'Ascending S1 Snow Depth, R = {stat_asc['corr']}', color='green')
    ax[0].plot(merged_desc['date'], merged_desc['snow_depth_y'], label=f'Descending S1 Snow Depth, R = {stat_desc['corr']}', color='red')

    ax[0].legend()

    # temperature and 32F line
    line32 = np.zeros_like(merged['date'], dtype=float)
    line32[:] = 32.0
    ax[1].plot(merged['date'], merged['temp_avg'], label='Temperature', color='red')
    ax[1].plot(merged['date'], line32, label='32 F', color='black')
    ax[1].legend()

    # vh_mean
    ax[2].plot(merged['date'], merged['vh_mean'], label='VH, db', color='black')
    ax[2].plot(merged_asc['date'], merged_asc['vh_mean'], label='ascending VH, db', color='green')
    ax[2].plot(merged_desc['date'], merged_desc['vh_mean'], label='descending VH, db', color='red')
    ax[2].legend()

    # vv_mean
    ax[3].plot(merged['date'], merged['vv_mean'], label='VV, db', color='black')
    ax[3].plot(merged_asc['date'], merged_asc['vv_mean'], label='ascending VV, db', color='green')
    ax[3].plot(merged_desc['date'], merged_desc['vv_mean'], label='descending VV, db', color='red')
    ax[3].legend()

    
    ax[4].plot(merged['date'], merged['cr_mean'], label='CR Ratio, db', color='black')
    ax[4].plot(merged_asc['date'], merged_asc['cr_mean'], label='ascending CR Ratio, db', color='green')
    ax[4].plot(merged_desc['date'], merged_desc['cr_mean'], label='descending CR Ratio, db', color='red')
    ax[4].legend()

    '''
    # precipitation
    ax[3].plot(merged['date'], merged['precip_inc'], label='precip increment, m', color='red')
    ax[3].legend()

    # snow-rain-ratio
    if 'snow_rain_ratio' in merged.columns:
        ax[4].plot(merged['date'], merged['snow_rain_ratio'], label='snow-rain-ratio',color='blue')
        ax[4].legend()
    '''

    if outfile:
        # create directory if not exist
        Path(outfile).parent.mkdir(exist_ok=True)
        fig.savefig(outfile)

    plt.show()

def draw_multiple_bars(merged, outfile):
    # when calculating corr, get rid of NAN data
    merged = merged[~merged['snow_depth_y'].isnull()]
    corr = merged['snow_depth_y'].corr(merged['snow_depth_x'])
    corr = float("{:.2f}".format(corr))

    st_date = merged['Time_x'].iloc[0].strftime('%Y-%m-%d')
    ed_date = merged['Time_x'].iloc[-1].strftime('%Y-%m-%d')

    # set global parameters for the figure
    params = {'legend.fontsize': 20, 'legend.handlelength': 2,
              'axes.titlesize': 22,
              'axes.labelsize': 20,
              'xtick.labelsize': 20,
              'ytick.labelsize': 20
              }
    plt.rcParams.update(params)

    # if 'snow_rain_ratio' in merged.columns:
    #    fig, [ax0, ax1, ax2, ax3, ax4] = plt.subplots(nrows=5, ncols=1)
    # else:

    # fig, [ax0, ax1, ax2, ax3] = plt.subplots(nrows=4, ncols=1)

    fig, ax = plt.subplots(nrows=4, ncols=1)
    fig.set_figwidth(30)
    fig.set_figheight(30)
    # fig.suptitle('This is a somewhat long figure title', fontsize=16)

    if merged.attrs['res']:
        title = f'SNOTEL and {merged.attrs['flightdir']} S1 Snow Depth Averaged over {merged.attrs['res']} m Resolution of the {merged.attrs['location'].capitalize()} during the {st_date} to {ed_date} Period'
    else:
        title = f'SNOTEL and {merged.attrs['flightdir']} S1 Snow Depth Averaged over the AOI of the {merged.attrs['location'].capitalize()} during the {st_date} to {ed_date} Period'

    fig.suptitle(title, fontsize=24)

    # increase the size of labels
    # [i.tick_params(axis='both', which='major', labelsize=20) for i in ax]
    # [i.tick_params(axis='both', which='minor', labelsize=20) for i in ax]



    time = pd.to_datetime(merged['Time_x'])
    # time = time.dt.strftime('%d')
    x = np.arange(len(time))

    width = 0.25  # the width of the bars
    multiplier = 0

    snow_depths = {'s1_snow_depth': merged['snow_depth_y'], 'snotel_snow_depth': merged['snow_depth_x']}

    for attribute, measurement in snow_depths.items():
        offset = width * multiplier
        if multiplier == 0:
            lbl = f'{attribute}, R={corr}'
        else:
            lbl = f'{attribute}'

        rects = ax[0].bar(x + offset, measurement, width, label=lbl)
        # ax0.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax[0].set_ylabel('Snow Depth, m')
    ax[0].set_title('S1 and SNOTEL Snow Depth')

    xtks = ax[0].get_xticks()

    xtks1 =xtks[1: len(xtks)-1]

    xtknames1 = [time[time.index[int(x[int(i)])]].strftime('%Y-%m-%d') for i in xtks1]

    ax[0].set_xticks(xtks1 + width, xtknames1)
    #ax[0].tick_params(axis='both', which='major', labelsize=20)
    #ax[0].tick_params(axis='both', which='minor', labelsize=15)
    ax[0].legend(loc='upper left', ncols=2)
    # ax[0].set_ylim(0, 250)

    # temperature and 32F line
    merged_line32 = np.zeros_like(x, dtype=float)
    merged_line32[:] = 32.0
    # ax1.plot(snotel['Time'], snotel['temp_avg'], label='Temperature', color='red')
    ax[1].plot(x, merged['temp_avg'], label='Daily Average Air Temperature', color='red')
    ax[1].plot(x, merged_line32, label='32 F', color='blue')
    ax[1].set_ylabel('Temperature, degree F')
    ax[1].set_xticks(xtks1, xtknames1)
    ax[1].legend()

    # cross-polarization ratio
    ax[2].plot(x, merged['cr_mean'], label='Cross-Polarization Ratio', color='blue')
    ax[2].set_xticks(xtks1, xtknames1)
    ax[2].set_ylabel('VH/VV Ratio')
    ax[2].legend()

    # precipitation
    # ax3.plot(snotel['Time'], snotel['precip_inc'], label='precip increment, m', color='red')
    # ax3.plot(x, merged['precip_inc'], label='precip increment, m', color='red')
    rects = ax[3].bar(x, merged['precip_inc'], width, label = 'Precipitation Increment')
    # ax3.bar_label(rects, padding=3)
    ax[3].set_xticks(xtks1, xtknames1)
    ax[3].set_ylabel('Precipitation, m')
    ax[3].legend()

    '''
    # snow-rain-ratio
    if 'snow_rain_ratio' in merged.columns:
        # ax4.plot(snotel['Time'], snotel['snow_rain_ratio'], label='snow-rain-ratio',color='blue')
        # ax4.plot(merged['Time'], merged['snow_rain_ratio'], label='snow-rain-ratio', color='blue')
        data={'snow_rain_ratio': merged['snow_rain_ratio']}
        rects = ax4.bar(x,  data['snow_rain_ratio'], width, label='snow_rain_ratio')
        ax4.set_ylabel('Ratio')
        ax4.set_title('Snow Rain Ratio')
        ax4.set_xticks(x + width, time)
        ax4.legend()
    '''

    if outfile:
        # create directory if not exist
        Path(outfile).parent.mkdir(exist_ok=True)
        fig.savefig(outfile)

    plt.show()


def get_stdate_eddate_from_file(s1_file):
    nc_ds = xr.open_dataset(s1_file, decode_coords="all")
    st = nc_ds.time[0].values
    ed= nc_ds.time[-1].values
    stdate = datetime.strftime(pd.Timestamp(st).to_pydatetime(),'%Y-%m-%d')
    eddate = datetime.strftime(pd.Timestamp(ed).to_pydatetime(), '%Y-%m-%d')

    return stdate, eddate


def clip_s1(s1_file, lon, lat, aoi: None, res: None, stdate: None, eddate: None):
    nc_ds = xr.open_dataset(s1_file, decode_coords="all")

    if (nc_ds.flight_dir.values == 'ascending').all():
        flightdir = 'ascending'
    elif (nc_ds.flight_dir.values == 'descending').all():
        flightdir = 'descending'
    else:
        flightdir = 'both'

    # if stdate and eddate, only keep data from stdate to eddata, normally form 11/15 to 3/15
    if stdate and eddate:
        nc_ds = nc_ds.sel(time=slice(stdate, eddate))

    # test purpose
    s1_polybbox = bbox2polygon(list(nc_ds.snow_depth.rio.bounds()))
    write_polygon(s1_polybbox, s1_file.replace(".nc", "_s1_output.geojson"))

    # clip by the AOI or by box of 500m around the lon, lat
    if aoi:
        # geojsfile = "/media/jiangzhu/Elements/crrel/SNOTEL/creamers/creamers.geojson"
        poly = readgeojson(aoi)
    elif res:
        poly = polygon_via_point(lon=lon, lat=lat, resolution=res)
        write_polygon(poly, s1_file.replace(".nc", f'_rectangular_{res}.geojson'))
        # poly = geometry.box(*poly.bounds)
    else:
        poly = None

    if poly:
        jsstr = to_geojson(poly)
        geometries = [json.loads(jsstr)]
        nc_ds = nc_ds.rio.clip(geometries, all_touched=True)
        xsz = len(nc_ds.snow_depth.x)
        ysz = len(nc_ds.snow_depth.y)
        tot_num = nc_ds.fcf.data.size
        forest_num = nc_ds.fcf.data[nc_ds.fcf.data >= 0.5].size
        fcf_ratio = forest_num / float(tot_num)

    # test purpose

    s1_clipped = bbox2polygon(list(nc_ds.snow_depth.rio.bounds()))
    write_polygon(s1_clipped, s1_file.replace(".nc", "_s1_clipped.geojson"))

    # calculate the cr, cr_mean
    s1_sd_mean = nc_ds.snow_depth.mean(axis=(0, 1))

    vh = 10 ** nc_ds.s1.sel(band='VH')
    vh_mean = vh.mean(axis=(1, 2))
    vh_mean = vh_mean.reset_coords('band', drop=True)

    vv = 10 ** nc_ds.s1.sel(band='VV')
    vv_mean = vv.mean(axis=(1, 2))
    vv_mean = vv_mean.reset_coords('band', drop=True)

    cr = vh / vv
    cr_mean = cr.mean(axis=(1, 2))

    # convert vv_mean, vh_mean, and cr_mean in db
    vh_mean = np.log10(vh_mean)
    vv_mean = np.log10(vv_mean)
    cr_mean = np.log10(cr_mean)

    # add cr_mean to s1_sd_mean
    s1_merged = xr.merge([s1_sd_mean, vh_mean.rename('vh_mean'), vv_mean.rename('vv_mean'), cr_mean.rename('cr_mean')])
    s1_df = s1_merged.to_dataframe()
    s1_df['Time'] = s1_df.index
    # get location
    str_list = Path(s1_file).stem.split("_")
    loc = str_list[1]
    st = str_list[2]
    ed = str_list[3]

    s1_df['date'] = s1_df.index.date

    s1_df.attrs['location'] = loc
    s1_df.attrs['lon'] = lon
    s1_df.attrs['lat'] = lat
    s1_df.attrs['st_date'] = stdate
    s1_df.attrs['ed_date'] = eddate
    s1_df.attrs['res'] = res
    s1_df.attrs['xsize'] = xsz
    s1_df.attrs['ysize'] = ysz
    s1_df.attrs['fcf_ratio'] = fcf_ratio
    s1_df.attrs['flightdir'] = flightdir

    return s1_df


def clip_snotel(snotel_file, lon, lat, stdate: None, eddate: None):
    filename = str(Path(snotel_file).stem)

    if filename.find("creamers") != -1 or filename.find("fieldinglake") != -1:
        snotel = read_snotel_sd_precip_ratio_temp(snotel_file, lon, lat, {})
    else:
        snotel = read_snotel_sd_precip_temp(snotel_file, lon, lat, {})

    # convert date string to datetime64
    snotel['Time'] = pd.to_datetime(snotel['Time'])

    # only consider stdate to eddate period
    if stdate and eddate:
        mask = (snotel['Time'] >= stdate) & (snotel['Time'] <= eddate)
        snotel = snotel[mask]

    snotel = snotel.set_index(['time'])

    # merge snotel1 to s1_df
    # merged = pd.merge_asof(s1_df, snotel, on="time", direction="nearest")

    snotel['date'] = snotel.index.date

    return snotel

def concat_snotel_s1(snotel, s1):
    # snotel with x, s1_df with y
    merged = pd.merge(snotel, s1, on='date', how='outer')
    merged.attrs = s1.attrs
    merged = merged[~merged.Time_x.isnull()]
    return merged


def compare_s1_ascending_descending_both(s1_asc_file, s1_desc_file, s1_file, snotel_file, lon, lat, aoi: None, res: None, stdate: None, eddate: None, outfile: None):
    # read the nc_ds
    # for example, creamers' field   # Creamers' field, Latitude:	64.87, Longitude:	-147.74
    # stdate and eddate are yyyy-mm-dd, typical stdate='2021-11-15', eddate='2022-03-15'

    # since s1_asc have the least time period, use s1_asc time period to cut off the s1_desc and s1_both



    s1_asc = clip_s1(s1_asc_file, lon, lat, aoi=aoi, res=res, stdate=stdate, eddate=eddate)

    s1_desc = clip_s1(s1_desc_file, lon, lat, aoi=aoi, res=res, stdate=stdate, eddate=eddate)

    s1 = clip_s1(s1_file, lon, lat, aoi=aoi, res=res, stdate=stdate, eddate=eddate)

    # read snotel
    snotel = clip_snotel(snotel_file, lon, lat, stdate=stdate, eddate=eddate)

    # merge snotel and s1
    merged_asc = concat_snotel_s1(snotel, s1_asc)
    merged_desc = concat_snotel_s1(snotel, s1_desc)
    merged = concat_snotel_s1(snotel, s1)

    # create output file name
    if not outfile:
        if aoi:
            outfile = s1_asc_file.replace(".nc", f'_aoi.png')
        else:
            outfile = s1_asc_file.replace(".nc", f'_poi_{res}.png')

    # output the dataframe to csv
    merged_asc.to_csv(outfile.replace('.png','_asc.csv'))
    merged_desc.to_csv(outfile.replace('.png','_desc.csv'))
    merged.to_csv(outfile.replace('.png','_both.csv'))

    # draw plots
    outfile = outfile.replace('.png', f'_x{merged.attrs['xsize']}_y{merged.attrs['ysize']}.png')

    draw_asc_desc_lines(merged_asc, merged_desc, merged, 'Creamers', outfile)
    # draw bar plots
    # draw_multiple_bars(merged, outfile.replace('.png','_barplots.png'))



def main():

    #outfile = '/home/jiangzhu/data/crrel/SNOTEL/creamers/investigate.png'

    #s1_file = "/home/jiangzhu/data/crrel/SNOTEL/creamers/s1_creamers_20230801_20240731.nc"

    #snotel_file = "/home/jiangzhu/data/crrel/SNOTEL/creamers/depth_precipt_temp_20230801_20240731.txt"

    #lon = -147.74
    #lat = 64.87
    #attrs = {}

    parser = ArgumentParser()
    parser.add_argument('--s1asc', type=str,  required=True)
    parser.add_argument('--s1desc', type=str,  required=True)
    parser.add_argument('--s1both', type=str,  required=True)
    parser.add_argument('--snotelfile', type=str, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--aoigeojsonfile', type=str, default=None)
    parser.add_argument('--res', type=float, default=None)
    parser.add_argument('--stdate', type=str, default=None)
    parser.add_argument('--eddate', type=str, default=None)
    parser.add_argument('--outfile', type=str, default=None)

    args = parser.parse_args()

    if args.aoigeojsonfile is None and args.res is None:
        print("need to input either aoigeojsonfile or res")
        sys.exit(1)

    # get the stdate and eddata from s1asc

    stdate, eddate = get_stdate_eddate_from_file(args.s1asc)

    compare_s1_ascending_descending_both(args.s1asc, args.s1desc, args.s1both, args.snotelfile, args.lon, args.lat, args.aoigeojsonfile, args.res, stdate, eddate, args.outfile)

    print('completed ...')

if __name__ == '__main__':
    main()





