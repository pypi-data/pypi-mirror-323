from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import geopandas as gpd
import pandas as pd
from pathlib import Path
from asf_snow.utils.analyze_sentinel1_snow import draw_combined_gdf, draw_scatter_plot

file = '/home/jiangzhu/data/crrel/sentinel1_snowEx21_ts_snow_pits_v1/fraser/fraser_202011_202105/sentinel1_202011_202105_500_12h_12h_average_y_fraser_experimental_forest.shp'
def single_statistic_results(file: str, timethresh=None):

    lst = Path(file).stem.split("_")
    res = int(lst[3])
    timeint = int(lst[4][:-1])
    timethresh = int(lst[5][:-1])
    method = lst[6]
    precip = lst[7]
    outfile = f'/home/jiangzhu/data/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/sentinel1_202011_202104_{res}_{timeint}h_{timethresh}h_{method}_{precip}_Fraser.png'

    gdf = gpd.read_file(file)


    draw_combined_gdf(gdf, res=res, timeint=timeint, timethresh=timethresh, flg=method, outfile=outfile, precip=precip)


    # draw_scatter_plot(tot, res=res)

    # calculate the correlation between snow depth and observation


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--file', type=str,  required=True)

    args = parser.parse_args()

    single_statistic_results(file)

    print("completed ...")