import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta
import glob
from pytz import timezone
sys.path.append('/Users/anastasiiagordienko/Desktop/uni/effprogr/effprogr_project/')
from bld.project_paths import project_paths_join as ppj

'''
This code consists of three general parts.

The first part is basically trivial data import and cleaning steps.

First, I import original csv-files from electricity_data folder as Pandas dataframes and append them as one dataframe.
I rename data columns into English; change date variable format to datetime class; create a datetime variable joining original date and hour variables.
I cut data up to the end of 2015 since after 2015 some regions experienced local time shifts (not country-level) which we are not interested in.
I merge this dataframe with imported time_changes.csv on id_region to get informational variables on local UTC-s (timezones) in regions, id and regions and energy systems.
I export this dataframe into 'OUT_DATA' data_general.csv file.

The second part is to change time from Moscow to local time. Originally, in all regions datetime variable is given in Moscow time.
From time_changes.csv I got a *utc_after_DST2014* variable which represents the current UTC for a given region. Except for 4 regions, time timeshifts
in October 2010, March 2011 and October 2014 were country-level, so almost all regions changed time one hour forward or back at 2 am Moscow time.
It means, that time difference between Moscow and a given region was constant during the data period. That is why I create a variable *delta* which is
difference in hours between Moscow and a region's local time. This delta is calculated differently for 4 regions which either did not change time in 2014
or changed it for 2 hours (not 1 hour as did the rest of regions), so the difference between these regions' and Moscow time varied in different time periods.
After creating a proper *delta* variable, I create a new datetime variable by adding to initial datetime var (Moscow time) this delta (specifying values in *delta* as hours).
Thus, a new datetime var represents a local time for each region accounting for specific timeshifts in several regions.
This dataframe is exported into 'OUT_DATA' data_general_local.csv file.

*Note*: thankfully to data source from where used data was retrieved, there is no need in modifying data imposed by timeshifts.
That is, there is no necessity in creating additional rows for hours which were lost due to timeshifts forward in time and
removing rows for additional hours imposed by timeshift back in time. In data such rows are already changed (the lost hours copy the values from the previous hour;
how additional hours were eliminated is yet a mystery).

The final third part is to reshape energy indicator of factual electricity consumption *cons_fact* from hourly frequency into 3-hours dynamics.
This reshaping is needed for the further analysis, since we have weather data for each 3 hours only.
First, I create hour bins in local time, 3 hours in each bin: [0,3), [3,6),..., [21,24). Then I just sum *cons_fact* for each hour bin, date and region (local time).
I extract some time-related columns (month, year, weekday etc.), attach info variables on id of regions and systems and export this dataframe into 'OUT_DATA' cons_sum_local_time.csv file.

As a result of this code implementation, there are three new csv files in 'OUT_DATA' folder.
*data_general* is data for all regions we have with the correct variable formats, MOSCOW time.
*data_general_local* is *data_general* with additional variables corresponding to LOCAL time.
*cons_sum_local_time* is summed cons_fact for each three-hour bins in LOCAL time.

'''
##### Import several cvs-s into one dataframe
csvs = glob.glob(ppj('IN_DATA', 'electricity_data/*.csv'))

list_data = []
for file in csvs:
    general = pd.read_csv(file, encoding="cp1251", decimal=",",engine='python', sep=';')
    list_data.append(general)

data = pd.concat(list_data, ignore_index=True)
data.columns = ['date', 'hour', 'id_region', 'id_system', 'region', 'ibr_av',
'ibr_max', 'gen_plan', 'cons_plan', 'gen_fact', 'cons_fact']
##### Join date and hour variables to get a full date variable
data.loc[:,'date_hour'] = data['date'].astype(str) + " " + data['hour'].astype(str) + ":00"
##### Set dateframe format. This is MOSCOW TIME (UTC +3)
data.loc[:,'date_hour'] = data['date_hour'].apply(lambda x: datetime.strptime(x, '%d-%m-%Y %H:%M'))
data.loc[:,'date'] = data['date'].apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))
##### Do not need data after 2015 for now, cut it
end_date = datetime.strptime('31-12-2015 23:00', '%d-%m-%Y %H:%M')
data_cut = data.loc[data['date_hour']<=end_date]
#data = data.set_index(['date_hour', 'id_region'])
##### Import another csv with info on timezones' changes in the regions
time_changes = pd.read_csv(ppj('IN_DATA', 'time_changes.csv'), engine='python', sep=';')
#### Merge on id_region
data_general = pd.merge(data_cut, time_changes[['utc_after_DST2014', 'id_region', 'id_system', 'system']], on = 'id_region')
data_general.to_csv(ppj('OUT_DATA', 'data_general.csv'))

