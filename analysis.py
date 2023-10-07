import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import folium as fp
from streamlit_folium import folium_static





def main():
    # setting our web page layout as wide view

    st.set_page_config(layout="wide")
    # grouping tasks for the sidebar
    EDA_tasks = ["1.distinguish attributes","2.Data Cleaning", "3.Maps"]
    # choosing from the sidebar
    choice = st.sidebar.radio("select tasks:", EDA_tasks)
    # setting our file input format types
    file_format = st.radio('Select file format:', ('csv', 'excel'), key='file_format')
    # setting a file uploader in our web application
    data = st.file_uploader("UPLOAD A DATASET 	:open_file_folder: ")



    if data:
        if file_format == 'csv':
            df = pd.read_csv(data)
        else:
            df = pd.read_excel(data)
        st.dataframe(df.head())


    # if 'my_dframe1' not in st.session_state:
    #     st.session_state.my_dframe1 = pd.DataFrame()
    # if 'my_dframe2' not in st.session_state:
    #     st.session_state.my_dframe2 = pd.DataFrame()
    # if 'my_dframe3' not in st.session_state:
    #     st.session_state.my_dframe3 = pd.DataFrame()

    if choice == '1.distinguish attributes':
        # assigning heading to the choice
        st.subheader(" Distinguishing attributes  :1234:")
        da_tasks = ("Show Shape","Show Columns","Summary","Show Selected Columns","show numerical variables","show categorical variables","percentage distribution of unique values in fields")
        da_options = st.sidebar.selectbox("Distinguishing attributes in EDA", da_tasks)
        # creating a checkbox to display shape(rows and columns) in the data
        if da_options == "Show Shape":
            st.subheader("Show Shape")
            if data is not None:
                st.write("rows and columns formate ", df.shape)

        # creating a checkbox to display  columns in the data
        if da_options == "Show Columns":
            st.subheader("Show Columns")
            all_columns = df.columns.to_list()
            st.write(all_columns)

        # creating a checkbox to display  summary of the data
        if da_options == "Summary":
            st.subheader("Summary")
            st.write(df.describe())

        # creating a checkbox to display  selected columns in the data
        if da_options == "Show Selected Columns":
            st.subheader("Show Selected Columns")
            all_columns = df.columns.to_list()
            selected_columns = st.multiselect("Select Columns", all_columns)
            new_df = df[selected_columns]
            st.dataframe(new_df)
        # creating a checkbox to display  only numerical columns in the data
        if da_options == "show numerical variables":
            st.subheader("Show numerical variables")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            newdf = df.select_dtypes(include=numerics)
            st.dataframe(newdf)

        # creating a checkbox to display  only categorical columns in the data
        if da_options == "show categorical variables":
            st.subheader("Show categorical variables")
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            newdf = df.select_dtypes(include=numerics)
            df1 = df.drop(newdf, axis=1)
            st.dataframe(df1)

        # creating a checkbox to display  percentage of unique values in as selected column in the data
        if da_options == "percentage distribution of unique values in fields":
            st.subheader("percentage distribution of unique values in fields")
            all_columns = df.columns.to_list()
            sel_cols = st.multiselect("Select Columns", all_columns)
            cd = df[sel_cols].value_counts(normalize=True) * 100
            st.dataframe(cd)

    elif choice == '2.Data Cleaning':
        st.subheader(" Data cleaning 🛠️")
        options = st.sidebar.selectbox("Select an option", ["Show the NA values", "Remove duplicate values", "Speed"])        
        rdf = df[df['Latitude'] != 0]
     
    
        if options == "Show the NA values":
            st.subheader("Show the NA values")
            nas = df.isnull().sum()
            st.dataframe(nas)

        

        if options == "Remove duplicate values":
            st.subheader("Remove duplicate values")
            st.dataframe(rdf)
            st.download_button(label='Download CSV', data=rdf.to_csv(), mime='text/csv')

        if options == "Speed":
            tasks = ("Average speed", "Min speed", "Max speed", "Total distance" , "Overspeed")
            option = st.selectbox("Speed", tasks)
            st.subheader("Speed")
            rdf['int_speed'] = rdf.apply(lambda row: float(row['Speed'][:-4]), axis=1)
            
            if option == "Average speed":
                st.write(rdf.int_speed.mean())
            elif option == "Min speed":
                st.write(rdf.int_speed.min())
            elif option == "Max speed":
                st.write(rdf.int_speed.max())
            elif option == "Total distance":
                x = rdf  # Use the filtered DataFrame 'rdf' here
                x['Prev_Latitude'] = x['Latitude'].shift()
                x['Prev_Longitude'] = x['Longitude'].shift()
                x = x.dropna()
                x['Distance'] = x.apply(lambda row: geodesic((row['Prev_Latitude'], row['Prev_Longitude']),
                                                            (row['Latitude'], row['Longitude'])).kilometers, axis=1)
                total_distance = x['Distance'].sum()
                st.write(total_distance)
            elif option == "Overspeed":
                fdf = rdf[rdf['int_speed'] > 50]
                st.dataframe(fdf.Address)

    elif choice == "3.Maps":
        st.subheader(" Maps")
        rdf = df[df['Latitude'] != 0]
        df['int_speed'] = df.apply(lambda row: float(row['Speed'][:-4]), axis=1)
        fdf = df[df['int_speed'] > 50]
        options = st.sidebar.selectbox("Select an option", ["overspeed_map", "Total coordinates map"  , "Day wise maps" , "compare maps"])  
        rdf = df[df['Latitude'] != 0]

        if options == "overspeed_map":

            fm = fp.Map(location=[16.9891, 82.2475], zoom_start=12)

            for index, row in fdf.iterrows():
                fp.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=5,  # Adjust the radius as needed (size of the dots)

                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=1.0,  # Set fill_opacity to 1 to make it solid
                    popup=f"speed: {row['int_speed']}",  # Customize the popup as needed
                ).add_to(fm)

            folium_static(fm)

        if options == "Total coordinates map":
            coordinates = list(zip(rdf['Latitude'], rdf['Longitude']))

            # Create a Folium map
            n = fp.Map(location=[16.9891, 82.2475], zoom_start=12)

            # Create a PolyLine with the given coordinates (color is blue)

            # Add CircleMarkers along the PolyLine path
            for coord in coordinates:
                fp.CircleMarker(
                    location=coord,
                    radius=5,
                    color='blue',  # Change this color as needed
                    fill=True,
                    fill_color='blue',  # Change this color as needed
                    fill_opacity=0.7,
                ).add_to(n)

            # Display the map
            folium_static(n)

        if options == "Day wise maps":
            rdf[['date', 'time']] = rdf['Time'].str.split(' ', expand=True)
            unique_dates = rdf['date'].unique()
            l = []
            date_dataframes = {}  # Create a dictionary to store DataFrames

            for date in unique_dates:
                z = date[:10].replace('-', "_")
                l.append(z)
                date_dataframes[z] = rdf[rdf['date'] == date].copy()  # Store DataFrame in the dictionary

            selected_dates = st.multiselect("Select Dates", l)

            selected_dataframes = [date_dataframes[date] for date in selected_dates]

            if selected_dataframes:
                st.write("Selected Dataframes:")
                for i in selected_dataframes:
                    daydf=i
                    zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                    d = fp.Popup('daydf', parse_html=True)
                    map = fp.Map(location=[16.9891, 82.2475], zoom_start=12)
                    fp.PolyLine(locations=zipped, color='blue' ,popup = d).add_to(map)
                    folium_static(map)

            else:
                st.write("No dates selected.")

        # if options == "compare maps":
        #     rdf[['date', 'time']] = rdf['Time'].str.split(' ', expand=True)
        #     unique_dates = rdf['date'].unique()
        #     l = []
        #     date_dataframes = {}  # Create a dictionary to store DataFrames

        #     for date in unique_dates:
        #         z = date[:10].replace('-', "_")
        #         l.append(z)
        #         date_dataframes[z] = rdf[rdf['date'] == date].copy()  # Store DataFrame in the dictionary

        #     selected_dates = st.multiselect("Select Dates", l)

        #     if selected_dates:
        #         st.sidebar.write("Selected Maps:")
        #         map = fp.Map(location=[16.9891, 82.2475], zoom_start=12)  # Create a single map
        #         colors = ['blue', 'red', 'green', 'purple', 'orange', 'black',"pink","yellow","violet","indigo"]  # List of colors
                
        #         for i, date in enumerate(selected_dates):
        #             daydf = date_dataframes[date]
        #             zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                    
        #             # Use a unique color for each DataFrame
        #             color_index = i % len(colors)
        #             color = colors[color_index]
                    
        #             fp.PolyLine(locations=zipped, color=color).add_to(map)  # Add polyline with unique color
        #             st.sidebar.write(f"Map for {date}")
                
        #         folium_static(map)  # Display the single map with all polylines
        #     else:
        #         st.write("No dates selected.")
        if options == "compare maps":
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
                st.sidebar.write("Selected Maps:")
                map = fp.Map(location=[16.9891, 82.2475], zoom_start=12)  # Create a single map
                colors = ['blue', 'red', 'green', 'purple', 'orange', 'black', "pink","yellow","violet","brown"]  # List of colors
                
                # Create a list to store names and colors
                names_and_colors = [(date, colors[i % len(colors)]) for i, date in enumerate(selected_dates)]
                
                for date, color in names_and_colors:
                    daydf = date_dataframes[date]
                    zipped = list(zip(daydf['Latitude'], daydf['Longitude']))
                    
                    fp.PolyLine(locations=zipped, color=color).add_to(map)  # Add polyline with unique color
                    st.sidebar.write(f"Map for {date} (Color: {color})")
                
                folium_static(map)  # Display the single map with all polylines
            else:
                st.write("No dates selected.")


                        
if __name__ == '__main__':
    main()