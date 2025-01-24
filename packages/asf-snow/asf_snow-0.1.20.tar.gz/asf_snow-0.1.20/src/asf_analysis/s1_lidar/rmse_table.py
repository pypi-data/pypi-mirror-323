#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt

from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error, mean_absolute_error

from spicy_snow.retrieval import retrieval_from_parameters


def bias(x, y): return np.mean(x - y)

def get_stats(x, y, nrmse = False):
    if type(x) == xr.DataArray: x = x.values.ravel()
    if type(y) == xr.DataArray: y = y.values.ravel()
    if type(x) == list: x = np.array(x)
    if type(y) == list: y = np.array(y)
    idx = (~np.isnan(x)) & (~np.isnan(y))
    x, y = x[idx], y[idx]
    r, p = pearsonr(x, y)
    b = bias(x, y)
    mae = mean_absolute_error(x, y)

    # rmse = mean_squared_error(x, y, squared = False)
    rmse = mean_squared_error(x, y)

    if nrmse:
        nrmse_value = rmse / np.mean(x)
        return r, b, mae, rmse, nrmse_value

    return r, b, mae, rmse

from scipy.stats import norm
def fischerz(truth, x1, x2):
    idx1 = (~np.isnan(truth)) & (~np.isnan(x1))
    idx2 = (~np.isnan(truth)) & (~np.isnan(x2))
    n = np.min([len(x1[idx1]), len(x2[idx2])])
    cor1 = pearsonr(truth[idx1], x1[idx1]).statistic
    cor2 = pearsonr(truth[idx2], x2[idx2]).statistic
    fischer1 = 0.5*np.log((1+cor1)/(1-cor1))
    fischer2 = 0.5*np.log((1+cor2)/(1-cor2))
    expected_sd = np.sqrt(1/(n-3))
    return 2 * (1 - norm(0, expected_sd).cdf(np.abs(fischer1 - fischer2)))


# In[ ]:


# npy_dirs = Path('/bsuhome/zacharykeskinen/scratch/spicy/param_npys')
# all_res = xr.open_dataset(npy_dirs.joinpath('grouped.nc'))
# all_res_dry = xr.open_dataset(npy_dirs.joinpath('dry_grouped.nc'))
# A = all_res.max('B').min('C')['pearsonr'].idxmax('A')
# B = all_res['pearsonr'].max('A').min('C').idxmax('B')
# print(A)
# print(B)
# print(all_res['mae'].sel(A = A, B = B).idxmin('C'))


# new table with WUS

# In[ ]:

# statscvsfile = '/home/jiangzhu/data/crrel/lidar_via_zach/scratch/spicy/SnowEx-Data-lave/stats_new.csv'