################################################################################
##### Define dates of DST-related time changes (Moscow time)
dst_2010 = datetime.strptime('31-10-2010 2:00', '%d-%m-%Y %H:%M')
st_2011 = datetime.strptime('27-03-2011 2:00', '%d-%m-%Y %H:%M')
wt_2014 = datetime.strptime('26-10-2014 2:00', '%d-%m-%Y %H:%M')

##### A mask for regions that did not change time in 2014
no_wt_regions = [32, 36, 94]
mask = (data_general['id_region'].isin(no_wt_regions)) & (data_general['date_hour'] < wt_2014)
##### Calculate difference in time with Moscow
data_general.loc[:,'delta'] = np.where(mask,
                                      data_general['utc_after_DST2014'] - 4,
                                      data_general['utc_after_DST2014'] - 3)
##### 76 region set time 2 hours back, not 1 as all other regions
data_general.loc[:,'delta'] = np.where((data_general['id_region'] == 76) &
                                        (data_general['date_hour'] < wt_2014),
                                        data_general['delta'] + 1,
                                        data_general['delta'])
##### This is to set timezone in the date variable - did not use further
#data['msk_time_zone'] = data['date_hour'].replace(tzinfo=timezone('Etc/GMT+3'))
#data['msk_time_zone'] = data['date_hour'].dt.tz_localize('Etc/GMT+3')

##### Trials on UTC changing
# adds days
#data_new['local'] = data_new['date_hour'] + data_new['delta'].map(timedelta)
#new_df = data_new['date_hour'].apply(lambda x: str(x + timedelta(hours=data_new['delta'])))
#def convert_datetime(region, delta):
#        new_df = data.date_hour[(data['id_region'] == region)].apply(lambda x: str(x + timedelta(hours=delta)))
#        return(new_df)
#def map_values(row, values_dict):
#    return values_dict[row]

#values_dict = {50:2}

#data['delta'] = data['id_region'].apply(map_values, args = (values_dict,))

##### This finally worked: creates a new date variable in LOCAL TIME
##### adding the calculated delta to Moscow time
data_general.loc[:,'local_time'] = data_general['date_hour'] + pd.TimedeltaIndex(data_general['delta'], unit='H')
##### Extract hours, months, days, years for local time
datatime = pd.DatetimeIndex(data_general.local_time)
data_general.loc[:,'year_local'] = datatime.year
data_general.loc[:,'month_local'] = datatime.month
data_general.loc[:,'day_local'] = datatime.day
data_general.loc[:,'hour_local'] = datatime.hour
data_general.loc[:,'date_local'] = datatime.date
data_general.loc[:,'weekday_local'] = datatime.weekday
data_general.loc[:,'week_local'] = datatime.week
start_date = datetime.strptime('01-08-2010 00:00', '%d-%m-%Y %H:%M')
end_date = datetime.strptime('31-12-2015 23:00', '%d-%m-%Y %H:%M')
data_general_local = data_general.loc[(data_general['local_time']<=end_date)
                                    & (data_general['local_time']>=start_date)]
data_general_local.to_csv(ppj('OUT_DATA', 'data_general_local_time.csv'))
################################################################################
data_general_local.loc[:,'hour_bins'] = pd.cut(data_general_local["hour_local"],
                                              [0,3,6,9,12,15,18,21,24],
                                              include_lowest = True,
                                              right = False)
##### Sum over regions, dates and hour bins
cons_fact_sum = data_general_local.groupby(['id_region','date_local','hour_bins']).agg({'cons_fact': "sum"})
cons_fact_sum = cons_fact_sum.reset_index()
##### Extract year, month, day of a month, weekday
datatime = pd.DatetimeIndex(cons_fact_sum.date_local)
cons_fact_sum.loc[:,'year_local'] = datatime.year
cons_fact_sum.loc[:,'month_local'] = datatime.month
cons_fact_sum.loc[:,'day_local'] = datatime.day
cons_fact_sum.loc[:,'weekday_local'] = datatime.weekday
cons_fact_sum.loc[:,'week_local'] = datatime.week

##### Attach some more info on regions
region_codes = pd.read_csv(ppj('IN_DATA', 'regions_codes.csv'),
                           engine='python', sep=';')
cons_fact_sum_full = pd.merge(cons_fact_sum,
                             region_codes[['id_system', 'system', 'region', 'id_region']],
                             on = 'id_region')
cons_fact_sum_full.to_csv(ppj('OUT_DATA', 'cons_sum_local_time.csv'))
