import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import folium as fp
from streamlit_folium import folium_static
from shapely.geometry import Point
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2
from folium.plugins import Fullscreen, MiniMap
import requests
from streamlit_lottie import st_lottie
import json

def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
lottie_animation = load_lottie_file("bus.json")

def main():
    st.set_page_config(layout="wide")
    # st.title("Geo-Spatial-Insights")
    st.image("Geo_Spatial_Insights.png",use_column_width=True)
    EDA_tasks = ["1.distinguish attributes","2.Data Cleaning", "3.Speed","4.Maps","5.Entry & Exit points","About Creator🧐"]
    choice = st.sidebar.radio("select tasks:", EDA_tasks)
    data = pd.read_excel("report (5).xlsx",skiprows=7)


        
    df = pd.DataFrame(data)
    
    df.rename(columns={'Unnamed: 0': 'Valid', 'Unnamed: 1': 'Time', 'Unnamed: 2': 'Lat', 'Unnamed: 3': 'Long',
                            'Unnamed: 5': 'Speed', 'Unnamed: 4': 'Altitude', 'Unnamed: 7': 'attributes'}, inplace=True)
    st.dataframe(df.head())


    if choice == '1.distinguish attributes':
        st.subheader(" Distinguishing attributes  :1234:")
        da_tasks = ("Show Shape","Show Columns","Summary","Show Selected Columns","show numerical variables","show categorical variables","percentage distribution of unique values in fields")
        da_options = st.sidebar.selectbox("Distinguishing attributes in EDA", da_tasks)
        if da_options == "Show Shape":
            st.subheader("Show Shape")
            if data is not None:
                st.write("rows and columns formate ", df.shape)

        if da_options == "Show Columns":
            st.subheader("Show Columns")
            all_columns = df.columns.to_list()
            st.write(all_columns)

        if da_options == "Summary":
            st.subheader("Summary")
            st.write(df.describe())

        if da_options == "Show Selected Columns":
            st.subheader("Show Selected Columns")
            all_columns = df.columns.to_list()
            selected_columns = st.multiselect("Select Columns", all_columns)
            new_df = df[selected_columns]
            st.dataframe(new_df)

        if da_options == "show numerical variables":
            st.subheader("Show numerical variables")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            newdf = df.select_dtypes(include=numerics)
            st.dataframe(newdf)

        if da_options == "show categorical variables":
            st.subheader("Show categorical variables")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            newdf = df.select_dtypes(include=numerics)
            df1 = df.drop(newdf, axis=1)
            st.dataframe(df1)

        if da_options == "percentage distribution of unique values in fields":
            st.subheader("percentage distribution of unique values in fields")
            all_columns = df.columns.to_list()
            sel_cols = st.multiselect("Select Columns", all_columns)
            cd = df[sel_cols].value_counts(normalize=True) * 100
            st.dataframe(cd)

    elif choice == '2.Data Cleaning':
        st.subheader(" Data cleaning 🛠️")
        options = st.sidebar.selectbox("Select an option", ["Show the NA values", "Remove duplicate values"])        
        rdf = df[df['Latitude'] != 0]
     
        if options == "Show the NA values":
            st.subheader("Show the NA values")
            nas = df.isnull().sum()
            st.dataframe(nas)

        if options == "Remove duplicate values":
            st.subheader("Remove duplicate values")
            st.dataframe(rdf)
            st.download_button(label='Download CSV', data=rdf.to_csv(), mime='text/csv')

    elif choice == "3.Speed":
            rdf = df[df['Latitude'] != 0]
            rdf[['date', 'time']] = rdf['Time'].str.split(' ', expand=True)
            unique_dates = rdf['date'].unique()
            l = []
            date_dataframes = {}  
            for date in unique_dates:
                z = date[:10].replace('-', "_")
                l.append(z)
                date_dataframes[z] = rdf[rdf['date'] == date].copy()  
            selected_dates = st.multiselect("Select Dates", l)
            if selected_dates: 
                st.write("Selected Dataframe:")
                selected_date = selected_dates[-1] 
                rdf = date_dataframes[selected_date]
            rdf['int_speed'] = rdf.apply(lambda row: float(row['Speed'][:-4]), axis=1)
            st.subheader(" Average Speed")
            st.write(rdf.int_speed.mean())
            min_speed = rdf[(rdf['int_speed'] > 0) & (rdf['int_speed'] < rdf['int_speed'].max())]['int_speed'].min()
            st.subheader(" Min Speed")
            st.write(min_speed)

            st.subheader(" Max Speed")
            st.write(rdf.int_speed.max())
            st.subheader(" Total Distance")
            x = rdf 
            x['Prev_Latitude'] = x['Latitude'].shift()
            x['Prev_Longitude'] = x['Longitude'].shift()
            x = x.dropna()
            x['Distance'] = x.apply(lambda row: geodesic((row['Prev_Latitude'], row['Prev_Longitude']),
                                                        (row['Latitude'], row['Longitude'])).kilometers, axis=1)
            total_distance = x['Distance'].sum()
            st.write(total_distance)
            st.subheader(" OverSpeed Coordinates")
            fdf = rdf[rdf['int_speed'] > 50]
            st.dataframe(fdf.Address)

    elif choice == "4.Maps":
        st.subheader("Maps")
        options = st.sidebar.selectbox("Select an option", ["overspeed map", "Total coordinates map", "Day wise maps", "compare maps", "Bus standby", "Geo Fence"])
        rdf = df[df['Latitude'] != 0]
        rdf[['date', 'time']] = rdf['Time'].str.split(' ', expand=True)
        unique_dates = rdf['date'].unique()

        rdf['int_speed'] = rdf.apply(lambda row: float(row['Speed'][:-4]), axis=1)

        if options == "overspeed map":
            overspeed = st.number_input("Overspeed :")
            fdf = rdf[rdf['int_speed'] > overspeed]
            unique_dates = rdf['date'].unique()
            l = []
            date_dataframes = {}
            for date in unique_dates:
                z = date[:10].replace('-', "_")
                l.append(z)
                date_dataframes[z] = rdf[rdf['date'] == date].copy()
            selected_dates = st.multiselect("Select Dates", l)

            if selected_dates:
                st.write("Selected Dataframe:")
                selected_date = selected_dates[-1]
                daydf = date_dataframes[selected_date]
                zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                d = fp.Popup(selected_date, parse_html=True)
                fm = fp.Map(location=[16.9891, 82.2475], zoom_start=12)
                for index, row in fdf.iterrows():
                    fp.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=5,
                        color='red',
                        fill=True,
                        fill_color='red',
                        fill_opacity=1.0,
                        popup=f"speed: {row['int_speed']}",
                    ).add_to(fm)
                fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20, no_wrap=True).add_to(fm)
                fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20,no_wrap=True).add_to(fm)
                Fullscreen().add_to(fm)
                folium_static(fm)

        if options == "Total coordinates map":
            coordinates = list(zip(rdf['Latitude'], rdf['Longitude']))
            n = fp.Map(location=[16.9891, 82.2475], zoom_start=10)
            for coord in coordinates:
                fp.CircleMarker(
                    location=coord,
                    radius=5,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.7,
                ).add_to(n)
            # Adding tile layers and full-screen functionality
            fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20, no_wrap=True).add_to(n)
            fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20,no_wrap=True).add_to(n)
            Fullscreen().add_to(n)
            folium_static(n)

        if options == "Day wise maps":
            unique_dates = rdf['date'].unique()
            l = []
            date_dataframes = {}
            for date in unique_dates:
                z = date[:10].replace('-', "_")
                l.append(z)
                date_dataframes[z] = rdf[rdf['date'] == date].copy()
            selected_dates = st.multiselect("Select Dates", l)

            if selected_dates:
                st.write("Selected Dataframe:")
                selected_date = selected_dates[-1]
                daydf = date_dataframes[selected_date]
                zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                d = fp.Popup(selected_date, parse_html=True)
                m = fp.Map(location=[16.9891, 82.2475], zoom_start=12)
                fp.PolyLine(locations=zipped, color='blue', popup=d).add_to(m)
                fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20, no_wrap=True).add_to(m)
                fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20,no_wrap=True).add_to(m)
                Fullscreen().add_to(m)
                folium_static(m)
            else:
                st.write("No dates selected.")

        if options == "compare maps":
            unique_dates = rdf['date'].unique()
            l = []
            date_dataframes = {}
            for date in unique_dates:
                z = date[:10].replace('-', "_")
                l.append(z)
                date_dataframes[z] = rdf[rdf['date'] == date].copy()
            selected_dates = st.multiselect("Select Dates", l)
            if selected_dates:
                st.sidebar.write("Selected Maps:")
                m = fp.Map(location=[16.9891, 82.2475], zoom_start=12,world_copy_jump=True)
                colors = ['blue', 'red', 'green', 'purple', 'orange', 'black', "pink", "yellow", "violet", "brown"]
                names_and_colors = [(date, colors[i % len(colors)]) for i, date in enumerate(selected_dates)]
                for date, color in names_and_colors:
                    daydf = date_dataframes[date]
                    zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                    fp.PolyLine(locations=zipped, color=color).add_to(m)
                    fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20, no_wrap=True).add_to(m)
                    fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20,no_wrap=True).add_to(m)
                    Fullscreen().add_to(m) 
                    st.sidebar.write(f"Map for {date} (Color: {color})")
                folium_static(m)
            else:
                st.write("No dates selected.")

        if options == "Bus standby":
            data = rdf
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

            user_date = st.date_input("Select a Date:")
            user_date = user_date.strftime('%Y-%m-%d')
            df = data[data['Time'].dt.strftime('%Y-%m-%d') == user_date]

            df_copy = df.copy()
            df_copy.drop(columns=['Altitude', 'priority', 'sat', 'event', 'rssi', 'io200', 'io69', 'pdop', 'hdop', 'power',
                                'battery', 'io68', 'odometer','totalDistance','distance','motion','hours'], inplace=True)
            df_copy['ignition'] = df_copy['ignition'].map({'true': True, 'false': False})
            df_copy['time'] = df_copy['Time'].diff()
            threshold = pd.Timedelta(minutes=5).total_seconds()

            df_stops_start = df_copy[(df_copy['ignition'] == True) & (df_copy['Speed'] == 0) & (df_copy['time'].dt.total_seconds() > threshold)]
            df_stops_stop = df_copy[(df_copy['ignition'] == False) & (df_copy['Speed'] == 0) & (df_copy['time'].dt.total_seconds() > threshold)]

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

            if intervals:
                df_first = pd.DataFrame(intervals[0])
                df_last = pd.DataFrame(intervals[-1])
                lat_first = df_first.iloc[0, 2]
                log_first = df_first.iloc[0, 3]

                ignition_map = fp.Map(location=[lat_first, log_first], zoom_start=13)
                for idx, row in df_stops_start.iterrows():
                    lat = row['Latitude']
                    log = row['Longitude']
                    popupcontent = f"<strong> time stayed: {row['time']}</strong>"
                    fp.Marker(location=[lat, log], icon=fp.features.CustomIcon('img/idling.png', icon_size=(42, 42)), popup=popupcontent).add_to(ignition_map)
                for idx, row in df_stops_stop.iterrows():
                    lat = row['Latitude']
                    log = row['Longitude']
                    popupcontent = f"<strong> time stayed: {row['time']}</strong>"
                    fp.Marker(location=[lat, log], icon=fp.features.CustomIcon('img/.png', icon_size=(42, 42)), popup=popupcontent).add_to(ignition_map)
                fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20, no_wrap=True).add_to(ignition_map)
                fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20,no_wrap=True).add_to(ignition_map)
                fp.plugins.Fullscreen().add_to(ignition_map)
                folium_static(ignition_map)
            else:
                st.warning("No intervals found for the selected date.")

        if options == "Geo Fence":
            radius = st.text_input("Enter Radius (in meters):")
            try:
                radius = float(radius)
                if radius < 0:
                    st.error("Radius must be a positive number.")
                    return
            except ValueError:
                st.error("Invalid input for radius. Please enter a numeric value.")
                return
            circle_center = [16.9800, 82.2395]
            geofence_polygon = Point(circle_center).buffer(radius / 111.32) 
            geofence_gdf = gpd.GeoDataFrame({'geometry': [geofence_polygon]}, crs="EPSG:4326")
            m = fp.Map(location=circle_center, zoom_start=12)
            fp.Circle(location=circle_center, radius=radius, color='green', fill=True, fill_color='green', fill_opacity=0.3).add_to(m)
            for index, row in rdf.iterrows():
                point = Point(row['Longitude'], row['Latitude'])
                if point.within(geofence_polygon):
                    fp.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=5, color='blue', fill=True, fill_color='blue', fill_opacity=0.7, popup="inside").add_to(m)
                else:
                    fp.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=5, color='blue', fill=True, fill_color='blue', fill_opacity=0.7, popup=f"Coordinates : {row['Address']}").add_to(m)
            # Adding tile layers and full-screen functionality
            fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20, no_wrap=True).add_to(m)
            fp.TileLayer(tiles='https://{s}.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', attr='Google', subdomains=['mt0', 'mt1', 'mt2', 'mt3'], max_zoom=20,no_wrap=True).add_to(m)
            Fullscreen().add_to(m)
            folium_static(m)



    elif choice == "5.Entry & Exit points":
            rdf = df[df['Latitude'] != 0]
            rdf[['date', 'time']] = rdf['Time'].str.split(' ', expand=True)
            unique_dates = rdf['date'].unique()
            l = []
            date_dataframes = {}  # Create a dictionary to store DataFrames

            for date in unique_dates:
                z = date[:10].replace('-', "_")
                l.append(z)
                date_dataframes[z] = rdf[rdf['date'] == date].copy()  # Store DataFrame in the dictionary

            selected_dates = st.multiselect("Select Dates", l)

            if selected_dates: 
                st.write("Selected Dataframe:")
                selected_date = selected_dates[-1]  
                daydf = date_dataframes[selected_date]
                
                def haversine(lat1, lon1, lat2, lon2):
                    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])  # Use 'map' directly
                    dlat, dlon = lat2 - lat1, lon2 - lon1
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    return 6371 * 2 * atan2(sqrt(a), sqrt(1 - a))
                
                circle_centers = {
                    "Pitapuram": (17.12069941663565, 82.25250466805956, 1.0),
                    "Junior College": (16.972599268499, 82.24037203701558, 1.0), 
                    "Surampalem": (17.089768812937248, 82.06717500416023, 1.0),    
                }
                circle_centers1 = {
                    "Surampalem": (17.089768812937248, 82.06717500416023, 1.0),
                    "Junior College": (16.972599268499, 82.24037203701558, 1.0), 
                    "Pitapuram": (17.12069941663565, 82.25250466805956, 1.0),    
                }
                st.subheader("ForeNoon")
                daydf['Time'] = pd.to_datetime(daydf['Time'])
                for name, center in circle_centers.items():
                    center_latitude, center_longitude, radius = center
                    st.write('<span style="color: orange;">Centre:</span>',f'<span style="color: white;">{name}</span>', unsafe_allow_html=True)
                    
                    for period, df in [("AM", daydf[daydf['Time'].dt.hour < 12])]:
                        entry, exit = None, None
                        for _, row in df.iterrows():
                            dist = haversine(center_latitude, center_longitude, row['Latitude'], row['Longitude'])
                            if dist <= radius:
                                if entry is None:
                                    entry = row['Time']
                                    entry=str(entry)[11:]
                                exit = row['Time']
                                exit=str(exit)[11:]
                        if entry and exit:
                            # entry = (f"{entry}")
                            # exit  = (f"{exit} {period}")
                            
                            st.write('<span style="color: aqua;">Entry Point:  </span>',f'<span style="color: yellow;"> {entry}</span>',f'<span style="color: orange;">{period}</span>', unsafe_allow_html=True)
                            st.write('<span style="color: white;">Exit Point:  </span>',f'<span style="color: skyblue;"> {exit}</span>',f'<span style="color: lightgreen;">{period}</span>', unsafe_allow_html=True)
                st.subheader("AfterNoon")
                for name, center in circle_centers1.items():
                    center_latitude, center_longitude, radius = center
                    st.write('<span style="color: orange;">Centre:</span>',f'<span style="color: white;">{name}</span>', unsafe_allow_html=True)

                    for period, df in [("PM", daydf[daydf['Time'].dt.hour > 12])]:
                        entry, exit = None, None
                        for _, row in df.iterrows():
                            dist = haversine(center_latitude, center_longitude, row['Latitude'], row['Longitude'])
                            if dist <= radius:
                                if entry is None:
                                    entry = row['Time']
                                    entry=str(entry)[11:]
                                exit = row['Time']
                                exit=str(exit)[11:]
                        if entry and exit:
                            # entry = (f"{entry}")
                            # exit  = (f"{exit} {period}")
                            st.write('<span style="color: aqua;">Entry Point:  </span>',f'<span style="color: yellow;"> {entry}</span>',f'<span style="color: orange;">{period}</span>', unsafe_allow_html=True)
                            st.write('<span style="color: white;">Exit Point:  </span>',f'<span style="color: skyblue;"> {exit}</span>',f'<span style="color: lightgreen;">{period}</span>', unsafe_allow_html=True)



    elif choice == "About Creator🧐":
        st.subheader("About Creator")
        with st.expander("Kalyan Kanchumarthi"):
                col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed
                with col1:
                    st.image("mypic.jpg", use_column_width=True)
                with col2:
                    st.write("""
                    Hello! I'm Kalyan Kanchumarthi, \n
                    a passionate developer exploring the world of AI and programming.

                    - I love building applications that make life easier.
                    - I'm good at Python and data analysis.
                    - Don't misunderstand me as a nerd; I'm socially adept too! 😄
                    - Thank you for checking out my app!

                    Do check out my [LinkedIn](https://www.linkedin.com/in/kalyan-kanchumarthi-a6320a235/) and [GitHub](https://github.com/SrinivasaKalyan).
                    """)

  
    with st.sidebar:
        st_lottie(lottie_animation, height=200, key="lottie_animation")


if __name__ == '__main__':
    main()
