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


def compare_sentinel1_snow_depth_to_snex(ncfile, varname, snexfile, location, res, timeint, timethresh, base, method,
                                         precip):

    # sentinel1 snow depth data
    nc_var = get_var(ncfile, varname)

    # NASA snowEx summary swe data

    if '_ts_' in Path(snexfile).stem:
        gdf_snex = read_snex21_ts_summary_swe_v01(snexfile)
        # NASA snowEx summary environment data
        # snexenvfile = "/home/jiangzhu/data/crrel/snowEx21_ts_snow_pits_v1/SNEX21_TS_SP_Summary_Environment_v01.csv"

        snexenvfile = snexfile.replace("SWE", "Environment")
        if Path(snexenvfile).is_file():
            gdf_env = read_snex21_ts_summary_environment_v01(snexenvfile)
            # combine two GeoDataFrames
            gdf_snex = pd.merge(gdf_snex, gdf_env, on=['Location', 'Site', 'PitID', 'Time', 'UTMZone', 'Easting',
                                                   'Northing', 'Latitude', 'Longitude'], how='inner')

            gdf_snex = gdf_snex.rename(columns={"geometry_x": "geometry"})

            gdf_snex = gdf_snex.drop(columns=['geometry_y'])

        # get rid of rows that have precipitation of moderate or heavy
        # NONE=no snow anywhere in plot area; VERY LIGHT=occasional snowflake up to ~ 0.5 cm per hour accumulation;
        # LIGHT=~ 1 cm per hour accumulation; MODERATE=~ 2 cm per hour accumulation; HEAVY=~ 5 cm per hour accumulation
        if precip == 'n' and 'Recip Rate' in gdf_snex:
            # gdf_snex = gdf_snex[~((gdf_snex['Precip Rate'].str.lower() == 'moderate') |
            # (gdf_snex['Precip Rate'].str.lower() == 'heavy'))]
            gdf_snex = gdf_snex[gdf_snex['Precip Rate'].isnull()]

    elif '_SWE_' in Path(snexfile).stem:
        gdf_snex = read_snex23_swe(snexfile)

    elif '_comunity_' in Path(snexfile).stem:
        gdf_snex = read_SNEX23_MAR23_SD_AK_20230307_20230316_v01d0(snexfile)
    else:
        print(f'{snexfile} not exist')
        sys.exit(1)
    # go over each location
    locations = gdf_snex['Location'].unique()

    for loc in locations:
        # only check Boise River Basin
        # if loc not in 'Boise River Basin':
        #    continue
        # only check Fraser Experimental Forest
        if not (location in loc):
            continue

        gdf_snex = gdf_snex[gdf_snex['Location'].str.contains(loc)]

        gdf_snex_v = gdf_snex.sort_values(by=['time'], ignore_index=True)

        if base == 'snex':
            # call zonal_analyses_based_snex
            combined = zonal_analyses_based_snex(nc_var, gdf_snex_v, res=res, timeint=timeint, timethresh=timethresh,
                                                 method=method)
        else:
            # call zonal_analyses_based_sentinel1
            combined = zonal_analyses_based_sentinel1(nc_var, gdf_snex_v, res=res, timeint=timeint,
                                                      timethresh=timethresh, method=method)

        affix = f'_{int(res)}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_{loc.replace(" ", "_")}.shp'.lower()

        outfile = ncfile.replace(".nc", affix)

        pwildcard = str(Path(outfile).parent.joinpath(Path(outfile).stem)) + ".*"

        for file in glob.glob(pwildcard):
            # remove the file if it exists
            Path(file).unlink(missing_ok=True)

        # if not combined.empty:
        if type(combined) is not None:
            if not combined.empty:
                # save the combined GeoDataFrame
                combined.to_file(outfile)
            # break
            # draw line plot
            # pngfile = outfile.replace('.shp', '.png')
            # draw_combined_gdf(combined, res=res, timeint=timeint, timethresh=timethresh, flg=method,
            #                  outfile=pngfile, precip=precip)

    return outfile


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--ncfile', type=str,  required=True)
    parser.add_argument('--varname', type=str, default='snow_depth')
    parser.add_argument('--snexfile', type=str,  required=True)
    parser.add_argument('--location', type=str, default='Boise')
    parser.add_argument('--res', type=float, default=100)
    parser.add_argument('--timeint', type=int, default=24)
    parser.add_argument('--timethresh', type=int, default=6)
    parser.add_argument('--base', choices=['snex', 's1'], default='s1')
    parser.add_argument('--method', choices=['nearest', 'average', 'close',
                                             'nearest', 'average', 'close'])
    parser.add_argument('--precip', choices=['y', 'n'], default='y')

    args = parser.parse_args()

    compare_sentinel1_snow_depth_to_snex(args.ncfile, varname=args.varname, snexfile=args.snexfile,
                                         location=args.location, res=args.res, timeint=args.timeint,
                                         timethresh=args.timethresh, base=args.base, method=args.method,
                                         precip=args.precip)

    print('completed analysis...')
