import geopandas as gpd
import xarray as xr
import xvec

from geodatasets import get_path

counties = gpd.read_file(get_path("geoda.natregimes"))

pop1960 = xr.DataArray(counties.PO60, coords=[counties.geometry], dims=["county"])


pop1960 = pop1960.xvec.set_geom_indexes("county", crs=counties.crs)








print("completed ...")



