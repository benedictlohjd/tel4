
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

pd.set_option('display.max_columns', 100)

#%% 

@sleep_and_retry
@limits(calls=200, period=timedelta(seconds=60).total_seconds())
def get_lat_long(postal_code: str, silent=True) -> Tuple[str, str]:
    """
    Returns latitude coordinate and longitude coordinate from Singapore postal code. If invalid postal code, returns a tuple of empty strings.
    
    Args:
        postal_code (str): Six-character postal code

    Returns:
        Tuple: latitude, longitude
    """

    if not postal_code:
        return '', ''

    import requests
    import json
    
    url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal=" + postal_code + "&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    response = requests.request("GET", url)
    response_body = json.loads(response.content)
    try:
        lat, long = response_body['results'][0]['LATITUDE'], response_body['results'][0]['LONGITUDE']
        if not silent:
            print(f'{postal_code} corresponds to latitude {latitude} and longitude {longitude}')
        return lat, long
    except IndexError:
        # IndexError likely due to invalid postal code
        if not response_body['results']:
            print(f"OneMap API returns '' for postal code {postal_code}")
        return '', ''

#%%

@sleep_and_retry
@limits(calls=200, period=timedelta(seconds=60).total_seconds())
def get_pln_area_name(latitude: str, longitude: str, year='2024') -> str:

    if not (latitude and longitude):
        return ''

    import requests
    
    url = f"https://www.onemap.gov.sg/api/public/popapi/getPlanningarea?latitude={latitude}&longitude={longitude}&year={year}"
    response = requests.request("GET", url, headers=headers)
    response_body = json.loads(response.content)
    planning_area_name = response_body[0]['pln_area_n']
    return planning_area_name
    
    
#%%

# Read in data (the data to be read in is created using 00_TEL4DataMerger.R)
df_postcode=pd.read_csv(
    "C:/Users/bened/OneDrive/Desktop/NUS-econ-predoc/03-TEL-LG-TW-PL/01_Data/Output/v1_and_v2_17Jun2024_0.csv",
    dtype=str,
    na_values='NA'
    )
df_postcode=df_postcode[['Name', 'Mobile', 'Postal', 'WS1_Postal', 'WS2_Postal', 'WS3_Postal', 'F1_Postal', 'F2_Postal', 'F3_Postal']]

#%%

# Loading onemap api token
load_dotenv(os.getcwd())

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

# # Finding lat and long of one postcode using pyonemap
# loc = onemap.search(
#     df_postcode['WS1_Postal'][0], 'Y', 'Y'
# )

# print(
#     loc['results'][0]['LATITUDE'], loc['results'][0]['LONGITUDE']
# )

# Check that all postal codes are six characters 
for postal_code in df_postcode:
    if postal_code=='Name' or postal_code=='Mobile':
        continue
    assert np.nanmin(df_postcode[postal_code].str.len())==6, f"Min length of {postal_code} is not 6"
    assert np.nanmax(df_postcode[postal_code].str.len())==6, f"Max length of {postal_code} is not 6"

# Replace NAs with empty strings
df_postcode.fillna('', inplace=True)

#%%

# Create new columns to store lat and long of each location
for postal_code in df_postcode:
    lat_name = postal_code+"_"+"lat"
    long_name = postal_code+"_"+"long"
    df_postcode[lat_name] = pd.Series('', index=df_postcode.index)
    df_postcode[long_name] = pd.Series('', index=df_postcode.index)

df_postcode['WS1_Postal_pln_area'] = pd.Series('', index=df_postcode.index)       

#%%

postal_codes = ['Postal', 'WS1_Postal', 'WS2_Postal', 'WS3_Postal', 'F1_Postal', 'F2_Postal', 'F3_Postal']

for i in tqdm(range(len(df_postcode))):
    for code in postal_codes:
        postal_code = df_postcode[code][i]
        if not postal_code:
            latitude, longitude = '', ''
        else:
            latitude, longitude = get_lat_long(postal_code)

        lat_name = code+"_"+"lat"
        long_name = code+"_"+"long"

        df_postcode.loc[i, lat_name] = latitude
        df_postcode.loc[i, long_name] = longitude

# Get URA planning area name for WS1
for i in tqdm(range(len(df_postcode))):
    lat, long = df_postcode['WS1_Postal_lat'][i], df_postcode['WS1_Postal_long'][i]
    pln_area_name = get_pln_area_name(lat, long)

    df_postcode.loc[i, 'WS1_Postal_pln_area'] = pln_area_name

#%%

df_postcode.to_csv('loc_lat_long_V1_and_V2_17Jun2024_0.csv', index=False)

#%%