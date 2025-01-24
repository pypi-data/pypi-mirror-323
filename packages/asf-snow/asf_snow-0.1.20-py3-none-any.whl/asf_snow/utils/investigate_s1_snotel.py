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

def draw_multiple_lines(merged, loc, wet_st, wet_ed, outfile):
    # merged = pd.merge_asof(s1_df, snotel, on="time", direction="nearest")
    merged = merged[~merged['snow_depth_y'].isnull()]

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
    #    fig, ax = plt.subplots(nrows=6, ncols=1)
    #else:
    fig, ax = plt.subplots(nrows=5, ncols=1)

    # fig.suptitle('This is a somewhat long figure title', fontsize=16)

    if merged.attrs['res']:
        title = f'SNOTEL and {merged.attrs['flightdir']} {merged.attrs['mode']} S1 Snow Depth Averaged over {merged.attrs['res']} m Resolution of the {merged.attrs['location'].capitalize()} during the {st_date} to {ed_date} Period'
    else:
        title = f'SNOTEL and {merged.attrs['flightdir']} {merged.attrs['mode']} S1 Snow Depth Averaged over the AOI of the {merged.attrs['location'].capitalize()}) during the {st_date} to {ed_date} Period'

    fig.suptitle(title, fontsize=24)

    # draw s1 and SNOTEL snow depth on the same panel
    fcf_ratio = float("{:.2f}".format(merged.attrs['fcf_ratio']))
    ax[0].plot(merged['date'], merged['snow_depth_x'], label=f'SNOTEL Snow Depth, R = {corr}, FC ratio {fcf_ratio}, S1-SNOTEL: min {min}, mean {mean}, max {max}, std {std}', color='red')
    ax[0].plot(merged['date'], merged['snow_depth_y'], label=f'Averaged Snow Depths of S1, xsize={merged.attrs['xsize']}, ysize={merged.attrs['ysize']}', color='blue')
    ax[0].legend()

    # temperature and 32F line
    line32 = np.zeros_like(merged['date'], dtype=float)
    line32[:] = 32.0
    ax[1].plot(merged['date'], merged['temp_avg'], label='Temperature', color='red')
    ax[1].plot(merged['date'], line32, label='32 F', color='blue')
    ax[1].legend()

    # wet snow percentage
    ax[2].plot(merged['date'], merged['wet_snow_percent'], label='Wet snow Percentage', color='red')
    ax[2].set_xlim(ax[1].get_xlim())
    ax[2].set_ylim([0, 100])
    ax[2].legend()

    # cross-polarization ratio
    ax[3].plot(merged['date'], merged['vh_mean'], label='VH, db', color='blue')
    ax[3].plot(merged['date'], merged['vv_mean'], label='VV, db', color='red')
    ax[3].plot(merged['date'], merged['cr_mean'], label='Cross-Polarization Ratio, db', color='black')
    ax[3].legend()

    # precipitation
    ax[4].plot(merged['date'], merged['precip_inc'], label='precip increment, m', color='red')
    ax[4].legend()

    # snow-rain-ratio
    # if 'snow_rain_ratio' in merged.columns:
    #    ax[5].plot(merged['date'], merged['snow_rain_ratio'], label='snow-rain-ratio',color='blue')
    #    ax[5].legend()

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
        title = f'SNOTEL and {merged.attrs['flightdir']} {merged.attrs['mode']} S1 Snow Depth Averaged over {merged.attrs['res']} m Resolution of the {merged.attrs['location'].capitalize()} during the {st_date} to {ed_date} Period'
    else:
        title = f'SNOTEL and {merged.attrs['flightdir']} {merged.attrs['mode']} S1 Snow Depth Averaged over the AOI of the {merged.attrs['location'].capitalize()} during the {st_date} to {ed_date} Period'

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


