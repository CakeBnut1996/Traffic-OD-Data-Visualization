import pandas as pd
import numpy as np
from collections import Counter
import math
import random
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from shapely.geometry import Point, LineString, shape
from geopandas import GeoDataFrame
import geoplot as gplt
import geoplot.crs as gcrs


# read STL data
school = pd.read_csv("Demand/Pima_OD_UA_team_School_2267_Travel/Pima_OD_UA_team_2267_od_all.csv")
summer = pd.read_csv("Demand/Pima_OD_UA_team_Summer_7548_Travel/Pima_OD_UA_team_7548_od_all.csv")
snow = pd.read_csv("Demand/Pima_OD_UA_team_Snowbirds_6202_Travel/Pima_OD_UA_team_6202_od_all.csv")

len(set(school['Origin Zone ID']))  # 1088
len(set(school['Destination Zone ID']))  # 1081

len(set(summer['Origin Zone ID']))  # 1083
len(set(summer['Destination Zone ID']))  # 1084

len(set(snow['Origin Zone ID']))  # 1087
len(set(snow['Destination Zone ID']))  # 1091

taz = gpd.read_file("D:/A - Project/TucsonModel/Pima-County---Regional_2017_TAZ_ZoneSet/zone_set_2017_TAZ.shp")
# ------------------ pre-processing ---------------------
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

# total missing rate
(1-len(demand_dt)/(1104*1104*24))*100 # 95.68399099344501

# ------------------ departure time distribution ---------------------
time_OD_count = demand_dt.groupby('time')['O-D Traffic (Calibrated Index)'].sum()
time_OD_count = time_OD_count.reindex(['12am', '1am ', '2am ', '3am ', '4am ', '5am ', '6am ', '7am ', '8am ',
                                       '9am ', '10am', '11am', '12pm', '1pm ', '2pm ', '3pm ', '4pm ',
                                       '5pm ', '6pm ', '7pm ', '8pm ', '9pm ', '10pm', '11pm'])
time_OD_count = time_OD_count*100/demand_dt['O-D Traffic (Calibrated Index)'].sum()
plt.figure(figsize=(18, 12))
time_OD_count.plot(kind='bar', width=0.8)
plt.title("Snowbirds Season Departure Time Distribution", fontsize=22)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('Hour', fontsize=18)
plt.ylabel('% of total OD pairs', fontsize=18)

# ------------------ complement missing OD's  ---------------------
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

# ------------------ missing rate ---------------------
# missing rate by hour
missing = od_complete[pd.isnull(od_complete['O-D Traffic (Calibrated Index)'])]
len(missing)

time_OD_count = missing[['time', 'O-D Traffic (Calibrated Index)']].fillna(-1).groupby('time').count()/(1104*1104)
time_OD_count = time_OD_count.reindex(['12am', '1am ', '2am ', '3am ', '4am ', '5am ', '6am ', '7am ', '8am ',
                                       '9am ', '10am', '11am', '12pm', '1pm ', '2pm ', '3pm ', '4pm ',
                                       '5pm ', '6pm ', '7pm ', '8pm ', '9pm ', '10pm', '11pm'])

plt.figure(figsize=(12, 8))
# time_OD_count.plot(kind='bar', width=0.8)
y_pos = np.arange(len(time_OD_count['O-D Traffic (Calibrated Index)'].index))
performance = time_OD_count['O-D Traffic (Calibrated Index)']
plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.title("Average percent of missing OD pairs by hour", fontsize=22)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('Hour', fontsize=18)
plt.ylabel('# of missing pairs/theoretical # pairs in an hour', fontsize=18)

# ------------------ major OD pair missing rate - --------------------
pairs = demand_dt[['Orig',
                   'Dest',
                   'O-D Traffic (Calibrated Index)']].groupby(['Orig','Dest']).mean().reset_index()
