import geopandas as gpd
import pandas as pd
import numpy as np
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from datetime import datetime
from metloom.pointdata import SnotelPointData


def get_snotel(snotelsite:str, stdate:str, eddate:str):
    '''
    read SNOTEL data into a GeoDataframe
    :param siteid: "site_number:state_name:SNTL", for example creamers' field SNOTEL "1302:AK:SNTL"
    :param stsate: yyyy-mm-dd
    :param eddate: yyyy-mm-dd
    :return: GeoDataframe
    '''

    #A LLOWED_VARIABLES is alias of SnotelVariables
    # varlist = ['SNOWDEPTH', 'SWE', 'RH', 'TEMPAVG', 'TEMPMIN', 'TEMPMAX', 'PRECIPITATION','PRECIPITATIONACCUM']
    # "713:CO:SNTL", "MyStation"

    stdate = datetime.strptime(stdate, '%Y-%m-%d')
    eddate = datetime.strptime(eddate, '%Y-%m-%d')

    snotel_point = SnotelPointData(snotelsite, "Mystation")
    df = snotel_point.get_daily_data(stdate, eddate,
                                     [snotel_point.ALLOWED_VARIABLES.SNOWDEPTH,
                                      snotel_point.ALLOWED_VARIABLES.SWE,
                                       snotel_point.ALLOWED_VARIABLES.RH,
                                      snotel_point.ALLOWED_VARIABLES.TEMPAVG,
                                      snotel_point.ALLOWED_VARIABLES.TEMPMIN,
                                      snotel_point.ALLOWED_VARIABLES.TEMPMAX,
                                      snotel_point.ALLOWED_VARIABLES.PRECIPITATION,
                                      snotel_point.ALLOWED_VARIABLES.PRECIPITATIONACCUM]
                                     )

    # convert multiply index to normal columns
    df.reset_index(inplace=True)

    # rename datetime to Time
    df.rename(columns={'datetime': 'Time', 'SNOWDEPTH': 'snow_depth', 'AVG AIR TEMP': 'temp_avg',
                       'PRECIPITATION':'precip_inc'}, inplace=True)

    # convert snow_depth unit form inch to meter
    df['snow_depth'] = df['snow_depth']*0.0254

    return df


def read_snex_csv(file, col_names=None, skiprows=0, comment="#", numeric_cols=None):
    # read csv file into a dataframe
    df = pd.read_csv(file, names=col_names, comment=comment)

    # drop the first skiprows
    df.drop(df.index[range(0, skiprows)], axis=0, inplace=True)

    # change numeric columns to float datatype
    # numeric_cols = ['Easting', 'Northing', 'Latitude', 'Longitude', 'DensityA', 'DensityB', 'Density',
    #                'SWEA', 'SWEB', 'SWE', 'HS']

    if numeric_cols:
        for col in numeric_cols:
            df[col] = df[col].astype(float)

    # convert df into GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    # set CRS
    gdf.crs = 'epsg:4326'

    # write gdf to geojson file
    # gdf.to_file("/home/jiangzhu/data/crrel/snex23_swe/snex.geojson",driver='GeoJSON')
    
    return gdf


def read_snotel(file, lon, lat):

    # /home/jiangzhu/data/crrel/SNOTEL/creamersfield/20220801_20230731.csv
    # Latitude: 64 deg; 52 min N, 64.867 Longitude: 147 deg; 44 min W, -147.733
    # UTC = AKST + 9
    col_names = ['Time', 'snow_depth', 'qc_flag', 'qa_flag', 'snow_depth_collection']

    skiprows = 1

    comment = "#"
    df = pd.read_csv(file, names=col_names, comment=comment)

    # drop the first skiprows
    df.drop(df.index[range(0, skiprows)], axis=0, inplace=True)

    # convert Date string to datetime64 and create the time column
    df['time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d')
    # convert AK time to UTC
    df['time'] = df['time'] + pd.DateOffset(hours=9, minutes=0)
    # convert to float
    df['snow_depth'] = df['snow_depth'].astype(float)
    # convert inch to meter
    df['snow_depth'] = df['snow_depth']*0.0254
    # remove rows with qc_flag='S' or 'N'
    df = df.drop(df[(df['qc_flag'] == 'S') | ( df['qc_flag'] == 'N')].index)
    # convert df into GeoDataFrame
    num = len(df)
    lst_lon = [lon]*num
    lst_lat = [lat]*num

    new_data = {'Longitude': lst_lon, 'Latitude': lst_lat}

    df = df.assign(**new_data)

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    gdf.attrs = {'Location': 'Creamers Field', 'SiteID': 1302, 'County': 'Fairbanks North Star', 'State': 'AK'}

    gdf.crs = 'epsg:4326'

    return gdf