def calc_cr(nc_ds, mode:str='all'):
    mk1 = np.isnan(nc_ds.snow_depth)
    mk2 = nc_ds.wet_snow_flag.astype(np.bool)

    # calculate the percentage of wet snow for each time
    mk1sum = mk1.astype(np.byte).sum(axis=(1, 2))
    mk2sum = mk2.astype(np.byte).sum(axis=(1, 2))
    tot_valid_pixel = len(mk1.x) * len(mk1.y) - mk1sum
    wet_snow_percent = 100 * mk2sum / tot_valid_pixel

    if mode == 'dry':
        mk2 = nc_ds.wet_snow_flag.astype(np.bool)
        mk = np.logical_or(mk1, mk2)
    elif mode == 'wet':
        mk2 = ~nc_ds.wet_snow_flag.astype(np.bool)
        mk = np.logical_or(mk1, mk2)
    else:
        mk = mk1

    # construct the np.masked array
    sd = np.ma.MaskedArray(nc_ds.snow_depth, mk)
    vh = np.ma.MaskedArray(nc_ds.s1.sel(band='VH'), mk)
    vv = np.ma.MaskedArray(nc_ds.s1.sel(band='VV'), mk)

    # calculate the cr, cr_mean
    sd_mean = nc_ds.snow_depth.mean(axis=(1,2))
    sd_mean.data = sd.mean(axis=(1, 2)).data

    vh_mean = nc_ds.s1.sel(band='VH').mean(axis=(1,2))
    vh = 10 ** vh
    vh_mean.data = vh.mean(axis=(1, 2)).data
    vh_mean = vh_mean.reset_coords(['band'], drop=True)

    vv_mean = nc_ds.s1.sel(band='VV').mean(axis=(1, 2))
    vv = 10 ** vv
    vv_mean.data = vv.mean(axis=(1, 2)).data
    vv_mean = vv_mean.reset_coords(['band'], drop=True)

    cr = nc_ds.s1.sel(band='VH') / nc_ds.s1.sel(band='VV')
    cr_mean = cr.mean(axis=(1, 2))
    cr_var = vh / vv
    cr_mean.data = cr_var.mean(axis=(1, 2)).data

    # convert vv_mean, vh_mean, and cr_mean in db
    vh_mean = np.log10(vh_mean)
    vv_mean = np.log10(vv_mean)
    cr_mean = np.log10(cr_mean)

    return sd_mean, vh_mean, vv_mean, cr_mean, wet_snow_percent


def investigate_s1_snotel(s1_file, snotelfile, snotelsite, lon, lat, aoi: None, res: None, stdate: None, eddate: None,
                          wet_st: None, wet_ed: None, mode: str='all', outfile: str=None):
    # read the nc_ds
    # stdate and eddate are yyyy-mm-dd, typical stdate='2021-11-15', eddate='2022-03-15'

    nc_ds = xr.open_dataset(s1_file, decode_coords="all")

    nc_ds = nc_ds.transpose('time','band','y','x',...)

    nc_ds = nc_ds.sortby('time')

    if (nc_ds.flight_dir.values == 'ascending').all():
        flightdir = 'ascending'
    elif (nc_ds.flight_dir.values == 'descending').all():
        flightdir = 'descending'
    else:
        flightdir = 'both'

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
        poly=None

    if poly:
        jsstr = to_geojson(poly)
        geometries = [json.loads(jsstr)]
        nc_ds = nc_ds.rio.clip(geometries, all_touched=True)

    xsz = len(nc_ds.snow_depth.x)
    ysz = len(nc_ds.snow_depth.y)
    tot_num = nc_ds.fcf.data.size
    forest_num = nc_ds.fcf.data[nc_ds.fcf.data>=0.5].size
    fcf_ratio = forest_num/float(tot_num)

    # test purpose

    s1_clipped = bbox2polygon(list(nc_ds.snow_depth.rio.bounds()))
    write_polygon(s1_clipped, s1_file.replace(".nc", "_s1_clipped.geojson"))

    # calculate cr
    sd_mean, vh_mean, vv_mean, cr_mean, wet_snow_percent = calc_cr(nc_ds, mode=mode)

    # set nan for wet_snow_percentage outside of wet_st and wet_ed


    # add cr_mean to s1_sd_mean
    s1_merged = xr.merge([sd_mean, vh_mean.rename('vh_mean'), vv_mean.rename('vv_mean'),
                          cr_mean.rename('cr_mean'), wet_snow_percent.rename('wet_snow_percent')])

    # if stdate and eddate, only keep data from stdate to eddata, normally form 11/15 to 3/15
    st_year = int(s1_merged.time[0].dt.year)
    ed_year = int(s1_merged.time[-1].dt.year)

    if stdate and eddate:
        stdate64 = np.datetime64(datetime.strptime(f'{stdate} 00:00:00', '%Y-%m-%d %H:%M:%S'))
        eddate64 = np.datetime64(datetime.strptime(f'{eddate} 00:00:00', '%Y-%m-%d %H:%M:%S'))
        s1_merged = s1_merged.sel(time=slice(stdate64, eddate64))

    # if wet_st and wet_ed are set, then only keep wet_snow_flag within the time range between wet_st and wet_ed
    if wet_st and wet_ed:
        wet_st64 = np.datetime64(datetime.strptime(f'{st_year}-{wet_st} 00:00:00', '%Y-%m-%d %H:%M:%S'))
        wet_ed64 = np.datetime64(datetime.strptime(f'{ed_year}-{wet_ed} 00:00:00', '%Y-%m-%d %H:%M:%S'))
        s1_merged.wet_snow_percent.sel(time=slice(s1_merged.time[0], wet_st64)).loc[:] = None
        s1_merged.wet_snow_percent.sel(time=slice(wet_ed64, s1_merged.time[-1])).loc[:] = None

    #convert xarray.dataset to pandas dataframe
    s1_df = s1_merged.to_dataframe()

    s1_df['Time'] = s1_df.index
    # get location
    str_list = Path(s1_file).stem.split("_")
    loc = str_list[1]
    st = str_list[2]
    ed = str_list[3]

    # Creamers' field
    # Latitude:	64.87
    # Longitude:	-147.74
    if snotelfile:
        filename = str(Path(snotelfile).stem)
        if filename.find("creamers") != -1 or  filename.find("fieldinglake") != -1:
            snotel = read_snotel_sd_precip_ratio_temp(snotelfile, lon, lat, {})

        else:
            snotel = read_snotel_sd_precip_temp(snotelfile, lon, lat, {})
            # convert date string to datetime64
            snotel['Time'] = pd.to_datetime(snotel['Time'])
            # only consider stdate to eddate period
            if stdate and eddate:
                mask = (snotel['Time']>=stdate) & (snotel['Time']<=eddate)
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
    s1_df['date'] = s1_df.index.date

    merged = pd.merge(snotel, s1_df, on='date', how='outer')

    # snotel with x, s1_df with y
    # remove NaT in Time_x
    # merged  = merged[~merged.Time_x.isnull()]

    # add attrs to merged

    merged.attrs['location'] = loc
    merged.attrs['lon'] = lon
    merged.attrs['lat'] = lat
    merged.attrs['st_date'] = stdate
    merged.attrs['ed_date'] = eddate
    merged.attrs['res'] = res
    merged.attrs['xsize'] = xsz
    merged.attrs['ysize'] = ysz
    merged.attrs['fcf_ratio'] = fcf_ratio
    merged.attrs['flightdir'] = flightdir
    merged.attrs['mode'] = mode
    if not outfile:
        if aoi:
            outfile = s1_file.replace(".nc", f'_aoi.png')
        else:
            outfile = s1_file.replace(".nc", f'_poi_{res}.png')

    # output the dataframe to csv
    merged.to_csv(outfile.replace('.png','.csv'))

    # calculate corr
    merged1 = merged[~merged['snow_depth_y'].isnull()]
    corr = merged1['snow_depth_y'].corr(merged1['snow_depth_x'])

    corr = float("{:.2f}".format(corr))

    # draw plots
    outfile = outfile.replace('.png', f'_x{xsz}_y{ysz}.png')

    draw_multiple_lines(merged, 'Creamers', wet_st, wet_ed, outfile)
    # draw bar plots
    # draw_multiple_bars(merged, outfile.replace('.png','_barplots.png'))


