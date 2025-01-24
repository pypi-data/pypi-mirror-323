import json

import hyp3_sdk


def download_files_in_jobs(jobname, filelist=None, out_dir='.'):

    hyp3 = hyp3_sdk.HyP3('https://hyp3-api.asf.alaska.edu', prompt=True)

    jobs = hyp3.find_jobs(name=jobname)

    if len(jobs) == 0:
        return

    if filelist:
        with open(filelist) as file:
            lines = [line.rstrip() for line in file]

        # if job has been downloaded, skip it

        for job in jobs:

            if job.files[0]['filename'] in lines:
                continue
            else:
                job.download_files(location=out_dir, create=True)
    else:
        jobs.download_files(location=out_dir, create=True)

    return


if __name__ == '__main__':

    jobname = 'jz_snow_1'

    filelist = "/media/jiangzhu/data1/crrel/sentinel1_20201116_20210327/flist"

    out_dir = "/media/jiangzhu/data1/crrel/sentinel1_20201116_20210327"

    download_files_in_jobs(jobname, filelist=filelist, out_dir=out_dir)

    print('completed ...')
