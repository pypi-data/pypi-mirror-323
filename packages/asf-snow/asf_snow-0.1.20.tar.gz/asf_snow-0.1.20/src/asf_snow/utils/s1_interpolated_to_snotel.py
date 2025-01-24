from asf_snow.utils.analyze_sentinel1_snow import *
from asf_snow.utils.analyze_snex import *
import geopandas as gpd
import numpy as np

s1file = "/home/jiangzhu/data/crrel/SNOTEL/creamersfield/s1_2/sentinel1_creamers_20220801_20230731n_10_12h_12h_s1_average_y_creamers_field.shp"

snotelfile="/home/jiangzhu/data/crrel/SNOTEL/creamersfield/20220801_20230731.csv"

lon = -147.733

lat =  64.867

snotel = read_snotel(snotelfile, lon, lat)
snotel = snotel[~snotel['snow_depth'].isnull()]

snotel.time = snotel['time'] -  np.timedelta64(9, 'h')

snotel_ts = np.array([item.timestamp() for item in snotel['time']])
#snotel_t = np.array(snotel.time)
#snotel_t1 = snotel_t - np.timedelta64(9, 'h')

s1 = gpd.read_file(s1file)
s1 = s1[~s1['mean'].isnull()]

# s1_t = np.array(s1.time)
s1_ts = np.array([item.timestamp() for item in s1['time']])

s1_mean = np.array(s1['mean'])
s1_min = np.array(s1['min'])
s1_max = np.array(s1['max'])
s1_std = np.array(s1['std'])

snotel_sd = np.array(snotel['snow_depth'])

# interpolate s1 based on times of snotel

s1_interp_mean = np.interp(snotel_ts, s1_ts, s1_mean)
s1_interp_min = np.interp(snotel_ts, s1_ts, s1_min)
s1_interp_max = np.interp(snotel_ts, s1_ts, s1_max)
s1_interp_std = np.interp(snotel_ts, s1_ts, s1_std)


num = len(snotel_ts)

geometry = np.array([s1['geometry'].iloc[0]]*num)

columns = ['time','mean', 'min','max', 'std', 'snex_sd', 'geometry']

parsed =[[snotel_ts[i], s1_interp_mean[i], s1_interp_min[i],
          s1_interp_max[i], s1_interp_std[i], snotel_sd[i], geometry[i]] for i in range(num)]

# create new geoDataframe
gdf = gpd.GeoDataFrame(data=parsed, columns=columns)

gdf = gdf.set_crs('epsg:4326')


# calculate RMSE, R, and MBE
xm = snotel_sd
ym = s1_interp_mean

r = np.corrcoef(ym, xm)
corr = r[0,1]
rmse = np.sqrt(((xm - ym) ** 2).mean())
mbe = np.mean(ym - xm)

stderror =np.array(gdf['std'])

# draw plots
fig, [ax0, ax1] = plt.subplots(nrows=2, ncols=1)

fig.set_figwidth(30)
fig.set_figheight(30)

# mean, obs
s1_mean = "{:.2f}".format(gdf['mean'].mean())
s1_std = "{:.2f}".format(gdf['mean'].std())
obs_mean = "{:.2f}".format(gdf['snex_sd'].mean())
obs_std = "{:.2f}".format(gdf['snex_sd'].std())
corr1 = float("{:.2f}".format(corr))
rmse1 = "{:.2f}".format(rmse)
mbe1 = "{:.2f}".format(mbe)

ax0.plot(gdf.index, gdf['mean'], label=f'S1 Snow Depth, mean {s1_mean},'
                                       f' std {s1_std} ', color='blue')
ax0.errorbar(gdf.index, gdf['mean'], yerr=stderror, color='blue')

ax0.plot(gdf.index, gdf['snex_sd'], label=f'SNOTEL Snow Depth, mean {obs_mean},'
                                          f'std {obs_std}', color='red')
ax0.legend()

ax0.text(0.3, 0.9, f'RMSE {rmse1}, R {corr1}, MBE {mbe1}, Number of observations {len(gdf)}', color='red', transform=ax0.transAxes)

ax0.set_title(f'Zonal Statistic of S1 Snow Depth and SNOTEL Snow Depth')
ax0.set_xlabel(f'Sequence of Observations')
ax0.set_ylabel("snow depth, m")

# differnec with mean standard error bar
diff = gdf['mean'] - gdf['snex_sd']
#diff_mean = "{:.2f}".format(diff.mean())
diff_mean = round(diff.mean(), 2)
#diff_std = "{:.2f}".format(diff.std())
diff_std = round(diff.std(), 2)
ax1.errorbar(gdf.index, diff, yerr=stderror, label='Difference with Mean Standard Error', color='red')

ax1.legend()

corr1 = float("{:.2f}".format(corr))

ax1.text(0.6, 0.9, f'Correlation {corr1}, Mean of Difference {diff_mean}, STD {diff_std}', color='red',
         transform = ax1.transAxes)

ax1.set_title(f'The Difference of S1 Snow Depth Depth and SNOTEL Snow Depth')

ax1.set_xlabel(f'Sequence of Observations')

ax1.set_ylabel("Snow Depth, m")

# Number of pixels of mean
#ax2.plot(gdf.index, gdf['count'], label='Number of pixels', color='green')
# ax2.set_xticks(xtks, labels=xtkslb)
#ax2.set_xlabel(f'Sequence of Observations')
#ax2.legend()

outfile = s1file.replace(".shp", "_interp.png")
# create directory if not exist
Path(outfile).parent.mkdir(exist_ok=True)

fig.savefig(outfile)

plt.show()






print("completed ...")