def read_snotel_sd_precip_ratio_temp(file, lon, lat, attrs):

    # /home/jiangzhu/data/crrel/SNOTEL/creamersfield/20220801_20230731.csv
    # Latitude: 64 deg; 52 min N, 64.867 Longitude: 147 deg; 44 min W, -147.733
    # UTC = AKST + 9
    # col_names = ['Time', 'snow_depth', 'qc_flag', 'qa_flag', 'precip_acc', 'precip_inc', 'snow_rain_ratio', 'temp_avg','temp_min']
    # numeric_cols = ['snow_depth', 'precip_acc','precip_inc', 'snow_rain_ratio','temp_avg','temp_min']

    col_names = ['Time', 'snow_depth', 'qc_flag', 'qa_flag', 'precip_acc', 'precip_inc', 'temp_avg','temp_max', 'temp_min', 'snow_density', 'snow_rain_ratio']
    numeric_cols = ['snow_depth', 'precip_acc','precip_inc', 'temp_avg','temp_max', 'temp_min','snow_density', 'snow_rain_ratio']

    skiprows = 1
    comment = "#"
    df = pd.read_csv(file, names=col_names, comment=comment)

    # drop the first skiprows
    df.drop(df.index[range(0, skiprows)], axis=0, inplace=True)

    # convert Date string to datetime64 and create the time column
    df['time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d')
    # convert AK time to UTC
    df['time'] = df['time'] + pd.DateOffset(hours=9, minutes=0)
    # convert to float
    for i in numeric_cols:
        df[i] = df[i].astype(float)

    # convert inch to meter
    df['snow_depth'] = df['snow_depth']*0.0254
    df['precip_inc'] = df['precip_inc']*0.0254
    # remove rows with qc_flag='S' or 'N'
    df = df.drop(df[(df['qc_flag'] == 'S') | ( df['qc_flag'] == 'N')].index)

    # snow_rain_ratio should be in 0 to 100
    ch = df['snow_rain_ratio'] > 100.0
    df.loc[ch, "snow_rain_ratio"] = 100.0

    # convert df into GeoDataFrame
    num = len(df)
    lst_lon = [lon]*num
    lst_lat = [lat]*num

    new_data = {'Longitude': lst_lon, 'Latitude': lst_lat}

    df = df.assign(**new_data)

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    gdf.attrs = attrs

    gdf.crs = 'epsg:4326'

    return gdf

def read_snotel_sd_precip_temp(file, lon, lat, attrs):

    # /home/jiangzhu/data/crrel/SNOTEL/creamersfield/20220801_20230731.csv
    # Latitude: 64 deg; 52 min N, 64.867 Longitude: 147 deg; 44 min W, -147.733
    # UTC = AKST + 9
    col_names = ['Time', 'snow_depth', 'qc_flag', 'qa_flag', 'precip_acc', 'precip_inc', 'temp_avg','temp_max', 'temp_min']
    numeric_cols = ['snow_depth', 'precip_acc','precip_inc','temp_avg','temp_max', 'temp_min']

    skiprows = 1

    comment = "#"
    df = pd.read_csv(file, names=col_names, comment=comment)

    # drop the first skiprows
    df.drop(df.index[range(0, skiprows)], axis=0, inplace=True)

    # convert Date string to datetime64 and create the time column
    df['time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d')
    # convert AK time to UTC
    df['time'] = df['time'] + pd.DateOffset(hours=9, minutes=0)
    # convert to float
    for i in numeric_cols:
        df[i] = df[i].astype(float)

    # convert inch to meter
    df['snow_depth'] = df['snow_depth']*0.0254
    # remove rows with qc_flag='S' or 'N'
    df = df.drop(df[(df['qc_flag'] == 'S') | ( df['qc_flag'] == 'N')].index)
    # convert df into GeoDataFrame
    num = len(df)
    lst_lon = [lon]*num
    lst_lat = [lat]*num

    new_data = {'Longitude': lst_lon, 'Latitude': lst_lat}

    df = df.assign(**new_data)

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    gdf.attrs = attrs

    gdf.crs = 'epsg:4326'

    return gdf




