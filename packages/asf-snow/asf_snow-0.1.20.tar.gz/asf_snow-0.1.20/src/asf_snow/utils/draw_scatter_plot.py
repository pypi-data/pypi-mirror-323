from asf_snow.utils.compare_sentinel1_snow_depth_to_snex_lidar import *


lidarfile = "/home/jiangzhu/data/crrel/SnowEx20-21_QSI_Lidar_Snow_Depth_0d5m_UTM_Grid_V1/test/lidar_sample.tif"

ncfile = "/home/jiangzhu/data/crrel/SnowEx20-21_QSI_Lidar_Snow_Depth_0d5m_UTM_Grid_V1/test/nc_timerange.tif"

lidar = rio.open_rasterio(lidarfile)

nc = rio.open_rasterio(ncfile)

scatter_plot(lidar[0].data, nc[0].data, "/home/jiangzhu/data/crrel/SnowEx20-21_QSI_Lidar_Snow_Depth_0d5m_UTM_Grid_V1/test/scatter.png")