def stats_table_new(in_dir, statscvsfile):

    res = pd.DataFrame()

    dss = {fp.stem: xr.open_dataset(fp, decode_coords="all") for fp in in_dir.glob('*.nc')}
    mean_all = 0
    xs, ys = [], []
    dry_xs, dry_ys = [], []
    for stem, full_ds in dss.items():

        if stem == 'Frasier_2020-02-11':
            lidar_time = pd.to_datetime('2020-02-16')
            im_time = pd.to_datetime('2020-02-16')
        else:
            lidar_time = pd.to_datetime(full_ds.attrs['lidar-flight-time'])
            # drop the data at the sel_time
            full_ds_tmp = full_ds.drop_sel(time=lidar_time)
            im_time = pd.to_datetime(full_ds_tmp.sel(time = lidar_time, method = 'nearest').time.values.ravel()[0])

        d_days = im_time - lidar_time
        site_name = stem.replace('_', ' ').replace('Frasier', 'Fraser').split('-')[0]


        ds_img = full_ds.sel(time = im_time, method = 'nearest')
        ds_lidar = full_ds.sel(time = lidar_time, method = 'nearest')

        mean_all += ds_img['snow_depth'].mean()

        full_r, full_b, full_mae, full_rmse, full_nrmse = get_stats(ds_img['snow_depth'], ds_lidar['lidar-sd'], nrmse = True)
        # add RMSE and bias @ 90m
        for name, var in zip(['RMSE', 'Pearson R', 'nRMSE', 'Bias'], [full_rmse, full_r, full_nrmse, full_b]):
            res.loc[site_name, name] = var
        ys.extend(ds_lidar['lidar-sd'].data.ravel())
        xs.extend(ds_img['snow_depth'].data.ravel())

        # for dry only
        idx = ds_img['wet_snow'] == 0
        r, b, mae, rmse, nrmse  = get_stats(ds_img['snow_depth'].where(idx), ds_lidar['lidar-sd'].where(idx), nrmse = True)
        for name, var in zip(['RMSE', 'Pearson R', 'Bias'], [rmse, r, b]):
            res.loc[site_name, name + ' (Dry)'] = var
        res.loc[site_name, 'dry Fischer'] = fischerz(ds_lidar['lidar-sd'].data.ravel(), ds_img['snow_depth'].data.ravel(), ds_img['snow_depth'].where(idx).data.ravel())
        dry_ys.extend(ds_lidar['lidar-sd'].where(idx).data.ravel())
        dry_xs.extend(ds_img['snow_depth'].where(idx).data.ravel())

        # WUS over Lievens Improvement RMSE
        # l_ds = retrieval_from_parameters(full_ds, A = lievens_params[0], B = lievens_params[1], C = lievens_params[2]).sel(time = im_date, method = 'nearest')
        # l_r, l_b, l_mae, l_rmse, l_nrmse = get_stats(l_ds['lidar-sd'], l_ds['snow_depth'], nrmse = True)
        # res.loc[site_name, 'L22 RMSE'] = l_rmse
        # res.loc[site_name, 'L22 R'] = l_r
        # res.loc[site_name, 'L22 Fischer'] = fischerz(l_ds['lidar-sd'].data.ravel(), l_ds['snow_depth'].data.ravel(), ds['snow_depth'].data.ravel())
        res.loc[site_name, 'mean-all-sd'] = ds_lidar['lidar-sd'].mean().data.ravel()[0]
        res.loc[site_name, 'mean-dry-sd'] = ds_lidar['lidar-sd'].where(idx).mean().data.ravel()[0]

    r, b, mae, rmse = get_stats(xs, ys)
    for name, var in zip(['RMSE', 'Pearson R', 'Bias'], [rmse, r, b]):
        # res.loc['All Sites', name] = all_res.sel(A = 1.5, B = 0.1, C = 0.60)[name.lower().replace(' ', '')]
        res.loc['All Sites', name] = var
    # res.loc['All Site', 'nRMSE'] = all_res.sel(A = 1.5, B = 0.1, C = 0.60)['rmse'] /(mean_all / (len(dss)))

    r, b, mae, rmse = get_stats(dry_xs, dry_ys)
    for name, var in zip(['RMSE', 'Pearson R', 'Bias'], [rmse, r, b]):
        # res.loc[site_name, name + ' (Dry)'] = all_res_dry.sel(A = 1.5, B = 0.1, C = 0.60)[name.lower().replace(' ', '')]
        res.loc['All Sites', name + ' (Dry)'] = var

    res.loc['All Sites', 'dry Fischer'] = fischerz(xr.DataArray(ys), xr.DataArray(xs), xr.DataArray(dry_xs))

    res.loc['All Sites', 'mean-all-sd'] = np.nanmean(ys)
    res.loc['All Sites', 'mean-dry-sd'] = np.nanmean(dry_ys)
    # res.loc['All Sites', 'L22 RMSE'] = all_res.sel(A = 1.5, B = 0.1, C = 0.60)['rmse'] - all_res.sel(A = lievens_params[0], B = lievens_params[1], C = lievens_params[2])['rmse']
    # res.loc['All Sites', 'L22 R'] = all_res.sel(A = 1.5, B = 0.1, C = 0.60)['pearsonr'] - all_res.sel(A = lievens_params[0], B = lievens_params[1], C = lievens_params[2])['pearsonr']


    # In[ ]:


    res = res.applymap(lambda x: f'{x:.2f}').reindex(['All Sites', 'Banner 2020', 'Banner 2021', 'Dry Creek 2020',\
         'Fraser 2020', 'Fraser 2021', 'Little Cottonwood 2021', 'Mores 2020', 'Mores 2021', 'Cameron 2021'])
    res.drop(['nRMSE'], axis = 1)

    res.to_csv(statscvsfile)


    # In[ ]:


    for r in res[['Bias', 'Bias (Dry)']].values:
        print(f'& {r[0]} & {r[1]}')

    return res