def read_snex23_swe(file):
    """read SNEX23_SWE_*.csv file.
    https://nsidc.org/data/snowex/data?field_data_set_keyword_value=5
    https://nsidc.org/data/snex23_swe/versions/1.
    :param file: SNEX23_SWE_Mar23IOP_AK_20230313_20230316_v01.0.csv
    :return: GeoDataFrame
    """
    col_names = ['State', 'County', 'Site ID', 'Latitude', 'Longitude', 'Elevation', 'Date', 'Depth1', 'Depth2',
                 'Depth3', 'Mass1', 'Mass2', 'Mass3', 'Density1', 'Density2', 'Density3', 'SWE1', 'SWE2', 'SWE3']

    skiprows = 4

    comment = "#"

    numeric_cols = ['Latitude', 'Longitude', 'Elevation', 'Depth1', 'Depth2', 'Depth3', 'Mass1', 'Mass2', 'Mass3',
                    'Density1', 'Density2', 'Density3', 'SWE1', 'SWE2', 'SWE3']
    gdf = read_snex_csv(file, col_names=col_names, skiprows=skiprows, comment=comment, numeric_cols=numeric_cols)

    # convert Date string to datetime64 and create the time column
    gdf['time'] = pd.to_datetime(gdf['Date'], format='%d-%b-%y')
    # convert AK time to UTC
    gdf['time'] = gdf['time'] + pd.DateOffset(hours=9, minutes=0)

    gdf.rename(columns={'Date': 'Time', 'County': 'Location'}, inplace=True)

    # eliminate the bad record in the gdf
    gdf = gdf[(gdf['Depth1'] >= 0.0) & (gdf['Depth2'] >= 0.0) & (gdf['Depth3'] >= 0.0)]

    # calculate the average, snow+depth unit is in meter
    gdf['snow_depth'] = 0.01*(gdf['Depth1'] + gdf['Depth2'] + gdf['Depth3'])/3.0
    gdf['SWE'] = (gdf['SWE1'] + gdf['SWE2'] + gdf['SWE3'])/3.0
    gdf['HS'] = gdf['snow_depth']*100.0
    return gdf


def read_SNEX23_MAR23_SD_AK_20230307_20230316_v01d0(file):

    # SNEX23_MAR23_SD_AK_20230307_20230316_v01.0.csv

    col_names = ['State', 'County', 'Site ID', 'Latitude', 'Longitude', 'Elevation', 'Date', 'Depth1', 'Depth2',
                'Depth3', 'Mass1', 'Mass2', 'Mass3', 'Density1', 'Density2', 'Density3', 'SWE1', 'SWE2', 'SWE3']

    col_names = ['State', 'County', 'Study Area', 'Plot ID', 'ID', 'Date', 'Time', 'Latitude', 'Longitude',
                'Northing', 'Easting', 'Elevation', 'Depth', 'Equipment ID', 'Instrument', 'Version Number']

    skiprows = 2

    comment = "#"

    numeric_cols = ['Latitude', 'Longitude', 'Northing', 'Easting', 'Elevation', 'Depth']

    gdf = read_snex_csv(file, col_names=col_names, skiprows=skiprows, comment=comment, numeric_cols=numeric_cols)

    # eliminate the bad record in the gdf
    gdf = gdf[gdf['Depth'] >= 0.0]
    # snow_depth
    gdf['snow_depth'] = 0.01*gdf['Depth']
    gdf['SWE'] = np.nan
    gdf['HS'] = gdf['Depth']

    return gdf

def read_snex23_snow_water_equivalent(file):
    """read SNEX23_SWE_Mar23IOP_AK_20230313_20230316_v01.0_md.csv
    https://nsidc.org/data/snowex/data?field_data_set_keyword_value=5
    https://nsidc.org/data/snex23_swe/versions/1.
    :param file: SNEX23_SWE_Mar23IOP_AK_20230313_20230316_v01.0.csv
    :return: GeoDataFrame
    """
    col_names = ['State', 'County', 'Site ID', 'Latitude', 'Longitude', 'Elevation', 'Date', 'Depth1', 'Depth2',
                'Depth3', 'Mass1', 'Mass2', 'Mass3', 'Density1', 'Density2', 'Density3', 'SWE1', 'SWE2', 'SWE3']

    skiprows = 2

    comment = "#"

    return read_snex_csv(file, col_names=col_names, skiprows=skiprows, comment=comment)


