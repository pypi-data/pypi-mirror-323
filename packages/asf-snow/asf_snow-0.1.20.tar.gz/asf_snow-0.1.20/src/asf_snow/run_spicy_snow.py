from pathlib import Path
import shapely


# Add main repo to path if you haven't added with conda-develop
# import sys
# sys.path.append('path/to/the/spicy-snow/')

from spicy_snow.retrieval import retrieve_snow_depth
from spicy_snow.IO.user_dates import get_input_dates

# change to your minimum longitude, min lat, max long, max lat
area = shapely.geometry.box(-113.2, 43, -113, 43.4)

# this will be where your results are saved
out_nc = Path('~/data/crrel/spicy-test/test.nc').expanduser()

# this will generate a tuple of dates from the previous August 1st to this date
dates = get_input_dates('2021-04-01') # run on all s1 images from (2020-08-01, 2021-04-01) in this example

spicy_ds = retrieve_snow_depth(area = area, dates = dates, 
                               work_dir = Path('~/data/crrel/spicy-test/').expanduser(), 
                               job_name = f'testing_spicy',
                               existing_job_name = 'testing_spicy',
                               debug=False,
                               outfp=out_nc)
