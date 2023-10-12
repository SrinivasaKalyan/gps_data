import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import folium as fp
from streamlit_folium import folium_static
from shapely.geometry import Point, Polygon
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2





def main():
    st.set_page_config(layout="wide")
    EDA_tasks = ["1.distinguish attributes","2.Data Cleaning", "3.Speed","4.Maps","5.Entry & Exit points"]
    choice = st.sidebar.radio("select tasks:", EDA_tasks)
    file_format = st.radio('Select file format:', ('csv', 'excel'), key='file_format')
    data = st.file_uploader("UPLOAD A DATASET 	:open_file_folder: ")



    if data:
        if file_format == 'csv':
            df = pd.read_csv(data)
        else:
            df = pd.read_excel(data)
        st.dataframe(df.head())
        st.dataframe(df)

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

    if choice == "3.Speed":
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
            st.subheader(" Min Speed")
            st.write(rdf.int_speed.min())
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
        st.subheader(" Maps")
        rdf = df[df['Latitude'] != 0]
        df['int_speed'] = df.apply(lambda row: float(row['Speed'][:-4]), axis=1)
        fdf = df[df['int_speed'] > 50]
        options = st.sidebar.selectbox("Select an option", ["overspeed map", "Total coordinates map"  , "Day wise maps" , "compare maps","Bus standby" , "Geo Fence"])  
        rdf = df[df['Latitude'] != 0]
        if options == "overspeed map":
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
            folium_static(fm)

        if options == "Total coordinates map":
            coordinates = list(zip(rdf['Latitude'], rdf['Longitude']))
            n = fp.Map(location=[16.9891, 82.2475], zoom_start=12)
            for coord in coordinates:
                fp.CircleMarker(
                    location=coord,
                    radius=5,
                    color='blue',  
                    fill=True,
                    fill_color='blue',  
                    fill_opacity=0.7,
                ).add_to(n)
            folium_static(n)

        if options == "Day wise maps":
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
                daydf = date_dataframes[selected_date]
                zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                d = fp.Popup(selected_date, parse_html=True)
                m = fp.Map(location=[16.9891, 82.2475], zoom_start=12)
                fp.PolyLine(locations=zipped, color='blue', popup=d).add_to(m)
                folium_static(m) 
                st.write("No dates selected.")

        if options == "compare maps":
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
                st.sidebar.write("Selected Maps:")
                m = fp.Map(location=[16.9891, 82.2475], zoom_start=12)  
                colors = ['blue', 'red', 'green', 'purple', 'orange', 'black', "pink","yellow","violet","brown"] 
                names_and_colors = [(date, colors[i % len(colors)]) for i, date in enumerate(selected_dates)]
                for date, color in names_and_colors:
                    daydf = date_dataframes[date]
                    zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                    fp.PolyLine(locations=zipped, color=color).add_to(m) 
                    st.sidebar.write(f"Map for {date} (Color: {color})")
                folium_static(m)  
            else:
                st.write("No dates selected.")
        
        if options == "Bus standby":
            sdf=rdf['Attributes'].str.split(' ',expand=True)
            rdf=pd.concat([rdf,sdf[6]],axis=1)
            rdf[6] = rdf.apply(lambda row: str(row[6][9:]), axis=1)
            xdf = rdf[(rdf[6] == 'true')& (df['int_speed'] == 0) ]
            m1 = fp.Map(location=[16.9891, 82.2475], zoom_start=12)
            for index, row in xdf.iterrows():
                fp.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=3,  
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=1.0, 
                    popup=f"Day: {row['int_speed']}<br>ignition: {row[6]}").add_to(m1)
            folium_static(m1)

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
            geofence_polygon = Point(circle_center).buffer(radius / 111.32)  # Assuming you're working with lat-long in degrees
            geofence_gdf = gpd.GeoDataFrame({'geometry': [geofence_polygon]}, crs="EPSG:4326")
            m = fp.Map(location=circle_center, zoom_start=12)
            fp.Circle(location=circle_center, radius=radius, color='green', fill=True, fill_color='green', fill_opacity=0.3).add_to(m)
            for index, row in rdf.iterrows():
                point = Point(row['Longitude'], row['Latitude'])
                if point.within(geofence_polygon):
                    fp.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=5, color='blue', fill=True, fill_color='blue', fill_opacity=0.7, popup="inside").add_to(m)
                else:
                    fp.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=5, color='blue', fill=True, fill_color='blue', fill_opacity=0.7, popup=f"Coordinates : {row['Address']}").add_to(m)
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
                      
if __name__ == '__main__':
    main()