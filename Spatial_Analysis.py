import pandas as pd
import numpy as np
from collections import Counter
import math
import random
import matplotlib.pyplot as plt
import geopandas
import contextily as ctx
from mpl_toolkits.axes_grid1 import make_axes_locatable

# read STL data
school = pd.read_csv("Demand/Pima_OD_UA_team_School_2267_Travel/Pima_OD_UA_team_2267_od_all.csv")
summer = pd.read_csv("Demand/Pima_OD_UA_team_Summer_7548_Travel/Pima_OD_UA_team_7548_od_all.csv")
snow = pd.read_csv("Demand/Pima_OD_UA_team_Snowbirds_6202_Travel/Pima_OD_UA_team_6202_od_all.csv")

# read shapefile
taz = geopandas.read_file("D:/A - Project/TucsonModel/Pima-County---Regional_2017_TAZ_ZoneSet/zone_set_2017_TAZ.shp")
taz.plot()

input_file = school
# demand - summer, school, snow
demand_dt = input_file
demand_dt.columns
set(demand_dt['Day Type'])
demand_dt = demand_dt[demand_dt['Day Type'] == '1: Average Weekday (M-Th)']

# keep only O, D, OD traffic
demand_dt = demand_dt[['Origin Zone ID', 'Destination Zone ID', 'Day Part', 'O-D Traffic (Calibrated Index)']]
# remove redundant rows!
set(demand_dt['Day Part'])
demand_dt = demand_dt[demand_dt['Day Part'] != '00: All Day (12am-12am)']
demand_dt['time'] = demand_dt['Day Part'].astype(str).str[4:8]
demand_dt = demand_dt.drop('Day Part', axis=1)
# Counter(demand_dt['time'])
demand_dt.rename(columns={'Origin Zone ID': 'Orig',
                          'Destination Zone ID': 'Dest'},
                 inplace=True)
set(demand_dt['time'])

# create example 1-1104, 0-23
x1 = 1
x2 = 1104  # number of zones
x = list(range(x1, x2 + 1))
Orig = np.repeat(x, x2)
len(Orig)  # 1218816
Orig = list(Orig) * 24

x1 = 1
x2 = 1104  # number of zones
x = list(range(x1, x2 + 1))
Dest = x * x2
len(Dest)  # 1218816
Dest = list(Dest) * 24

# hr = list(range(0, 1380 + 60, 60))
hr = list(['12am', '1am ', '2am ', '3am ', '4am ', '5am ', '6am ', '7am ', '8am ',
           '9am ', '10am', '11am', '12pm', '1pm ', '2pm ', '3pm ', '4pm ',
           '5pm ', '6pm ', '7pm ', '8pm ', '9pm ', '10pm', '11pm'])
hr = np.repeat(hr, 1218816)

example = pd.DataFrame({'Orig': Orig, 'Dest': Dest, 'time': hr})
example.shape

od_complete = example.merge(demand_dt, on=['Orig', 'Dest', 'time'], how='left')

# missing rate by region - peak hours - 7,8,9 AM 4,5,6 PM
nonmiss = od_complete[-pd.isnull(od_complete['O-D Traffic (Calibrated Index)'])]
cmp = plt.cm.OrRd
cmp.set_under(color='green')

peak_hour = ['7am ', '8am ', '9am ', '4pm ', '5pm ', '6pm ']

# orgin
for time in peak_hour:
    nonmiss_hour = nonmiss[nonmiss['time'] == time]

    # origin no missing values - can sum together
    origin = nonmiss_hour[['Orig', 'O-D Traffic (Calibrated Index)']].groupby('Orig').sum(). \
        reset_index(). \
        rename(columns={'O-D Traffic (Calibrated Index)': 'OD_traffic', 'Orig': 'id'})

    taz_combined_miss = taz.merge(origin, on='id', how='left')
    # taz_combined_miss['OD_traffic'].isna().sum()  # 29 origin zones no traffic
    taz_combined = taz_combined_miss[taz_combined_miss['OD_traffic'] >= 0]

    # fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax = taz_combined_miss.plot(color="grey", figsize=(18, 12))

    # Using vmin and vmax forces the range for the colors
    taz_combined.plot(column='OD_traffic', cmap=cmp, ax=ax, legend=True, vmin=0.0000001, vmax=3000)
    plt.grid(linestyle='dotted', color='gray')
    plt.title(
        "Origin " + time + ", # missing zones (in grey) = %d,\n " % (taz_combined_miss['OD_traffic'].isna().sum()) +
        "# zones with zero traffic (in green)= %d" % len(taz_combined[taz_combined['OD_traffic'] == 0]),
        fontsize=22)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel('Longitude', fontsize=18)
    plt.ylabel('Latitude', fontsize=18)
    plt.savefig("orig_" + time)

