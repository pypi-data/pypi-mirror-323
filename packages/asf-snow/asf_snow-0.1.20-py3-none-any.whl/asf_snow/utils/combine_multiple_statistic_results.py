from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import geopandas as gpd
import pandas as pd
from pathlib import Path
from asf_snow.utils.analyze_sentinel1_snow import draw_combined_gdf, draw_histgram, draw_scatter_plot



filelist = [
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20201101_1130/sentinel1_20201101_1130_500_24h_close_boise_river_basin.shp',
    '//media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boiseboise_20201201_1231/sentinel1_20201201_1231_500_24h_close_boise_river_basin.shp',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210101_0131/sentinel1_20210101_0131_500_24h_close_boise_river_basin.shp',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210201_0228/sentinel1_20210201_0228_500_24h_close_boise_river_basin.shp',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210301_0331/sentinel1_20210301_0331_500_24h_close_boise_river_basin.shp',
    '/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/boise_20210401_0430/sentinel1_20210401_0430_500_24h_close_boise_river_basin.shp'
    ]


def combine_multiple_statistic_results(filelist:list, timethresh=None):

    file = filelist[0]
    out_dir = str(Path(file).parent.parent)
    lst = Path(file).stem.split("_")

    res = int(lst[3])
    timeint = int(lst[4][:-1])
    timethresh = int(lst[5][:-1])
    base = lst[6]
    method = lst[7]
    precip = lst[8]
    outfile = f'{out_dir}/sentinel1_202011_202104_{res}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_boise_river_basin.png'

    num = len(filelist)
    tot = None
    for i in range(num):

        if Path(filelist[i]).is_file():
            gdf = gpd.read_file(filelist[i])
            if tot is None:
                tot = gdf.copy(deep=True)
            else:
                tot = pd.concat([tot, gdf], ignore_index=True)

    # if tot is not None:
    #    draw_combined_gdf(tot, res=res, timeint=timeint, timethresh=timethresh, base=base, method=method,
    #                      outfile=outfile, precip=precip)

    # draw_scatter_plot(tot, res=res)

    # calculate the correlation between snow depth and observation

    return tot


def read_filelist(filelistname):
    filelst = []

    with open(filelistname) as f:
        while True:
            line = f.readline()
            if line:
                filelst.append(line.strip())
            else:
                break

    return filelst


def draw_snow_difference_histgram(filelistname):
    # read the file list
    filelist = read_filelist(filelistname)
    file = filelist[0]
    out_dir = str(Path(file).parent.parent)
    lst = Path(file).stem.split("_")
    res = int(lst[3])
    timeint = int(lst[4][:-1])
    timethresh = int(lst[5][:-1])
    base = lst[6]
    method = lst[7]
    precip = lst[8]
    outfile = f'{out_dir}/histgram_snow_depth_diff_{res}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_boise.png'

    # combine the statistic
    combined = combine_multiple_statistic_results(filelist)

    # draw histgram of snow depth difference

    draw_histgram(combined, res, timeint, timethresh, base, method, outfile, precip)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--file', type=str,  required=True)

    args = parser.parse_args()
    filelst = []

    with open(args.file) as f:
        while True:
            line = f.readline()
            if line:
                filelst.append(line.strip())
            else:
                break

    combine_multiple_statistic_results(filelst)

    print("completed ...")