# produce snow depth for Fraser sites
# -105.961, 39.811, -105.748, 40.02


python -m pdb sentinel1_snow.py --username cirrusasf --password Cumulus*189Jzhu! --area -105.961 39.811 -105.748 40.02 --daterange 2021-03-01 2021-03-31 --workdir /home/jiangzhu/data/crrel/sentinel1_snowEx21_ts_snow_pits_v1/fraser/boise_20210301_0331 --jobname jz_snow_fraser_202103 --existjobname jz_snow_fraser_202103 --outnc /home/jiangzhu/data/crrel/sentinel1_snowEx21_ts_snow_pits_v1/fraser/fraser_20210301_0331/sentinel1_20210301_0331.nc



