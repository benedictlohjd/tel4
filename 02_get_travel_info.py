
#%%

import time
import requests
import json
import os
import numpy as np
import pandas as pd

from datetime import timedelta
from dotenv import load_dotenv                # For loading environment variables
from ratelimit import limits, sleep_and_retry # To limit number of API calls per unit of time 
from typing import Tuple                      
from tqdm import tqdm                         # To provide progress bars

# from pyonemap import OneMap # Python wrapper for LTA's OneMap API (written by Teo Cheng Guan)

#%%

@sleep_and_retry
@limits(calls=200, period=timedelta(seconds=60).total_seconds())
def get_travel_time_and_legs(
        start_latitude: str, start_longitude: str, end_latitude: str, end_longitude: str, mode="TRANSIT", numItineraries="1"
        ) -> Tuple[int, str, str]:

    if not (start_latitude and start_longitude) or not (end_latitude and end_longitude):
        return -1, '', ''

    import requests

    try:
        url = f"https://www.onemap.gov.sg/api/public/routingsvc/route?start={start_latitude}%2C{start_longitude}&end={end_latitude}%2C{end_longitude}&routeType=pt&date=06-17-2024&time=07%3A35%3A00&mode={mode}&numItineraries={numItineraries}"
        response = requests.request("GET", url, headers=headers, timeout=10)
    
        if 'error' in response.json():
            error = response.json()['error']
            return -1, error, error
        elif 'status' in response.json():
            error = response.json()['message']
            return -1, error, error
            
        duration = response.json()['plan']['itineraries'][0]['duration']
        leg_0 = ''
        leg_1 = ''
    except requests.JSONDecodeError:
        return get_travel_time_and_legs(
            start_latitude, start_longitude, end_latitude, end_longitude
        )

    
    for leg in response.json()['plan']['itineraries'][0]['legs']:
        if leg_0 and leg_1:
            break
        if leg['mode'] != 'WALK':
            if leg['mode'] == 'BUS':
                bus = 'bus '+leg['route']
                _from = leg['from']['name']
                _to   = leg['to']['name']
                _leg = bus+' from '+_from + ' to ' + _to
            elif leg['mode'] == 'SUBWAY':
                mrt = 'mrt ' + leg['route']
                _from = leg['from']['name']
                _to   = leg['to']['name']
                if leg['intermediateStops']:
                    _via = leg['intermediateStops'][0]['name']
                    _leg = mrt+' from '+_from + ' to ' + _to + ' via ' + _via
                else:
                    _leg = mrt+' from '+_from + ' to ' + _to
            if not leg_0:
                leg_0 = _leg
            else:
                leg_1 = _leg
        else:
            continue

    return duration, leg_0, leg_1


#%%

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)

#%%

# Read in lat and long data
df_lat_long = pd.read_csv(
    "C:/Users/bened/OneDrive/Desktop/NUS-econ-predoc/03-TEL-LG-TW-PL/01_Data/Output/loc_lat_long_V1_and_V2_17Jun2024_0.csv",
    dtype='str'
    )

# Fill NAs with ''
df_lat_long.fillna('', inplace=True)

#%%

# Loading onemap api token
load_dotenv("C:\\Users\\bened\\telproject\\.env")

url = "https://www.onemap.gov.sg/api/auth/post/getToken"
      
payload = {
    "email": os.getenv('ONEMAP_EMAIL'),
    "password": os.getenv('ONEMAP_EMAIL_PASSWORD')
    }
      
response = requests.request("POST", url, json=payload)
token = response.json()['access_token']
headers = {
    'Authorization': token
}

#%%

# Create new columns to store duration and legs to travel from Postal to locations
for loc in ['WS1', 'WS2', 'WS3', 'F1', 'F2', 'F3']:
    duration = f"Postal_to_{loc}_duration"
    leg_0    = f"Postal_to_{loc}_leg_0"
    leg_1    = f"Postal_to_{loc}_leg_1"

    df_lat_long[duration] = pd.Series(-1, index=df_lat_long.index)
    df_lat_long[leg_0] = pd.Series('', index=df_lat_long.index)
    df_lat_long[leg_1] = pd.Series('', index=df_lat_long.index)

#%%

for i in tqdm(range(len(df_lat_long))):
    for loc in ['WS1', 'WS2', 'WS3', 'F1', 'F2', 'F3']:
        duration_col = f"Postal_to_{loc}_duration"
        leg_0_col    = f"Postal_to_{loc}_leg_0"
        leg_1_col    = f"Postal_to_{loc}_leg_1"

        end_loc_lat = loc+"_"+"Postal"+"_"+"lat"
        end_loc_long = loc+"_"+"Postal"+"_"+"long"

        start_lat = df_lat_long.loc[i, 'Postal_lat']
        start_long = df_lat_long.loc[i, 'Postal_long']
        end_lat = df_lat_long.loc[i, end_loc_lat]
        end_long = df_lat_long.loc[i, end_loc_long]

        if not (end_lat and end_long):
            duration, leg_0, leg_1 = -1, '', ''
        else:
            duration, leg_0, leg_1 = get_travel_time_and_legs(
                start_lat, start_long, end_lat, end_long
            )

        df_lat_long.loc[i, duration_col] = duration
        df_lat_long.loc[i, leg_0_col] = leg_0
        df_lat_long.loc[i, leg_1_col] = leg_1

#%%

df_lat_long.to_csv("travel_times_2.csv")

#%%