def read_snex21_ts_summary_swe_v01(file):
    """read the SNEX21_TS_SP_Summary_SWE_v01.csv file
    https://nsidc.org/data/data-access-tool/SNEX21_TS_SP/versions/1
    https://nsidc.org/data/snex21_ts_sp/versions/1
    :param file:SNEX21_TS_SP_Summary_SWE_v01.csv
    :return: GeoDataFrame
    """
    col_names_orig = ['Location', 'Site', 'PitID', 'Date/Local Standard Time', 'UTM Zone', 'Easting (m)',
                      'Northing (m)', 'Latitude', 'Longitude', 'Density A Mean (kg/m^3)', 'Density B Mean (kg/m^3)',
                      'Density Mean (kg/m^3)', 'SWE A (mm)', 'SWE B (mm)', 'SWE (mm)', 'HS (cm)', 'Flag']

    col_names_new = ['Location', 'Site', 'PitID', 'Time', 'UTMZone', 'Easting', 'Northing',
                     'Latitude', 'Longitude', 'DensityA', 'DensityB',
                     'Density', 'SWEA', 'SWEB', 'SWE', 'HS', 'Flag']

    col_rename = {'Date/Local Standard Time': 'Time', 'UTM Zone': 'UTMZone', 'Easting (m)': 'Easting',
                  'Northing (m)': 'Northing', 'Density A Mean (kg/m^3)': 'DensityA',
                  'Density B Mean (kg/m^3)': 'DensityB', 'Density Mean (kg/m^3)':'Density',
                  'SWE A (mm)':'SWEA',  'SWE B (mm)':'SWEB',  'SWE (mm)': 'SWE', 'HS (cm)': 'HS'}


    numeric_cols = ['Easting', 'Northing', 'Latitude', 'Longitude', 'DensityA', 'DensityB', 'Density',
                    'SWEA', 'SWEB', 'SWE', 'HS']

    skiprows = 20

    comment = "#"

    gpd = read_snex_csv(file, col_names=col_names_new, skiprows=skiprows, comment=comment, numeric_cols=numeric_cols)

    # convert Date string to datetime and convert it into UTC (Boise)
    gpd['time'] = pd.to_datetime(gpd['Time'], format='%Y-%m-%dT%H:%M') + pd.DateOffset(hours=6, minutes=0)

    # calculate the snow depth in snex, SWE = hs x ρs/ pw, ps- snow density kg/m3, pw-water density kg/m3 =1000 kg/m3
    # SWE in mm, snex_sd in m, found snex['HS'] is almost equal to snex['snow_depth']

    gpd['snow_depth'] = gpd['SWE']*1000.0/gpd['Density']*0.001

    # gpd['snow_depth'] = gpd['HS']*0.001

    return gpd


def read_snex21_ts_summary_environment_v01(file):
    """read "SNEX21_TS_SP_Summary_Environment_v01.csv"
    :param file: SNEX21_TS_SP_Summary_Environment_v01.csv
    :return: GeoDataFrame
    """

    col_names = ['Location', 'Site', 'PitID', 'Time', 'UTMZone', 'Easting', 'Northing', 'Latitude', 'Longitude',
                 'Precip Type', 'Precip Rate', 'Sky', 'Wind', 'Ground Condition', 'Ground Roughness',
                 'Ground Vegetation', 'Height of Ground Vegetation', 'Canopy']

    numeric_cols = ['Easting', 'Northing', 'Latitude', 'Longitude']

    skiprows = 21

    comment = "#"

    gdf = read_snex_csv(file, col_names=col_names, skiprows=skiprows, comment=comment, numeric_cols=numeric_cols)

    return gdf



'''
def get_gdf(filelist):
    gdf = None
    for file in filelist:
        if gdf is None:
            gdf = read_snex_csv(file, skiprows=0)
        else:
            gdf.append(read_snex_csv(file, skiprows=0))
    return gdf
'''


def main():

    parser = ArgumentParser()

    parser.add_argument('--file')

    args = parser.parse_args()

    gdf  = read_snex21_ts_summary_swe_v01(args.file)


if __name__ == '__main__':

    # file1="/home/jiangzhu/data/crrel/snex23_swe/SNEX23_SWE_Mar23IOP_AK_20230313_20230316_v01.0.csv"

    # file = "/home/jiangzhu/data/crrel/snowEx21_ts_snow_pits_v1/302507681/SNEX21_TS_SP_Summary_SWE_v01.csv"

    main()

    print("completed ...")










