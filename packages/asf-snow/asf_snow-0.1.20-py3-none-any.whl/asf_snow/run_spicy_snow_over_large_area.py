from shapely import geometry
from itertools import product
for lon_min, lat_min in product(range(-117, -113), range(43, 46)):
    area = shapely.geometry.box(lon_min, lat_min, lon_min + 1, lat_min + 1)
    out_nc = Path(f'~/Desktop/spicy-test/swath_{lon_min}-{lon_min + 1}_{lat_min}-{lat_min + 1}.nc').expanduser()
    if out_nc.exists():
        continue

    spicy_ds = retrieve_snow_depth(area = area, dates = dates, 
                                work_dir = Path('~/scratch/spicy-lowman-quadrant/data/').expanduser(), 
                                job_name = f'spicy-lowman-{lon_min}-{lon_min + 1}_{lat_min}-{lat_min + 1}', # v1
                                existing_job_name = f'spicy-lowman-{lon_min}-{lon_min + 1}_{lat_min}-{lat_min + 1}', # v1
                                debug=False,
                                outfp=out_nc)