# dest
for time in peak_hour:
    nonmiss_hour = nonmiss[nonmiss['time'] == time]

    # origin no missing values - can sum together
    dest = nonmiss_hour[['Dest', 'O-D Traffic (Calibrated Index)']].groupby('Dest').sum(). \
        reset_index(). \
        rename(columns={'O-D Traffic (Calibrated Index)': 'OD_traffic', 'Dest': 'id'})

    taz_combined_miss = taz.merge(dest, on='id', how='left')
    # taz_combined_miss['OD_traffic'].isna().sum()  # 29 origin zones no traffic
    taz_combined = taz_combined_miss[taz_combined_miss['OD_traffic'] >= 0]

    # fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax = taz_combined_miss.plot(color="grey", figsize=(18, 12))

    # Using vmin and vmax forces the range for the colors
    taz_combined.plot(column='OD_traffic', cmap=cmp, ax=ax, legend=True, vmin=0.0000001, vmax=3000)
    plt.grid(linestyle='dotted', color='gray')
    plt.title(
        "Destination " + time + ", # missing zones (in grey) = %d,\n "
        % (taz_combined_miss['OD_traffic'].isna().sum()) +
        "# zones with zero traffic (in green)= %d" % len(taz_combined[taz_combined['OD_traffic'] == 0]),
        fontsize=22)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel('Longitude', fontsize=18)
    plt.ylabel('Latitude', fontsize=18)
    plt.savefig("dest_" + time)

# non-peak
time = '7am '
nonmiss_hour = nonmiss[nonmiss['time'] == time]

# origin no missing values - can sum together
dest = nonmiss_hour[['Dest', 'O-D Traffic (Calibrated Index)']].groupby('Dest').sum(). \
    reset_index(). \
    rename(columns={'O-D Traffic (Calibrated Index)': 'OD_traffic', 'Dest': 'id'})

taz_combined_miss = taz.merge(dest, on='id', how='left')
# taz_combined_miss['OD_traffic'].isna().sum()  # 29 origin zones no traffic
taz_combined = taz_combined_miss[taz_combined_miss['OD_traffic'] >= 0]

# fig, ax = plt.subplots(1, 1, figsize=(18, 12))
ax = taz_combined_miss.plot(color="grey", figsize=(18, 12))

# Using vmin and vmax forces the range for the colors
taz_combined.plot(column='OD_traffic', cmap=cmp, ax=ax, legend=True, vmin=0.0000001, vmax=3000)
plt.grid(linestyle='dotted', color='gray')
plt.title(
    "Destination " + time + ", # missing zones (in grey) = %d,\n "
    % (taz_combined_miss['OD_traffic'].isna().sum()) +
    "# zones with zero traffic (in green)= %d" % len(taz_combined[taz_combined['OD_traffic'] == 0]),
    fontsize=22)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('Longitude', fontsize=18)
plt.ylabel('Latitude', fontsize=18)
plt.savefig("dest_" + time)

# add a basemap

time = '7am '
nonmiss_hour = nonmiss[nonmiss['time'] == time]

# origin no missing values - can sum together
dest = nonmiss_hour[['Dest', 'O-D Traffic (Calibrated Index)']].groupby('Dest').sum(). \
    reset_index(). \
    rename(columns={'O-D Traffic (Calibrated Index)': 'OD_traffic', 'Dest': 'id'})

taz_combined_miss = taz.merge(dest, on='id', how='left')
# taz_combined_miss['OD_traffic'].isna().sum()  # 29 origin zones no traffic
taz_combined = taz_combined_miss[taz_combined_miss['OD_traffic'] >= 0]

df = taz_combined_miss.to_crs(epsg=2868)
# fig, ax = plt.subplots(1, 1, figsize=(18, 12))
ax = taz_combined_miss.plot(color="grey", figsize=(18, 12))
ctx.add_basemap(ax)

# Using vmin and vmax forces the range for the colors
taz_combined.plot(column='OD_traffic', cmap=cmp, ax=ax, legend=True, vmin=0.0000001, vmax=3000)
plt.grid(linestyle='dotted', color='gray')
plt.title(
    "Destination " + time + ", # missing zones (in grey) = %d,\n "
    % (taz_combined_miss['OD_traffic'].isna().sum()) +
    "# zones with zero traffic (in green)= %d" % len(taz_combined[taz_combined['OD_traffic'] == 0]),
    fontsize=22)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('Longitude', fontsize=18)
plt.ylabel('Latitude', fontsize=18)
plt.savefig("dest_" + time)