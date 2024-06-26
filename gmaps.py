
#%%

import googlemaps
import pandas as pd

from datetime import datetime
from tqdm import tqdm

#%%

API_KEY = ""

gmaps = googlemaps.Client(API_KEY)

#%%

HDB_data = pd.read_csv("C:/Users/bened/Downloads/Telegram Desktop/HDB_map.csv")
TEL_data = pd.read_csv("C:/Users/bened/Downloads/Telegram Desktop/TEL4 routes- TEL4 MRT line and exit.csv")

HDB_and_TEL = HDB_data.merge(
    TEL_data,
    how="left",
    left_on="mrt_station_exit",
    right_on="address"
)

HDB_and_TEL.rename(columns={
    "Lat": "tel_station_lat",
    "Long": "tel_station_long"
}, inplace=True)

HDB_and_TEL.drop(columns="address", inplace=True)

#%%

HDB_and_TEL['time_walk(sec)_gmaps'] = pd.Series(-1, index=HDB_and_TEL.index)
HDB_and_TEL['dis_walk(m)_gmaps'] = pd.Series(-1, index=HDB_and_TEL.index)

#%%

now = datetime.now()

for i in tqdm(range(len(HDB_and_TEL))):
    origin = (HDB_and_TEL.loc[i, "LATITUDE"], HDB_and_TEL.loc[i, "LONGITUDE"])
    dest = (HDB_and_TEL.loc[i, "tel_station_lat"], HDB_and_TEL.loc[i, "tel_station_long"])

    directions = gmaps.directions(origin, dest, mode="walking", departure_time=now)

    HDB_and_TEL.loc[i, 'time_walk(sec)_gmaps'] = directions[0]['legs'][0]['duration']['value']
    HDB_and_TEL.loc[i, 'dis_walk(m)_gmaps'] = directions[0]['legs'][0]['distance']['value']

#%%

HDB_and_TEL['diff_time_walk(sec)'] = HDB_and_TEL['time_walk(sec)'].sub(HDB_and_TEL['time_walk(sec)_gmaps'])
HDB_and_TEL['diff_dis_walk(m)'] = HDB_and_TEL['dis_walk(m)'].sub(HDB_and_TEL['dis_walk(m)_gmaps'])

#%%

HDB_and_TEL.to_csv("HDB_to_tel_exits_onemap_v_gmaps.csv")

#%%