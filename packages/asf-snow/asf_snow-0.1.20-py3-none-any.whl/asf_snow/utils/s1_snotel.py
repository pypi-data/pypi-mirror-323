from asf_snow.sentinel1_snow import *

from asf_snow.utils.analyze_sentinel1_snow import bbox_via_point

from asf_snow.utils.compare_sentinel1_snow_depth_to_snotel import *

from asf_snow.utils.draw_s1_snotel_plot import *



# 1, download SNOTEL manually

# 2, produce S1 data
# python sentinel1_snow.py --username cirrusasf --password xxxxxxxxx --area -147.75 64.85 -147.72 64.88 --daterange 2022-08-01 2023-07-31 --workdir /home/jiangzhu/data/crrel/SNOTEL/creamersfield/s1 --jobname jz_creamers_20220801_20230731_2 --existjobname jz_creamers_20220801_20230731_2 --outnc /home/jiangzhu/data/crrel/SNOTEL/creamersfield/s1/sentinel1_creamers_20220801_20230731_2.nc

# 3. product analysis results

# 4. draw plots




def main():
    parser = ArgumentParser()
    parser.add_argument('--snotelfile',type=str, required=True)
    parser.add_argument('--lon', type=float,required=True)
    parser.add_argument('--lat', type=float,required=True)
    parser.add_argument('--snotelarea', type=float,required=True)
    parser.add_argument('--username', type=str, default=None)
    parser.add_argument('--password', type=str, default=None)
    parser.add_argument('--daterange', nargs="*", type=str, default=['2008-08-01', '2021-04-01'])
    parser.add_argument('--workdir', type=str, default='./')
    parser.add_argument('--outnc', type=str, default='s1_data')
    parser.add_argument('--jobname', type=str, default='jz_s1')
    parser.add_argument('--existjobname', type=str, default='testing_job')
    parser.add_argument('--parameterabc', nargs="*", type=float, default=[2.5, 0.2, 0.55])
    parser.add_argument('--debug', type=bool, default=False)

    args = parser.parse_args()

    # download snotelfile mannually
    # Nenana
    # snotelfile = "/home/jiangzhu/data/crrel/SNOTEL/nenana/nenana_2081_20230801_20240731.csv"
    # lon=-148.91, lat=64.69, elevation=415 ft


    # lot,lat to bbox

    bbox = bbox_via_point(args.lon, args.lat, args.snotelarea)

    # produce S1 data
    # write args if args.workdir not exist

    environment_jsonfile = f'{args.workdir}/tmp/environment.json'

    # if not Path(environment_jsonfile).is_file():
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

    spicy_ds = sentinel1_snow(bbox, dates=args.daterange, workdir=args.workdir, jobname=args.jobname,
                              existjobname=args.jobname, outnc=args.outnc, parameterabc=args.parameterabc)

    # 3. analyze the s1 and snotel data

    resolutions = [50.0, 100.0, 200.0, 300.0, 400.0, 500.0]

    resolutions = [500.0]

    for res in resolutions:

        outfile = compare_sentinel1_snow_depth_to_snotel(args.outnc, 'snow_depth', args.snotelfile, args.lon, args.lat, res=res, timeint=24, timethresh=24, base='s1', method='average',
                                precip='n')
        # 4. draw plots
        draw_s1_snotel_plot(outfile)


if __name__ == '__main__':

    main()



