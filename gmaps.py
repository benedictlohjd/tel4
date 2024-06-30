
#%%

import googlemaps
import numpy as np
import pandas as pd

from collections import defaultdict
from datetime import datetime, timedelta
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

for i in tqdm(range(2)):
    origin = (HDB_and_TEL.loc[i, "LATITUDE"], HDB_and_TEL.loc[i, "LONGITUDE"])
    dest = (HDB_and_TEL.loc[i, "tel_station_lat"], HDB_and_TEL.loc[i, "tel_station_long"])

    directions = gmaps.directions(origin, dest, mode="walking", departure_time=now)

    HDB_and_TEL.loc[i, 'time_walk(sec)_gmaps'] = directions[0]['legs'][0]['duration']['value']
    HDB_and_TEL.loc[i, 'dis_walk(m)_gmaps'] = directions[0]['legs'][0]['distance']['value']

#%%

# Marine terrace MRT coordinates from gmaps: 1.3068678716918973, 103.91486286905939
# Marine parade MRT coordinates from gmaps: 1.3036778416964114, 103.90612036721541

HDB_and_TEL['tel_station_lat_1'] = np.select(
    [
        HDB_and_TEL['mrt_station_exit'].str.contains('Marine Terrace'),
        HDB_and_TEL['mrt_station_exit'].str.contains('Marine Parade')
    ],
    [
        1.3068678716918973,
        1.3036778416964114
    ],
    default=-1
)

HDB_and_TEL['tel_station_long_1'] = np.select(
    [
        HDB_and_TEL['mrt_station_exit'].str.contains('Marine Terrace'),
        HDB_and_TEL['mrt_station_exit'].str.contains('Marine Parade')
    ],
    [
        103.91486286905939,
        103.90612036721541
    ],
    default=-1
)

HDB_and_TEL['time_walk(sec)_gmaps_opt'] = pd.Series(-1, index=HDB_and_TEL.index)
HDB_and_TEL['dis_walk(m)_gmaps_opt'] = pd.Series(-1, index=HDB_and_TEL.index)

#%%

now = datetime.now()

# Pull data of walk duration and distance based on google maps suggested routes
for i in tqdm(range(len(HDB_and_TEL))):
    origin = (HDB_and_TEL.loc[i, "LATITUDE"], HDB_and_TEL.loc[i, "LONGITUDE"])
    dest = (HDB_and_TEL.loc[i, "tel_station_lat_1"], HDB_and_TEL.loc[i, "tel_station_long_1"])

    directions = gmaps.directions(origin, dest, mode="walking", departure_time=now)

    HDB_and_TEL.loc[i, 'time_walk(sec)_gmaps_opt'] = directions[0]['legs'][0]['duration']['value']
    HDB_and_TEL.loc[i, 'dis_walk(m)_gmaps_opt'] = directions[0]['legs'][0]['distance']['value']

#%%

# Compute difference between onemap walking data and gmaps walking data based on onemap suggested routes for start and end points
HDB_and_TEL['diff_time_walk(sec)'] = HDB_and_TEL['time_walk(sec)'].sub(HDB_and_TEL['time_walk(sec)_gmaps'])
HDB_and_TEL['diff_dis_walk(m)'] = HDB_and_TEL['dis_walk(m)'].sub(HDB_and_TEL['dis_walk(m)_gmaps'])

#%%
# Compute difference between onemap routes and gmaps routes
HDB_and_TEL['diff_time_walk(sec)_gmaps_opt'] = HDB_and_TEL['time_walk(sec)'].sub(HDB_and_TEL['time_walk(sec)_gmaps_opt'])
HDB_and_TEL['diff_dis_walk(m)_gmaps_opt'] = HDB_and_TEL['dis_walk(m)'].sub(HDB_and_TEL['dis_walk(m)_gmaps_opt'])

#%%

HDB_and_TEL.to_csv("HDB_to_tel_exits_onemap_v_gmaps_1.csv")

