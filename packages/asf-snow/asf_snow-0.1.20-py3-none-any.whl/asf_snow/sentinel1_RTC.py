from pathlib import Path
from os.path import join
import shapely
import json
import glob
import logging
import os
import sys
from typing import Optional
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from asf_snow.download.sentinel1 import s1_img_search, hyp3_pipeline, download_hyp3, combine_s1_images, files2dataarray

log = logging.getLogger(__name__)

def main():
    parser = ArgumentParser()
    parser.add_argument('--username', type=str, default=None)
    parser.add_argument('--password', type=str, default=None)
    parser.add_argument('--area', nargs="*", type=float, default=[-113.2, 43, -113, 43.4])
    parser.add_argument('--daterange', nargs="*", type=str, default=['2008-08-01', '2021-04-01'])
    parser.add_argument('--workdir', type=str, default='.')
    parser.add_argument('--jobname', type=str, default='testing_job')
    parser.add_argument('--existjobname', type=str, default='testing_job')
    parser.add_argument('--outnc', default='test.nc')
    parser.add_argument('--debug', type=bool, default=False)

    args = parser.parse_args()

    # change to your minimum longitude, min lat, max long, max lat
    area = args.area

    area = shapely.geometry.box(area[0], area[1], area[2], area[3])

    workdir = args.workdir

    Path(workdir).mkdir(parents=True, exist_ok=True)

    # workdir = Path(workdir).expanduser()
    # work_dir =str(workdir)
    outdir = join(workdir, 'tmp')

    # this will be where your results are saved
    outnc = args.outnc
    out_nc = Path(outnc).expanduser()

    # this will generate a tuple of dates from the previous August 1st to this date
    # dates = get_input_dates(dates)  # run on all s1 images from (2020-08-01, 2021-04-01) in this example
    dates = args.daterange

    dates = tuple(dates)

    job_name = args.jobname

    existing_job_name = args.existjobname

    # spicy_ds = sentinel1_snow(area=args.area, dates=args.daterange, workdir=args.workdir,
    #                            jobname=args.jobname, existjobname=args.existjobname, outnc=args.outnc)

    # spicy_ds = retrieve_snow_depth(area=area1, dates=dates, work_dir=Path(workdir).expanduser(),
    #                               job_name=jobname,
    #                               existing_job_name=existjobname,
    #                               outfp=out_nc,
    #                               debug=False,
    #                               )

    # get asf_search search results
    search_results = s1_img_search(area, dates)
    log.info(f'Found {len(search_results)} results')

    num = len(search_results)

    if len(glob.glob(f'{outdir}/*.zip')) == num or len(glob.glob(f'{outdir}/S1*_VV.tif')) == num:
        if len(glob.glob(f'{outdir}/S1*_VV.tif')) == num:
            filelist = glob.glob(f'{outdir}/S1*_VV.tif')
        else:
            filelist = glob.glob(f'{outdir}/*.zip')
        imgs = files2dataarray(filelist, area=area, outdir=outdir, clean=False)
    else:

        assert len(search_results) > 3, f"Need at least 4 images to run. Found {len(search_results)} using area: {area} and dates: {dates}."

        # download s1 images into dataset ['s1'] variable name
        jobs = hyp3_pipeline(search_results, job_name=job_name, existing_job_name=existing_job_name)

        imgs = download_hyp3(jobs, area, outdir=join(workdir, 'tmp'), clean=False)


if __name__ == '__main__':
    main()