import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
import glob
from pytz import timezone
sys.path.append('/Users/anastasiiagordienko/Desktop/uni/effprogr/effprogr_project/')
from bld.project_paths import project_paths_join as ppj
import csv
import re

# Import files
# creating a variable with the filenames (to use region codes for merging)

csvs = glob.glob(ppj('IN_DATA', 'Weather/*.csv'))
colnames=['local_time', 'temperature', 'humidity', 'wind_speed', 'clouds']

list_data = []
for file in csvs:
    w = pd.read_csv(file, encoding="cp1251", decimal=",",engine='python', sep=';', names=colnames, skiprows=1)
    w['filename']= os.path.splitext(os.path.basename(file))[0]
    list_data.append(w)
weather = pd.concat(list_data, ignore_index=True)
# too many variables in Weather8 (Khabarovsk), import and concat separately
weather = weather[weather['filename']!='Weather8']
khab = pd.read_csv(ppj('IN_DATA', 'Weather/Weather8.csv'), encoding="cp1251", decimal=",",engine='python', sep=';')
khab = khab[['Местное время в Комсомольске-на-Амуре', 'T', 'U', 'Ff', 'N']]
khab.columns = colnames
khab.loc[:, 'filename'] = "Weather8"
weather = pd.concat([weather, khab], ignore_index=True)
# Leave only regions' codes from the filenames
weather['id_region'] = weather['filename'].apply(lambda x: str(x)[7:]).astype(int)
weather.info()
# Change data types
weather.loc[:, 'temperature'] = pd.to_numeric(weather['temperature'], errors='raise')
weather.loc[:, 'humidity'] = pd.to_numeric(weather['humidity'], errors='raise')
weather.loc[:, 'wind_speed'] = pd.to_numeric(weather['wind_speed'], errors='raise')
weather.loc[:,'local_time'] = weather['local_time'].astype(str).apply(lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M'))
weather.isnull().sum()
# no more than 1% of nan-s per variable
null = weather[weather.isnull().any(axis=1)]

# I saw duplicates somewhere in 2013 (twice repeated hours)
weather.duplicated(subset=['id_region', 'local_time']).any() #True
# Show duplicates in region-date
duplicates = weather[weather.duplicated(['id_region', 'local_time'])]
# 15875 duplicates
print(max(duplicates['local_time']) - min(duplicates['local_time'])) # 40 days
# Indeed, in different days for different region in Jan-Feb 2013 there are twice repeated identical rows
# Drop duplicates
weather_clean = weather.drop_duplicates(subset=['id_region', 'local_time'], keep='first')
weather_clean.duplicated(subset=['id_region', 'local_time']).any() #False
# Filling nan-s as averages of the nearest values
weather_clean.isnull().sum()
weather_clean.loc[:, 'temperature'] = weather_clean.temperature.interpolate().bfill()
weather_clean.loc[:, 'humidity'] = weather_clean.humidity.interpolate().bfill()
weather_clean.loc[:, 'wind_speed'] = weather_clean.wind_speed.interpolate().bfill()

# Extract hours and dates separately from datetime
datatime = pd.DatetimeIndex(weather_clean.local_time)
weather_clean.loc[:,'hour_local'] = datatime.hour
weather_clean.loc[:,'date_local'] = datatime.date
weather_clean.loc[:,'date_local'] = weather_clean.loc[:,'date_local'].astype(str).apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

weather_clean.loc[:,'hour_bins'] = pd.cut(weather_clean["hour_local"],
                                              [0,3,6,9,12,15,18,21,24],
                                              include_lowest = True,
                                              right = False)
weather_clean.drop('filename', axis=1, inplace=True)
weather_clean.to_csv(ppj('OUT_DATA', 'weather_clean.csv'), index=False)
cons = pd.read_csv(ppj('OUT_DATA', 'data_general_local_time.csv'), parse_dates = ["date", "date_local", "local_time"])
cons.loc[:,'hour_bins'] = pd.cut(cons["hour_local"],
                                              [0,3,6,9,12,15,18,21,24],
                                              include_lowest = True,
                                              right = False)
# Sum over regions, dates and hour bins
cons_sum = cons.groupby(['id_region','date_local','hour_bins']).agg({'cons_fact': "sum"})
cons_sum  = cons_sum .reset_index()

datatime = pd.DatetimeIndex(cons_sum.date_local)
cons_sum.loc[:,'year_local'] = datatime.year
cons_sum.loc[:,'month_local'] = datatime.month
cons_sum.loc[:,'day_local'] = datatime.day
cons_sum.loc[:,'weekday_local'] = datatime.weekday
cons_sum.loc[:,'week_local'] = datatime.week
# Attach some more info on the regions
region_codes = pd.read_csv(ppj('IN_DATA', 'regions_codes.csv'),
                           engine='python', sep=';')
cons_sum_full = pd.merge(cons_sum,
                             region_codes[['id_system', 'system', 'region', 'id_region']],
                             on = 'id_region')
cons_weather = pd.merge(cons_sum_full, weather_clean, on = ['id_region', 'date_local', 'hour_bins'], how = 'left')
cons_weather
# check nan-s
cons_weather.isnull().sum()
nan = cons_weather.groupby('id_region').apply(lambda x: x.isnull().sum())
pd.set_option('display.max_rows', nan.shape[0]+1)
print(nan)

cons_weather.to_csv(ppj('OUT_DATA', 'cons_weather.csv'), index=False)

# sun-twilight
sun = pd.read_excel(ppj('IN_DATA', 'ALL_sun.xlsx'), parse_dates = ['Sun'])
twilight = pd.read_excel(ppj('IN_DATA', 'ALL_sun.xlsx'), sheet_name='Twilight', parse_dates = ['Twilight'])
sun = sun.set_index(['Sun'])
twilight = twilight.set_index(['Twilight'])
# to long format
sun_long = sun.unstack().reset_index()
twilight_long = twilight.unstack().reset_index()
sun_long.columns = ['id_region', 'local_time', 'sun']
twilight_long.columns = ['id_region', 'local_time', 'twilight']

sun_twilight = pd.merge(sun_long, twilight_long, on = ['id_region', 'local_time'])
sun_twilight.rename(columns={'local_time': 'local_time_sun'}, inplace=True)
cons_weather.rename(columns={'local_time': 'local_time_weather'}, inplace=True)


datatime = pd.DatetimeIndex(sun_twilight.local_time_sun)
sun_twilight.loc[:,'hour_local'] = datatime.hour
sun_twilight.loc[:,'date_local'] = datatime.date
sun_twilight.loc[:,'date_local'] = sun_twilight.loc[:,'date_local'].astype(str).apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

sun_twilight.loc[:,'hour_bins'] = pd.cut(sun_twilight["hour_local"],
                                              [0,3,6,9,12,15,18,21,24],
                                              include_lowest = True,
                                              right = False)

cons_weather_sun = pd.merge(cons_weather, sun_twilight, on = ['id_region', 'date_local', 'hour_bins'], how = 'left')
cons_weather_sun.drop(['hour_local_x', 'hour_local_y'], axis=1, inplace=True)
cons_weather_sun.loc[:,'twilight'] = cons_weather_sun.twilight.astype('int')
cons_weather_sun.to_csv(ppj('OUT_DATA', 'cons_weather_sun.csv'), index=False)
