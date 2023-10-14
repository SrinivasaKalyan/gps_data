import pandas as pd
import folium


gpsdata = pd.read_excel("C:\\Users\\srini\\Downloads\\gpsdata.xlsx")
data = pd.DataFrame(gpsdata)
data['Time'] = pd.to_datetime(data['Time'])
data['Attributes'] = data['Attributes'].str.split(' ')
split_data = []
for row in data['Attributes']:
    split_dict = {}
    for item in row:
        key_value = item.split('=')
        if len(key_value) == 2:
            key, value = key_value
            split_dict[key] = value
    split_data.append(split_dict)
split_data_df = pd.DataFrame(split_data)
data = pd.concat([data, split_data_df], axis=1)
data.drop(columns=['Attributes'], inplace=True)
data['totalDistance'] = data['totalDistance'].astype(float)
data['Speed'] = data['Speed'].str.split(' ', n=1, expand=True)[0]
data['Speed'].fillna(0, inplace=True)
data['Speed'] = data['Speed'].astype(float)
df = data[data['Time'].dt.strftime('%Y-%m-%d') == '2023-09-16']

df_copy = df.copy()
df_copy.drop(columns={'Altitude', 'priority', 'sat', 'event', 'rssi', 'io200', 'io69', 'pdop', 'hdop', 'power',
                    'battery', 'io68', 'odometer','totalDistance','distance','motion','hours'}, inplace=True)
df_copy['ignition'] = df_copy['ignition'].map({'true': True, 'false': False})
df_copy.loc[:, 'time'] = df_copy['Time'].diff()

df_stops_start = df_copy[((df_copy['ignition'] == True) & (df_copy['Speed'] == 0) & (df_copy['time'] > '0 days 00:05:00'))]
df_stops_stop = df_copy[((df_copy['ignition'] == False) & (df_copy['Speed'] == 0) & (df_copy['time'] > '0 days 00:05:00'))]
intervals = []
start_idx = None
in_interval = False
total_hours = 0
for idx, row in df_copy.iterrows():
    if row['Speed'] == 0 and row['ignition'] == True:
        if not in_interval:
            start_idx = idx
            in_interval = True
    elif in_interval and row['Speed'] == 0 and row['ignition'] == False:
        intervals.append(df_copy.loc[start_idx:idx])
        in_interval = False
        total_hours += df_copy.loc[start_idx:idx]['time'].sum().total_seconds() / 3600

df_first = pd.DataFrame(intervals[0])
df_last = pd.DataFrame(intervals[-1])
lat_first = df_first.iloc[0, 2]
log_first = df_first.iloc[0, 3]



ignition_map = folium.Map(location=[lat_first,log_first], zoom_start=13)        
for idx,row in df_stops_start.iterrows():
    lat = row['Latitude']
    log = row['Longitude']
    popupcontent = f"<strong> time stayed:{row['time']}</strong>"
    folium.Marker(location=[lat,log],icon=folium.Icon(color='orange'),popup=popupcontent).add_to(ignition_map)
for idx,row in df_stops_stop.iterrows():
    lat = row['Latitude']
    log = row['Longitude']
    popupcontent = f"<strong> time stayed:{row['time']}</strong>"
    folium.Marker(location=[lat,log],icon=folium.Icon(color='blue'),popup=popupcontent).add_to(ignition_map)
    
ignition_map