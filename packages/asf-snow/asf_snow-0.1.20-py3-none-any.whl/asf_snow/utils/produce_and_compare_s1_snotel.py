
import xarray as xr

from asf_snow.utils.snotel import download_snotel

from asf_snow.sentinel1_snow import *

from asf_snow.utils.analyze_sentinel1_snow import bbox_via_point

from asf_snow.utils.s1_snotel_corr_ts import *

# from asf_snow.utils.compare_sentinel1_snow_depth_to_snotel import *

# from asf_snow.utils.draw_s1_snotel_plot import *





# 1, download SNOTEL manually

# 2, produce S1 data
# python sentinel1_snow.py --username cirrusasf --password xxxxxxxxx --area -147.75 64.85 -147.72 64.88 --daterange 2022-08-01 2023-07-31 --workdir /home/jiangzhu/data/crrel/SNOTEL/creamersfield/s1 --jobname jz_creamers_20220801_20230731_2 --existjobname jz_creamers_20220801_20230731_2 --outnc /home/jiangzhu/data/crrel/SNOTEL/creamersfield/s1/sentinel1_creamers_20220801_20230731_2.nc

# 3. product analysis results

# 4. draw plots

def main():

    def _t_or_f(arg):
        ua = str(arg).upper()
        if 'TRUE'.startswith(ua):
            return True
        elif 'FALSE'.startswith(ua):
            return False
        else:
            pass  #error condition maybe?

    parser = ArgumentParser()

    parser.add_argument('--workdir', type=str, default='./')

    # for SNOTEL is downloaded manually
    # parser.add_argument('--snotelfile',type=str, required=True)
    # parser.add_argument('--lon', type=float,required=True)
    # parser.add_argument('--lat', type=float,required=True)


    # SNOTEL is downloaded dynamically with snotel site
    parser.add_argument('--snotelsite', type=str, help='1302:AK:SNTL', required=True)
    parser.add_argument('--snotelres', type=float, default=10000.0)
    parser.add_argument('--daterange', nargs="*", type=str, default=['2008-08-01', '2021-04-01'])

    # for S1 data download
    parser.add_argument('--username', type=str, default=None)
    parser.add_argument('--password', type=str, default=None)
    parser.add_argument('--flightdir', type=str, choices =['ascending','descending', 'both'], default='both')
    parser.add_argument('--jobname', type=str, default='jz_s1')
    parser.add_argument('--existjobname', type=str, default='testing_job')
    parser.add_argument('--parameterabc', nargs="*", type=float, default=[2.5, 0.2, 0.55])
    parser.add_argument('--wet_snow_thresh', type=float, default=-3.0)
    # parser.add_argument('--outnc', type=str, default='s1_data')
    # for compare the S1 and SNOTEL
    parser.add_argument('--avg', type=_t_or_f)
    parser.add_argument('--res', type=float, default=1000.0)
    # parser.add_argument('--lon', type=float, default=None)
    # parser.add_argument('--lat', type=float, default=None)

    parser.add_argument('--debug', type=bool, default=False)

    args = parser.parse_args()

    # 1. download snotel
    # For Creamers' Field, snotelsite='1302:AK:SNTL'

    site_and_range = f'{args.snotelsite.replace(":","_")}_{args.daterange[0].replace("-","")}_{args.daterange[1].replace("-","")}.geojson'

    snotelfile = Path.joinpath(Path(args.workdir), site_and_range)

    snotelfile, snotel = download_snotel(snotelsite=args.snotelsite, stdate=args.daterange[0], eddate=args.daterange[1], snotelfile=snotelfile)

    sitelon = float(snotel.iloc[0]['geometry'].x)
    sitelat = float(snotel.iloc[0]['geometry'].y)

    bbox = bbox_via_point(sitelon, sitelat, args.snotelres)

    # produce S1 data
    # write args if args.workdir not exist

    site_and_range = f'{args.flightdir}/sentinel1_{args.snotelsite.replace(":","_")}_{int(args.snotelres)}_{args.daterange[0].replace("-","")}_{args.daterange[1].replace("-","")}_{args.flightdir}.nc'

    nc_file = Path(args.workdir).joinpath(site_and_range)

    nc_file.parent.mkdir(parents=True, exist_ok=True)

    nc_file = str(nc_file)

    if not Path(nc_file).exists():
        environment_jsonfile = f'{args.workdir}/tmp/environment.json'
        if not os.path.exists(environment_jsonfile):
            environment = vars(args)
            environment['step'] = 'begin'
            environment['area'] = bbox
            os.environ['ENVIRONMENT'] = json.dumps(environment)

        else:
            environment = utils.read_environment(environment_jsonfile)
            os.environ['ENVIRONMENT'] = json.dumps(environment)

        # set environment for share
        if  args.username is not None and args.password is not None:
            os.environ['EARTHDATA_USERNAME'] = args.username
            os.environ['EARTHDATA_PASSWORD'] = args.password

        nc_ds = sentinel1_snow(area=bbox, dates=args.daterange, flightdir=args.flightdir, workdir=args.workdir,
                   jobname=args.jobname, existjobname=args.existjobname, outnc=nc_file,
                   parameterabc=args.parameterabc, wet_snow_thresh=args.wet_snow_thresh)
    else:
        # to_netcdf and read it back, the coords variables change, and crs is missing, need to restore them back
        nc_ds = xr.open_dataset(nc_file)
        nc_ds = nc_ds.set_coords(("spatial_ref","projection"))

    # set CRS for nc_ds
    try:
        crs = nc_ds.rio.crs
    except:
        try:
            nc_ds = nc_ds.set_coords(("spatial_ref","projection"))
            nc_ds.rio.write_crs('epsg:4326', inplace=True)
        except:
            pass

    # adjust nc_ds
    nc_ds.attrs['sitelon'] = sitelon
    nc_ds.attrs['sitelat'] = sitelat
    nc_ds.attrs['orbit'] = 'all'

    # write the bounds of nc_ds into geojson file
    s1_poly = bbox2polygon(list(nc_ds.snow_depth.rio.bounds()))
    geojson_file = nc_file.replace(".nc", ".geojson")
    write_polygon(s1_poly, geojson_file)


    # 3. analyze the s1 and snotel data for pixels for Creamers's Field
    '''
    Pixel 2, -147.7681, 64.8541, fcf=0.06
    Pixel 3, -147.7175, 64.8383, fcf=0
    Pixel 4, -147.6891, 64.8547, fcf = 0
    Pixel 5, -147.7126, 64.8838, fcf = 0.14
    Pixel 6, -147.7979, 64.8754, fcf=1.0
    Pixel 7, -147.6471, 64.8505, fcf=1.0
    Pixel 8, -147.7529, 64.8868, fcf=0.96
    '''
    pixels ={"pixel2":[-147.7681, 64.8541],
             "pixel3":[-147.7175, 64.8383],
             "pixel4":[-147.6891, 64.8547],
             "pixel5":[-147.7126, 64.8838],
             "pixel6":[-147.7979, 64.8754],
             "pixel7":[-147.6471, 64.8505],
             "pixel8":[-147.7529, 64.8868]
             }


    for key, value in pixels.items():

        geojson_file_pixel = geojson_file.replace(".geojson", f'_{key}.geojson')

        # if average, clip the nc_ds with lon, lat, and res
        if args.avg and args.res:
            poly = polygon_via_point(lon=value[0], lat=value[1], resolution=args.res)
            jsstr = to_geojson(poly)
            geometries = [json.loads(jsstr)]
            nc_ds_pixel = nc_ds.rio.clip(geometries, all_touched=True)
            # write boundary as polygon
            s1_poly_clipped = bbox2polygon(list(nc_ds_pixel.snow_depth.rio.bounds()))
            write_polygon(s1_poly_clipped, geojson_file_pixel)
        else:
            nc_ds_pixel = nc_ds.copy(deep=True)

        nc_ds_pixel.attrs['lon'] = value[0]

        nc_ds_pixel.attrs['lat'] = value[1]

        nc_ds_pixel.attrs['poi'] = key

        # get x and y
        gt = get_gt(nc_ds_pixel)
        x, y = lonlat_to_colrow(gt, value[0], value[1])

        # draw combination of all orbits
        snowcover = calc_s1_snotel_correlation(nc_ds_pixel, snotel, st_mmdd='11-01', ed_mmdd='04-01')

        outfile = geojson_file_pixel.replace(".geojson", ".nc")
        write_to_netcdf(snowcover, outfile)

        pngfile = geojson_file_pixel.replace(".geojson", ".png")
        draw_lines(nc_ds_pixel, snotel, outfile=pngfile, y=y, x=x, average=args.avg, res=args.res)


if __name__ == '__main__':

    main()



