import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

sys.path.append('/Users/anastasiiagordienko/Desktop/uni/effprogr/effprogr_project/')

from bld.project_paths import project_paths_join as ppj

def plot_time_shift(regions,               # list of integers: corresponding id-s of regions
                    date,                  # string; date in format '%Y-%m-%d'
                    data,                  # dataframe to use
                    date_moscow_var,       # string; name of a date variable in Moscow time (variable must be dateframe type '%Y-%m-%d')
                    date_local_var,        # string; name of a date variable in local time (variable must be dateframe type '%Y-%m-%d')
                    hour_moscow_var,       # string; name of a hour variable in Moscow time (variable must be int type)
                    hour_local_var,        # string; name of a hour variable in local time (variable must be int type)
                    id_region_var,         # string; name of a variable indicating the id-s of regions for plots (variable must be int type)
                    indicator):            # string; name of a variable indicating the outcome variable for plots (variable must be int type)
    '''Returns the dataframe for a given day and regions and
    creates plots indicator vs hour of a day graph for a given day and regions
    in local and Moscow time to show how time in data is shifted.

    As arguments expects list of corresponding id regions (they can be found in regions_code.csv in the "IN_DATA" directory);
    date of a desired day for plots (string of format '%Y-%m-%d'); uploaded dataframe with mentioned name variables for dates
    and hours of a day in Moscow and local time, variables for id of regions and main indicator of interest.

    '''
    nrow = int((len(regions)))
    fig, axs = plt.subplots(nrows = nrow,
                            ncols = 1,
                            sharex = True,
                            gridspec_kw={'hspace': 1},
                            figsize=(8,8))
    fig.suptitle(f"Time shift in data, {date}", fontsize=18)
    fig.subplots_adjust(top=0.85)
    for i in range(len(regions)):
        l1 = axs[i].plot(hour_local_var, indicator,
                        data = data.loc[(data[date_local_var] == date) &
                        (data[id_region_var] == regions[i])],
                        color = 'lightcoral',
                        marker = '*')
        l2 = axs[i].plot(hour_moscow_var, indicator,
                        data = data.loc[(data[date_moscow_var]== date) &
                        (data[id_region_var]==regions[i])],
                        color='slategrey')

        axs[i].set_title(f'in region {regions[i]}')

        for ax in axs.flat:
            ax.set(xlabel='Hour')
        for ax in axs:
            ax.label_outer()

    fig.legend([l1,l2],
                labels = ['Local Time', 'Moscow Time'],
                loc="lower right")
#                borderaxespad=0.01)
    fig.savefig(ppj("OUT_FIGURES", "data_timeshift.png"))


def plot_dst_region(regions,            # list of integers: corresponding id-s of regions
                    date,               # string; date in format '%Y-%m-%d'
                    data,               # dataframe to use
                    date_local_var,     # string; name of a date variable in local time (variable must be dateframe type '%Y-%m-%d')
                    hour_local_var,     # string; name of a hour variable in local time (variable must be int type)
                    id_region_var,      # string; name of a variable indicating the id-s of regions for plots (variable must be int type)
                    week_var,           # string: name of a variable indicating the number of week in local time (variable must be int type)
                    indicator):         # string; name of a variable indicating the outcome variable for plots (variable must be int type)
        '''The function is created to plot hour-averaged indicator values for given regions
        a week before and a week after the date of official shift in time.

        Returns the dataframe for a period of the given date +- a week for each of the given regions with averaged over hours throughout the time period
        and creates line plots indicator vs hour of a day a week before and after time change, for each region separately.

        As arguments expects list of corresponding id regions (they can be found in regions_code.csv in the "IN_DATA" directory);
        date of a desired day for plots (string of format '%Y-%m-%d'); uploaded dataframe with mentioned name variables for dates
        and hours of a day local time, variables for id of regions, number of a week and main indicator of interest.

        '''

        dst_date = datetime.strptime(date, '%Y-%m-%d')
        week_before = dst_date - timedelta(days=6)
        week_after = dst_date + timedelta(days=7)

        nrow = int((len(regions)))

        fig, axs = plt.subplots(nrows = nrow,
                            ncols = 1,
                            sharex = True,
                            gridspec_kw={'hspace': 1},
                            figsize=(8,8))
        fig.subplots_adjust(top=0.85)
        fig.suptitle(f"Weeks before and after time change on {date}")

        for i in range(len(regions)):
            df = data.loc[(data[date_local_var] <= week_after) &
                        (data[ date_local_var] >= week_before) &
                        (data[id_region_var] == regions[i])]

            data_plt = df.groupby([week_var, hour_local_var]).mean()
            data_plt = data_plt.reset_index()
            weeks = df[week_var].unique()
            axs[i].set_title(f'in region {regions[i]}')
            l1 = axs[i].plot(hour_local_var, indicator,
                            data = data_plt[data_plt[week_var]==weeks[0]],
                            color='mediumslateblue')

            l2 = axs[i].plot(hour_local_var, indicator,
                        data = data_plt[data_plt[week_var]==weeks[1]],
                        color='mediumvioletred',
                        marker = '.')
            for ax in axs.flat:
                ax.set(xlabel='Hour')
            for ax in axs:
                ax.label_outer()

                fig.legend([l1,l2],
                        labels = ['Week before time change',
                        'Week after time change'],
                        loc="lower right")

                fig.savefig(ppj("OUT_FIGURES", f"dst_regions_{date}.png"))