pairs = pairs.sort_values(by=['O-D Traffic (Calibrated Index)'], ascending=False)
imp_pairs = pairs[pairs['O-D Traffic (Calibrated Index)'] >= 5] # traffic greater than 50 vehicles
len(imp_pairs) # 1905
len(imp_pairs)/(1104*1104) # 0.007653329132535182

imp_demand = demand_dt.merge(imp_pairs[['Orig','Dest']], on=['Orig', 'Dest'], how='inner')
npairs = imp_demand[['Orig',
                     'Dest',
                     'O-D Traffic (Calibrated Index)']].groupby(['Orig','Dest']).count().reset_index()
npairs['missing'] = 1 - npairs['O-D Traffic (Calibrated Index)']/24
np.mean(npairs['missing']) # 0.546450650371641
# daytime
imp_demand_day = imp_demand[imp_demand['time'].isin(['8am ', '9am ', '10am', '11am', '12pm',
                                                 '1pm ', '2pm ', '3pm ', '4pm ', '5pm '])]
npairs_day = imp_demand_day[['Orig','Dest',
                         'O-D Traffic (Calibrated Index)']].groupby(['Orig','Dest']).count().reset_index()
npairs_day['missing'] = 1 - npairs_day['O-D Traffic (Calibrated Index)']/10
np.mean(npairs_day['missing']) # 0.31049716957912876

# comparison
plt.figure(figsize=(12, 8))
plt.hist(npairs['missing'], bins=10, edgecolor='black', color='green', label='24 hours', alpha=0.5)
plt.hist(npairs_day['missing'], bins=10, edgecolor='black', color='tomato', label='Daytime: 8AM-5PM', alpha=0.7)
plt.title("Important Pairs Missing Rate Distribution", fontsize=22)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('Missing Rate', fontsize=18)
plt.ylabel('# of OD pairs', fontsize=18)
plt.legend(loc='upper right', fontsize=16)

# higher missing rate spatial viz
severe_miss = npairs_day[npairs_day['missing'] >= 0.6]
centroid = taz.centroid
centroid_xy = pd.DataFrame({'Orig': centroid.index+1, 'Orig_x': centroid.x, 'Orig_y': centroid.y})
severe_miss = severe_miss.merge(centroid_xy, on='Orig')
centroid_xy = pd.DataFrame({'Dest': centroid.index+1, 'Dest_x': centroid.x, 'Dest_y': centroid.y})
severe_miss = severe_miss.merge(centroid_xy, on='Dest')
gdf = gpd.GeoDataFrame(severe_miss,
                       geometry=[Point(x1, y1) for x1, y1, in zip(severe_miss.Orig_x, severe_miss.Orig_y)])
gdf = gdf.rename({'geometry': 'Point1'}, axis=1)
gdf = gpd.GeoDataFrame(gdf,
                       geometry=[Point(x2, y2) for x2, y2, in zip(severe_miss.Dest_x, severe_miss.Dest_y)])
gdf = gdf.rename({'geometry': 'Point2'}, axis=1)
gdf['geometry'] = gdf.apply(lambda x: LineString([x['Point1'], x['Point2']]), axis=1)

g_part = gdf.sample(n=int(np.ceil(0.009*len(gdf))))
len(g_part)
# 32.206095, -111.047813
ax = gplt.webmap(taz, figsize=(18, 12), projection=gcrs.WebMercator())
gplt.sankey(
    g_part, limits=(2, 5),
    scale='missing', ax=ax,
    legend=True
)

# ------------------ major OD pair by hour - --------------------
pairs = demand_dt[['Orig', 'Dest', 'time',
                   'O-D Traffic (Calibrated Index)']].groupby(['Orig','Dest','time']).mean().reset_index()
pairs = pairs[pairs['time'].isin(['5pm '])]
pairs = pairs.sort_values(by=['O-D Traffic (Calibrated Index)'], ascending=False)

pairs.loc[(pairs['Orig'] == 380) & (pairs['Dest'] == 487)]