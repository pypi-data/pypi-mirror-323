from pathlib import Path
import sys
import glob
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from asf_snow.utils.analyze_sentinel1_snow import *

from asf_snow.utils.analyze_snex import *

# compare the snow depth derived with sentinel1 to NASA SnowEx experiment
# example arguments
# ncfile = "/home/jiangzhu/data/crrel/sentinel1_snowEx21_ts_snow_pits_v1/sentinel1.nc"
# snexfile = "/home/jiangzhu/data/crrel/snowEx21_ts_snow_pits_v1/302507681/SNEX21_TS_SP_Summary_SWE_v01.csv"
# snexenvfile = "/home/jiangzhu/data/crrel/snowEx21_ts_snow_pits_v1/SNEX21_TS_SP_Summary_Environment_v01.csv"
# varname = "snow_depth"
# res = 1000  # zonal analysis square size


# step 1. download SNOTEL data


# Step 2. read the 

# lon = -147.733, lat =  64.867
def compare_sentinel1_snow_depth_to_snotel(ncfile, varname, snotelfile, lon, lat, res, timeint, timethresh, base, method,
                                         precip):

    # sentinel1 snow depth data
    nc_var = get_var(ncfile, varname)

    # SNOTEL snoe depth data

    #test dry/wet snow
    # snotel = read_snotel_sd_precip_temp(snotelfile, lon, lat, {'Location':'creamers'})

    filename = str(Path(snotelfile).stem)
    location = filename.split("_")[0].capitalize()

    if filename.find("creamers") != -1 or filename.find("fieldinglake") != -1:
        snotel = read_snotel_sd_precip_ratio_temp(snotelfile, lon, lat, {'Location':location})
    else:
        snotel = read_snotel_sd_precip_temp(snotelfile, lon, lat, {'Location': location})

    if base == 'snotel':
        # call zonal_analyses_based_snex
        combined = zonal_analyses_based_snex(nc_var, snotel, res=res, timeint=timeint, timethresh=timethresh,
                                             method=method)
    else:
        # call zonal_analyses_based_sentinel1
        combined = zonal_analyses_s1_snotel_based_s1(nc_var, snotel, res=res, timeint=timeint,
                                                  timethresh=timethresh, method=method)

    loc = snotel.attrs['Location']
    affix = f'_{int(res)}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_{loc.replace(" ", "_")}.shp'.lower()

    affix_geojson = f'_{int(res)}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_{loc.replace(" ", "_")}.geojson'.lower()

    outfile = ncfile.replace(".nc", affix)

    outfile_geojson = ncfile.replace(".nc", affix_geojson)

    pwildcard = str(Path(outfile).parent.joinpath(Path(outfile).stem)) + ".*"

    for file in glob.glob(pwildcard):
        # remove the file if it exists
        Path(file).unlink(missing_ok=True)

    # if not combined.empty:
    if type(combined) is not None:
        if not combined.empty:
            # save the combined GeoDataFrame
            # combined.to_file(outfile)
            combined.to_file(outfile_geojson, driver='GeoJSON')
        # break
        # draw line plot
        # pngfile = outfile.replace('.shp', '.png')
        # draw_combined_gdf(combined, res=res, timeint=timeint, timethresh=timethresh, flg=method,
        #                  outfile=pngfile, precip=precip)

    return outfile_geojson


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--ncfile', type=str,  required=True)
    parser.add_argument('--varname', type=str, default='snow_depth')
    parser.add_argument('--snotelfile', type=str,  required=True)
    parser.add_argument('--lon', type=float )
    parser.add_argument('--lat', type=float)
    parser.add_argument('--res', type=float, default=100)
    parser.add_argument('--timeint', type=int, default=24)
    parser.add_argument('--timethresh', type=int, default=6)
    parser.add_argument('--base', choices=['snotel', 's1'], default='s1')
    parser.add_argument('--method', choices=['nearest', 'average', 'close'], default='average')
    parser.add_argument('--precip', choices=['y', 'n'], default='y')

    args = parser.parse_args()

    compare_sentinel1_snow_depth_to_snotel(args.ncfile, varname=args.varname, snotelfile=args.snotelfile, lon=args.lon,
                                           lat=args.lat, res=args.res, timeint=args.timeint,
                                           timethresh=args.timethresh, base=args.base, method=args.method,
                                         precip=args.precip)



    print('completed analysis...')