#%%

# ============================================================================================= #
# Get non TEL4 routes to interchanges and workplaces 
# ============================================================================================= #

# Get lat and long of TEL stations

INT_lat_lng = defaultdict(lambda: tuple())

INT = [
    "Stevens Mrt Station (DT10)",
    "Orchard Mrt Station (NS22)",
    "Outram Park Mrt Station (NE3)",
    "Marina Bay Mrt Station (CE2)",
]

for i in INT:
    loc = gmaps.geocode(i)
    lat_lng = loc[0]['geometry']['location']
    INT_lat_lng[i] = (lat_lng['lat'], lat_lng['lng'])

#%%

# Read in data of lat lng of participants' postal codes

postcode_lat_lng = pd.read_csv("c:\\Users\\bened\\tel4\\loc_lat_long_V1_and_V2_29Jun2024_0.csv")

# create extra columns to store data

non_tel4_routes = postcode_lat_lng.copy()
for i in ["stevens", 'orchard', 'outram', 'marina_bay']:
    non_tel4_travel_time = f"home_postal_to_{i}_time"
    non_tel4_travel_leg_0_travel_mode = f"home_postal_to_{i}_leg_0_travel_mode"
    non_tel4_travel_leg_1_travel_mode = f"home_postal_to_{i}_leg_1_travel_mode"
    non_tel4_travel_leg_0_start = f"home_postal_to_{i}_leg_0_start"
    non_tel4_travel_leg_0_end = f"home_postal_to_{i}_leg_0_end"
    non_tel4_travel_leg_1_start = f"home_postal_to_{i}_leg_1_start"
    non_tel4_travel_leg_1_end = f"home_postal_to_{i}_leg_1_end"

    non_tel4_routes[non_tel4_travel_time] = pd.Series(-1, index=non_tel4_routes.index)
    non_tel4_routes[non_tel4_travel_leg_0_travel_mode] = pd.Series('', index=non_tel4_routes.index)
    non_tel4_routes[non_tel4_travel_leg_0_start] = pd.Series('', index=non_tel4_routes.index)
    non_tel4_routes[non_tel4_travel_leg_0_end] = pd.Series('', index=non_tel4_routes.index)

    non_tel4_routes[non_tel4_travel_leg_1_travel_mode] = pd.Series('', index=non_tel4_routes.index)
    non_tel4_routes[non_tel4_travel_leg_1_start] = pd.Series('', index=non_tel4_routes.index)
    non_tel4_routes[non_tel4_travel_leg_1_end] = pd.Series('', index=non_tel4_routes.index)    

#%%

tel4_stations = [
    'Tanjong Rhu', 'Katong Park', 'Tanjong Katong', 'Marine Parade', 'Marine Terrace', 'Siglap', 'Bayshore'
]

depart_time = datetime.now() + timedelta(hours=16)

