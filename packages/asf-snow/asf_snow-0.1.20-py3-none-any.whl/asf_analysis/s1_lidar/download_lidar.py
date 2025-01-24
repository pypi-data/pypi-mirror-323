from pathlib import Path

from asf_snow.spicy_snow.download.snowex_lidar import download_dem, download_snow_depth,\
      download_veg_height, make_site_ds

lidar_dir = Path('/home/jiangzhu/data/crrel/lidar_via_zach')

def download_lidar_data(lidar_dir):
      download_snow_depth(lidar_dir)
      download_veg_height(lidar_dir)
      download_dem(lidar_dir)