def main():

    #outfile = '/home/jiangzhu/data/crrel/SNOTEL/creamers/investigate.png'

    #s1file = "/home/jiangzhu/data/crrel/SNOTEL/creamers/s1_creamers_20230801_20240731.nc"

    #snotelfile = "/home/jiangzhu/data/crrel/SNOTEL/creamers/depth_precipt_temp_20230801_20240731.txt"

    #snotelsite="1302:AK:SNTL"

    #lon = -147.74
    #lat = 64.87
    #attrs = {}

    parser = ArgumentParser()
    parser.add_argument('--s1file', type=str,  required=True)
    parser.add_argument('--snotelfile', type=str,  default=None)
    parser.add_argument('--snotelsite', type=str, help='1302:AK:SNTL', default=None)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--lat', type=float, required=True)

    parser.add_argument('--stdate', type=str, required=True, help='2023-08-01')
    parser.add_argument('--wet_stdate', type=str, help='11-15')
    parser.add_argument('--eddate', type=str, required=True, help='2024-07-31')
    parser.add_argument('--wet_eddate', type=str, help='04-15')

    parser.add_argument('--aoigeojsonfile', type=str, default=None)
    parser.add_argument('--res', type=float, default=None)
    parser.add_argument('--mode', help='dry, wet, or all', type=str, default='all', choices=['dry', 'wet', 'all'])
    parser.add_argument('--outfile', type=str, default=None)

    args = parser.parse_args()

    if args.aoigeojsonfile is None and args.res is None:
        print("need to input either aoigeojsonfile or res")
        sys.exit(1)
    investigate_s1_snotel(args.s1file, args.snotelfile, args.snotelsite, args.lon, args.lat, aoi=args.aoigeojsonfile,
                          res=args.res, stdate=args.stdate, wet_st=args.wet_stdate, eddate=args.eddate,
                          wet_ed=args.wet_eddate, mode=args.mode, outfile=args.outfile)

    print('completed ...')

if __name__ == '__main__':
    main()