for i in tqdm(range(len(non_tel4_routes))):

    if non_tel4_routes.loc[i, 'Postal_lat'] and non_tel4_routes.loc[i, 'Postal_long']:
        origin = (non_tel4_routes.loc[i, 'Postal_lat'], non_tel4_routes.loc[i, 'Postal_long'])

        for interchange in INT_lat_lng:
            dest = INT_lat_lng[interchange]

            if "Stevens" in interchange:
                station_name = 'stevens'
            elif "Orchard" in interchange:
                station_name = 'orchard'
            elif "Outram" in interchange:
                station_name = 'outram'
            elif "Marina" in interchange:
                station_name = 'marina_bay'
            
            directions = gmaps.directions(
                origin, dest,
                mode="transit",
                departure_time=depart_time,
                alternatives=True
            )

            if len(directions)==1:
                only_tel4 = False
                for route in directions:
                    for leg in route['legs']:
                        for step in leg['steps']:
                            if step['travel_mode'] == 'TRANSIT':
                                transit_details = step['transit_details']
                                vehicle_type = transit_details['line']['vehicle']['type']
                                if vehicle_type == 'BUS':
                                    continue
                                elif vehicle_type == 'SUBWAY':
                                    if transit_details['departure_stop']['name'] in tel4_stations:
                                        only_tel4 = True
                                        break
                        if only_tel4:
                            break
                
                if only_tel4:
                    directions = gmaps.directions(
                        origin, dest,
                        mode="transit",
                        transit_mode="bus",
                        departure_time=depart_time,
                        alternatives=True
                        )

            leg_0_start, leg_0_end, leg_1_start, leg_1_end = '', '', '', ''
            leg_0_travel_mode, leg_1_travel_mode = '', ''

            for route in directions:
                tel4 = False
                route_duration = route['legs'][0]['duration']['value']
                for leg in route['legs']:
                    for idx, step in enumerate(leg['steps']):
                        if leg_0_travel_mode and not leg_1_travel_mode and step['travel_mode'] == 'WALKING':
                            try:
                                if leg['steps'][idx+1]['travel_mode'] != 'WALKING':
                                    continue
                            except IndexError:
                                leg_1_travel_mode = step['html_instructions']
                        elif step['travel_mode'] == 'TRANSIT':
                            transit_details = step['transit_details']
                            vehicle_type = transit_details['line']['vehicle']['type']
                            if transit_details['departure_stop']['name'] in tel4_stations:
                                tel4 = True
                                break
                            else:
                                if vehicle_type in ['BUS', 'SUBWAY']:
                                    if not leg_0_travel_mode:
                                        leg_0_travel_mode = f"{vehicle_type} {transit_details['line']['name']}"
                                        leg_0_start = transit_details['departure_stop']['name']
                                        leg_0_end = transit_details['arrival_stop']['name']
                                    elif not leg_1_travel_mode:
                                        leg_1_travel_mode = f"{vehicle_type} {transit_details['line']['name']}"
                                        leg_1_start = transit_details['departure_stop']['name']
                                        leg_1_end = transit_details['arrival_stop']['name']
                                    else:
                                        break
                                    
                    if tel4:
                        leg_0_start, leg_0_end, leg_1_start, leg_1_end = '', '', '', ''
                        leg_0_travel_mode, leg_1_travel_mode = '', ''
                        route_duration = -1
                        break
                
                if leg_0_travel_mode and leg_0_start and leg_0_end:
                    break
            
            non_tel4_travel_time = f"home_postal_to_{station_name}_time"
            non_tel4_travel_leg_0_travel_mode = f"home_postal_to_{station_name}_leg_0_travel_mode"
            non_tel4_travel_leg_1_travel_mode = f"home_postal_to_{station_name}_leg_1_travel_mode"
            non_tel4_travel_leg_0_start = f"home_postal_to_{station_name}_leg_0_start"
            non_tel4_travel_leg_0_end = f"home_postal_to_{station_name}_leg_0_end"
            non_tel4_travel_leg_1_start = f"home_postal_to_{station_name}_leg_1_start"
            non_tel4_travel_leg_1_end = f"home_postal_to_{station_name}_leg_1_end"
            
            non_tel4_routes.loc[i, non_tel4_travel_leg_0_travel_mode] = leg_0_travel_mode
            non_tel4_routes.loc[i, non_tel4_travel_leg_1_travel_mode] = leg_1_travel_mode

            non_tel4_routes.loc[i, non_tel4_travel_time] = route_duration
            non_tel4_routes.loc[i, non_tel4_travel_leg_0_start] = leg_0_start
            non_tel4_routes.loc[i, non_tel4_travel_leg_0_end] = leg_0_end
            non_tel4_routes.loc[i, non_tel4_travel_leg_1_start] = leg_1_start
            non_tel4_routes.loc[i, non_tel4_travel_leg_1_end] = leg_1_end

    if i==0:
        break            

#%%

