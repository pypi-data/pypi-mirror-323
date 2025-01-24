from asf_snow.utils.combine_multiple_statistic_results import *

from asf_snow.utils.analyze_sentinel1_snow import *

# file = "/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/sentinel1_202011_202104_500_36h_6h_snex_close_y_boise_river_basin.geojson"

# file = "/media/jiangzhu/Elements/crrel/sentinel1_snowEx21_ts_snow_pits_v1/boise/sentinel1_202011_202104_500_12h_12h_snex_average_y_boise_river_basin.geojson"


def extract_arguments(file):
    out_dir = str(Path(file).parent.parent)
    lst = Path(file).stem.split("_")
    if 'fairbanks' in file or 'northslope' in file:
        lst = lst[1:]

    res = int(lst[3])
    timeint = int(lst[4][:-1])
    timethresh = int(lst[5][:-1])
    base = lst[6]
    method = lst[7]
    precip = lst[8]
    loc = lst[9]

    return out_dir, res, timeint, timethresh, base, method, precip, loc


def get_gdf_with_unique_pixels(gdf):
    gdf_o = gdf.copy(deep=True)
    gdf = gdf.drop_duplicates('s1geometry')
    gdf = gdf.reset_index(drop=True)

    # Average the snow depths of the duplicated records in gdf_o
    s1geometry = gdf['s1geometry']
    for index, item in s1geometry.items():
        snex_sd_mean = gdf_o[gdf_o['s1geometry'] == item]['snex_sd'].mean()
        gdf.loc[gdf['s1geometry'] == item, ['snex_sd']] = snex_sd_mean
    return gdf


def draw_diff_error_count(file):

    gdf = gpd.read_file(file)

    if 'fairbanks' in Path(file).stem:
        gdf = get_gdf_with_unique_pixels(gdf)

    out_dir, res, timeint, timethresh, base, method, precip, loc = extract_arguments(file)

    # plot_type = 'combined'

    # outfile = f'{out_dir}/{plot_type}_{res}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_{loc}.png'

    # draw_combined_gdf(gdf, res, timeint, timethresh, base, method, outfile, precip)

    plot_type = 'diff_error_count'

    outfile = f'{out_dir}/{plot_type}_{res}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_{loc}.png'

    # snex_ts,
    # draw_diff_error_count_plot(gdf, res, timeint, timethresh, base, method, outfile, precip)

    # snex23, alaska
    draw_diff_error_count_plot_index(gdf, res, timeint, timethresh, base, method, outfile, precip)

    plot_type = 'histogram'

    outfile = f'{out_dir}/{plot_type}_{res}_{timeint}h_{timethresh}h_{base}_{method}_{precip}_{loc}.png'

    draw_histgram(gdf, res, timeint, timethresh, base, method, outfile, precip)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--file', type=str,  required=True)

    args = parser.parse_args()

    draw_diff_error_count(args.file)

    print("completed ...")



