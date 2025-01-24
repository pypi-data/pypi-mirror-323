from asf_snow.utils.analyze_sentinel1_snow import *

def s1_snotel_diff_error_count_plots(file):

    lst = Path(file).stem.split("_")
    loc=lst[1].capitalize()
    res = int(lst[4])
    timeint = int(lst[5][:-1])
    timethresh = int(lst[6][:-1])
    base = lst[7]
    method = lst[8]
    precip = lst[9]

    outfile = file.replace(".geojson", ".png")
    gdf = gpd.read_file(file)
    # draw diff, error, and count plots
    draw_s1_snotel_diff_error_count_plot(gdf, res, timeint, timethresh, base, method, outfile, precip, loc)

    return

if __name__ == '__main__':

    # file = "/home/jiangzhu/data/crrel/SNOTEL/creamersfield/s1_2/sentinel1_creamers_20220801_20230731n_400_12h_12h_s1_average_y_creamers_field.shp"

    parser = ArgumentParser()
    parser.add_argument('--file',type=str, required=True)
    args = parser.parse_args()
    s1_snotel_diff_error_count_plots(args.file)