def plot_dst_system(systems,            # list of strings: corresponding names of energy systems
                    date,               # date in string format ('%Y-%m-%d')
                    data,               # dataframe to use
                    date_local_var,     # string; name of a date variable in local time (variable must be dateframe type '%Y-%m-%d')
                    hour_local_var,     # string; name of a hour variable in local time (variable must be int type)
                    system_var,         # string; name of a variable indicating the names of systems for plots (variable must be obj type)
                    indicator):         # string; name of a variable indicating the outcome variable for plots (variable must be int type)
        '''The function is created to plot hour-averaged indicator values for given energy systems
        a week before and a week after the date of official shift in time.

        Returns the dataframe for a period of the given date +- a week for each of the given energy systems with averaged over hours throughout the time period
        and creates line plots indicator vs hour of a day a week before and after time change, for each energy system separately.

        As arguments expects list of corresponding titles of energy systems (they can be found in regions_code.csv in the "IN_DATA" directory);
        date of a desired day for plots (string of format '%Y-%m-%d'); uploaded dataframe with mentioned name variables for dates
        and hours of a day local time, variables for names of energy systems, number of a week and main indicator of interest.

        '''

        cons_system = data.groupby([hour_local_var,date_local_var,system_var]).agg({indicator: "sum"})
        cons_system = cons_system.reset_index()

        datatime = pd.DatetimeIndex(cons_system[date_local_var])
        cons_system.loc[:,'week_local'] = datatime.week
        dst_date = datetime.strptime(date, '%Y-%m-%d')
        week_before = dst_date - timedelta(days=6)
        week_after = dst_date + timedelta(days=7)

        nrow = int(len(systems))

        fig, axs = plt.subplots(nrows = nrow,
                                ncols = 1,
                                sharex = True,
                                gridspec_kw={'hspace': 1},
                                figsize=(8,8))
        fig.subplots_adjust(top=0.85)
        fig.suptitle(f"Weeks before and after time change on {date}")

        for i in range(len(systems)):
            df = cons_system.loc[(cons_system[date_local_var] <= week_after) &
                        (cons_system[date_local_var] >= week_before) &
                        (cons_system[system_var] == systems[i])]
            data_plt = df.groupby(['week_local', hour_local_var]).mean()
            data_plt = data_plt.reset_index()
            weeks = df['week_local'].unique()

            axs[i].set_title(f'in {systems[i]} energy system ')
            l1 = axs[i].plot(hour_local_var, indicator,
                            data = data_plt[data_plt['week_local']==weeks[0]],
                            color='mediumslateblue')
            l2 = axs[i].plot(hour_local_var, indicator,
                            data = data_plt[data_plt['week_local']==weeks[1]],
                            color='mediumvioletred',
                            marker = '.')

            for ax in axs.flat:
                ax.set(xlabel='Hour')
            for ax in axs:
                ax.label_outer()
            fig.legend([l1,l2],
                        labels = ['Week before time change',
                                'Week after time change'],
                                loc="lower right")

            fig.savefig(ppj("OUT_FIGURES", f"dst_systems_{date}.png"))


data = pd.read_csv(ppj('OUT_DATA', 'data_general_local_time.csv'))
data.loc[:,'date_local'] = data['date_local'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
data.loc[:,'local_time'] = data['local_time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
plot_time_shift([41, 57, 25, 5],
                '2014-10-01',
                data,
                'date',
                'date_local',
                'hour',
                'hour_local',
                'id_region',
                'cons_fact')
for d in ['2014-10-26', '2010-10-31', '2011-03-27']:
    plot_dst_region([41, 57, 25, 5],
                d,
                data,
                'date_local',
                'hour_local',
                'id_region',
                'week_local',
                'cons_fact')
for d in ['2014-10-26', '2010-10-31', '2011-03-27']:
    plot_dst_system(['center', 'east', 'siberia', 'ural'],
                d,
                data,
                'date_local',
                'hour_local',
                'system',
                'cons_fact')