def stats_table_old(in_dir, statscsvfile):
    # # old table with spatial resolutions

    # In[ ]:


    res = pd.DataFrame()
    coarse_x = []
    coarse_y = []

    coarse_x_1k = []
    coarse_y_1k = []
    dss = {fp.stem: xr.open_dataset(fp) for fp in in_dir.glob('*.nc')}

    for stem, ds in dss.items():

        if stem == 'Frasier_2020-02-11':
            lidar_time = pd.to_datetime('2020-02-16')
            im_time = pd.to_datetime('2020-02-16')
            r, b, mae, rmse = get_stats(ds['lidar-sd'], ds['snow_depth'].sel(time = '2020-02-16'))


        else:
            lidar_time = pd.to_datetime(ds.attrs['lidar-flight-time'])
            # drop the data at the sel_time
            ds_tmp = ds.drop_sel(time=lidar_time)
            im_time = pd.to_datetime(ds_tmp.sel(time = lidar_time, method = 'nearest').time.values.ravel()[0])

            ds_lidar =  ds.sel(time = lidar_time, method = 'nearest')
            ds_im = ds.sel(time = im_time, method = 'nearest')

            r, b, mae, rmse = get_stats(ds_lidar['lidar_sd'], ds_im['snow_depth'])

        d_days = im_time - lidar_time

        site_name = stem.replace('_', ' ').split('-')[0]

        # add RMSE and bias @ 90m
        for name, var in zip(['RMSE', 'Pearson R'], [rmse, r]):
            res.loc[site_name, name] = var

        # for dry only
        idx = ds['wet_snow'].sel(time = im_time, method = 'nearest') == 0
        r, b, mae, rmse  = get_stats(ds['lidar-sd'].where(idx), ds['snow_depth'].sel(time = im_time, method = 'nearest').where(idx))
        for name, var in zip(['RMSE'], [rmse]):
            res.loc[site_name, name + ' (Dry)'] = var

        # @ 300 m
        ds_500 = ds.coarsen(x = 3, y = 3, boundary = 'pad').mean()
        r, b, mae, rmse  = get_stats(ds_500['lidar-sd'], ds_500['snow_depth'].sel(time = im_time, method = 'nearest'))
        coarse_x.append(ds_500['lidar-sd'].values.ravel())
        coarse_y.append(ds_500['snow_depth'].sel(time = im_time, method = 'nearest').values.ravel())

        for name, var in zip(['RMSE', 'Pearson R'], [rmse, r]):
            res.loc[site_name, name+' @ 300m'] = var

        # @ 500 m
        ds_500 = ds.coarsen(x = 6, y = 6, boundary = 'pad').mean()
        r, b, mae, rmse  = get_stats(ds_500['lidar-sd'], ds_500['snow_depth'].sel(time = im_time, method = 'nearest'))
        coarse_x.append(ds_500['lidar-sd'].values.ravel())
        coarse_y.append(ds_500['snow_depth'].sel(time = im_time, method = 'nearest').values.ravel())

        for name, var in zip(['RMSE', 'Pearson R'], [rmse, r]):
            res.loc[site_name, name+' @ 500m'] = var

        # @ 1 km

        ds_500 = ds.coarsen(x = 11, y = 11, boundary = 'pad').mean()
        r, b, mae, rmse  = get_stats(ds_500['lidar-sd'], ds_500['snow_depth'].sel(time = im_time, method = 'nearest'))
        coarse_x_1k.append(ds_500['lidar-sd'].values.ravel())
        coarse_y_1k.append(ds_500['snow_depth'].sel(time = im_time, method = 'nearest').values.ravel())

        for name, var in zip(['RMSE', 'Pearson R'], [rmse, r]):
            res.loc[site_name, name+' @ 1km'] = var

    '''
    for name, var in zip(['RMSE', 'Pearson R'], [rmse, r]):
        res.loc['All Sites', name] = all_res.sel(A = 1.5, B = 0.1, C = 0.59)[name.lower().replace(' ', '')]
    '''

    r, b, mae, rmse  = get_stats(np.concatenate(coarse_x).ravel(), np.concatenate(coarse_y).ravel())
    for name, var in zip(['RMSE', 'Pearson R'], [rmse, r]):
        res.loc['All Sites', name+' @ 500m'] = var

    r, b, mae, rmse  = get_stats(np.concatenate(coarse_x_1k).ravel(), np.concatenate(coarse_y_1k).ravel())
    for name, var in zip(['RMSE', 'Pearson R'], [rmse, r]):
        res.loc['All Sites', name+' @ 1km'] = var

    res.to_csv(statscsvfile)

    return res

# In[ ]:

def main():
    lievens_params = [2, 0.5, 0.44]
    # wus_params = [2.5, 0.2, 0.55]
    # wus_v2_params = [1.5, 0.1, 0.59]

    in_dir = Path('/home/jiangzhu/data/crrel/lidar2/scratch').expanduser().resolve()

    data_dir = Path('/home/jiangzhu/data/crrel/lidar2/scratch').expanduser().resolve()

    csvfile_new = '/home/jiangzhu/data/crrel/lidar2/stats_table_new.csv'

    csvfile_old = '/home/jiangzhu/data/crrel/lidar2/stats_table_old.csv'

    res_new = stats_table_new(in_dir, csvfile_new)


    # res_old = stats_table_old(in_dir, csvfile_old), not work yet, need debug it

if __name__ == '__main__':

    main()


