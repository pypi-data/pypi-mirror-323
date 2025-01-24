from asf_snow.utils.compare_sentinel1_snow_depth_to_snex_lidar import *

file="/home/jiangzhu/data/crrel/SnowEx20-21_QSI_Lidar_Snow_Depth_0d5m_UTM_Grid_V1/store.pckl"

f = open(file, 'rb')

lidar, nc = pickle.load(f)

f.close()

scatter_plot(lidar,nc, '/home/jiangzhu/data/crrel/SnowEx20-21_QSI_Lidar_Snow_Depth_0d5m_UTM_Grid_V1/test_scatter.png')


