"""
Functions to download PROBA-V forest-cover-fraction images for specific geometries
"""

import sys
from pathlib import Path
import os
from os.path import basename, exists, expanduser, join
import shutil
import shapely
import rioxarray as rxa
import xarray as xr
import numpy as np
import logging
log = logging.getLogger(__name__)

sys.path.append(expanduser('~/Documents/spicy-snow'))
from spicy_snow.utils.download import url_download


def download_fcf(dataset: xr.Dataset, out_fp: str, environment: dict = None) -> xr.Dataset:
    """
    Download PROBA-V forest-cover-fraction images.

    Args:
    dataset: large dataset to add IMS data to
    out_fp: filepath to save tiff of results

    Returns:
    dataset: large dataset with 'fcf' added as data variable
    """
    log.debug("Downloading Forest Cover")
    # this is the url from Lievens et al. 2021 paper
    fcf_url = 'https://zenodo.org/record/3939050/files/PROBAV_LC100_global_v3.0.1_2019-nrt_Tree-CoverFraction-layer_EPSG-4326.tif'
    # download just forest cover fraction to out file
    if not Path(out_fp).is_file():
        url_download(fcf_url, out_fp)
    # open as dataArray and return
    fcf = rxa.open_rasterio(out_fp)

    # reproject FCF and clip to match dataset
    log.debug(f"Clipping FCF to {dataset['s1'].rio.bounds()}")

    # clip first to avoid super long reproject processes
    fcf = fcf.rio.clip_box(*dataset['s1'].rio.bounds())

    # reproject FCF to match dataset
    fcf = fcf.rio.reproject_match(dataset['s1'])

    # remove band dimension as it only has one band
    fcf = fcf.squeeze('band')

    # convert unit8 to int8
    fcf.values = fcf.values.astype(float)

    # if the upper of valid range of data is greater than 1 set to 0-1
    valid_range = [float(i) for i in fcf.valid_range.split(",")]
    if valid_range[1] > 1:
        log.debug("fcf range is 0 to 100, so dividing by 100")
        fcf.values = fcf.values/100.0
        log.debug(f"New fcf max is {fcf.max()} and min is {fcf.min()}")

    assert fcf.max() <= 1, "Forest cover fraction must be bounded 0-1"
    assert fcf.min() >= 0, "Forest cover fraction must be bounded 0-1"

    log.debug(f'FCF min: {fcf.min()}')
    log.debug(f'FCF max: {fcf.max()}')
    log.debug(f'FCF mean: {fcf.mean()}')

    # merge FCF and name it 'fcf' as a data variable
    dataset = xr.merge([dataset, fcf.rename('fcf')])

    dataset.to_netcdf(f'{environment['workdir']}/tmp/sentinel1_snow_fcf.nc')

    return dataset

# End of file