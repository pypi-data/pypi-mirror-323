from pathlib import Path
from asf_snow.utils.analyze_snex import *


def read_snotel(snotelfile:str=None, snotelsite:str=None, lon:float=None, lat:float=None, stdate:str=None, eddate:str=None):
    # Creamers' field
    # Latitude:	64.87
    # Longitude:	-147.74
    if snotelfile:
        filename = str(Path(snotelfile).stem)
        if filename.find("creamers") != -1 or filename.find("fieldinglake") != -1:
            snotel = read_snotel_sd_precip_ratio_temp(snotelfile, lon, lat, {})

        else:
            snotel = read_snotel_sd_precip_temp(snotelfile, lon, lat, {})
            # convert date string to datetime64
            snotel['Time'] = pd.to_datetime(snotel['Time'])
            # only consider stdate to eddate period
            if stdate and eddate:
                mask = (snotel['Time'] >= stdate) & (snotel['Time'] <= eddate)
                snotel = snotel[mask]

        snotel = snotel.set_index(['time'])
        snotel['Time'] = snotel.index
    else:
        snotel = get_snotel(snotelsite=snotelsite, stdate=stdate, eddate=eddate)
        snotel = snotel.set_index(['Time'])
        snotel['time'] = snotel.index

    snotel['date'] = snotel.index.date
    snotel = snotel.set_geometry("geometry")

    return snotel


def download_snotel(snotelsite, stdate, eddate, snotelfile):
    if not snotelfile.exists():
        snotel = read_snotel(snotelsite=snotelsite, stdate=stdate, eddate=eddate)
        snotel.to_file(snotelfile, driver='GeoJSON')
    else:
        snotel = gpd.read_file(snotelfile)

        snotel = snotel.set_index(['Time'])
        snotel.index = snotel.index.tz_localize(None)
        snotel['time'] = snotel.index
        snotel['date'] = snotel.index.date

    return snotelfile, snotel

