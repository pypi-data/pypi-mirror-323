from folium import GeoJson
import numpy as np
from datetime import datetime
import pandas as pd
from geopandas import GeoSeries
from shapely import geometry, to_geojson
from shapely.geometry import Polygon
from zipfile import ZipFile
import json
from pathlib import Path
from zipfile import ZipFile
import geopandas as gpd
import xarray as xr
import rioxarray as rio


def bbox2polygon(bbox):
    # bbox = [ -116.12351, 37.9071, -105.86093, 47.0607]
    return geometry.box(*bbox)


def extractfromzipfile(zipfile: Path, file: Path):
    # loading the temp.zip and creating a zip object
    with ZipFile(zipfile, 'r') as zObject:
        # Extracting specific file in the zip
        # into a specific location.
        extfile = f'{zipfile.stem}/{file.name}'
        zipinfo = zObject.getinfo(extfile)
        zipinfo.filename = Path(extfile).name
        zObject.extract(zipinfo, path=file.parent)
    if file.is_file():
        return file
    else:
        return None


def write_environment(dic: dict, jsonfile):
    with open(jsonfile, 'w') as convert_file:
     convert_file.write(json.dumps(dic))


def read_environment(jsonfile: str):
    with open(jsonfile) as json_file:
        dic = json.load(json_file)
    return dic


def write_polygon(poly: geometry.Polygon, file: str):
    poly_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[poly])
    poly_gdf.to_file(file, driver="GeoJSON")

def read_polygon(geojsonfile):
    # geojson file only include one raw, its geometry is a Polygon

    gdf = gpd.read_file(geojsonfile)

    return gdf.loc[0, 'geometry']

# write_polygon2 does not work well
def write_polygon2(poly:geometry.Polygon,file: str):
    poly_dic = to_geojson(poly)
    geojson_data = json.loads(poly_dic)
    f = open(file, 'w')
    json.dump(geojson_data, f)
    f.close()

def poly_coords_2_polygon(coords):

    # coord =[(-147.739642245038, 64.864684437575), (-147.739207102818, 64.8648316353217), (-147.738892557103, 64.8656067041273), (-147.739110131994, 64.8658115743219), (-147.742841408334, 64.8664873680826), (-147.745829871823, 64.8669489866227), (-147.749026104411, 64.8670220774216), (-147.750556203041, 64.8669562783539), (-147.75041963082, 64.8657147933085), (-147.74839248122, 64.8652114488119), (-147.746463756512, 64.864688434635), (-147.744731279647, 64.8644809492782), (-147.74305235255, 64.8644505200646), (-147.739642245038, 64.864684437575)]

    polygon = Polygon(coords)

    return polygon


def geometry2geojsonfile(geometry: geometry, geojsonfile: str):
    with open(geojsonfile, 'w') as f:
        js_str = to_geojson(geometry)
        js = json.loads(js_str)
        f.write(json.dumps(js))


def geometry2geojsonfile_via_geopandas(geometry: geometry, epsg_code, geojsonfile: str):
    gdf = gpd.GeoDataFrame(index=[0], crs=f'epsg:{epsg_code}', geometry=[geometry])
    gdf.set_crs(f'epsg:{epsg_code}')
    gdf.to_file(geojsonfile, driver=GeoJson)


def write_raster(data: xr.DataArray, file):
    data.rio.to_raster(file)


def write_s1_raster(ncfile, outfile):
    nc_ds = xr.open_dataset(ncfile, decode_coords="all")
    sd = nc_ds.snow_depth
    sd1 = sd.transpose('time', 'y', 'x')
    sd1.rio.to_raster(outfile)


def boundingbox_from_gt(geoTransform: list, xsize, ysize):
    """
    given geotransform list and size list, return bounding box
    :param geoTransform:
    :param xsize
    :param ysize
    :return: bounds [minlon, minlat, maxlon, maxlat]
    """
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * xsize
    miny = maxy + geoTransform[5] * ysize

    return [minx, miny, maxx, maxy]


def convert_datetime64_2_datetime(datetime64):

    ts = pd.Timestamp(datetime64)

    datetime = ts.to_pydatetime()

    return datetime


def datestr_2_datetime64(datestr):

    date = np.datetime64(datetime.strptime(f'{datestr} 00:00:00', '%Y-%m-%d %H:%M:%S'))

    return date

def extract_outline_from_raster(rasterfile, outputfile):
    import rasterio as rio
    from rasterio.features import dataset_features
    import geopandas as gpd

    '''
    with rio.open(rasterfile) as ds:
        shapes = list(dataset_features(ds, bidx=1, as_mask=True, geographic=False, band=False))

        for shape in shapes:
            print(shape['geometry'])
    '''
    # Or as a GeoDataFrame
    with rio.open(rasterfile) as ds:
        gdf = gpd.GeoDataFrame.from_features(dataset_features(ds, bidx=1, as_mask=True, geographic=False, band=False))
        gdf.set_crs(crs=ds.crs, inplace=True, allow_override=True)
        gdf.to_file(outputfile)

    return outputfile

def shrink_geometry(shpfile, outputfile, buff= -50.0):
    import fiona
    from shapely.geometry import (shape, MultiPolygon, Polygon)
    from shapely import (to_geojson, from_geojson)
    import geopandas as gpd
    from pathlib import Path

    # c1 = fiona.open(shpfile)

    gdf_in = gpd.read_file(shpfile)

    poly_list = [item.buffer(distance=buff) for item in gdf_in['geometry']]
    if len(poly_list) == 1:
        geom = poly_list[0]
    else:
        geom = MultiPolygon(poly_list)
    #geometry = GeoSeries(poly_list)

    gdf = gpd.GeoDataFrame(index=[0], crs=gdf_in.crs, geometry = [geom])

    gdf.to_file(outputfile, driver='ESRI Shapefile')

    return poly_list

