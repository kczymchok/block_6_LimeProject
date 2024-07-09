import streamlit as st
import requests
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.distance import distance
from streamlit_folium import folium_static

st.title('Lean the Juice !')

# Function to load data
def load_data():
    df_mapping = pd.read_csv('/app/data/df_mapping.csv')
    return df_mapping

# Load the data
df_mapping = load_data()

# Input fields
year = st.number_input('Year', min_value=2000, max_value=2100, value=2024)
month = st.number_input('Month', min_value=1, max_value=12, value=8)
day = st.number_input('Day', min_value=1, max_value=31, value=26)
time_hours = st.number_input('Time in Hours', min_value=0, max_value=24, value=14, step=1)

# Input address
input_address = st.text_input('Enter your address in Île-de-France')

# Geocode the input address
if input_address:
    geolocator = Nominatim(user_agent="bike_availability_app")
    location = geolocator.geocode(input_address)
    if location:
        st.info(f"Location found: {location.address}")
        input_coords = (location.latitude, location.longitude)

        # Find the closest stations with predicted 0 bike availability
        closest_stations = []
        all_stations = []
        for stationcode in df_mapping['stationcode'].unique():
            capacity = int(df_mapping.loc[df_mapping['stationcode'] == stationcode, 'capacity'].iloc[0])
            payload = {
                "year": int(year),
                "month": int(month),
                "day": int(day),
                "time_seconds": int(time_hours * 3600),
                "stationcode": str(stationcode),
                "capacity": capacity
            }
            response = requests.post('http://fastapi:8000/predict', json=payload)

            if response.status_code == 200:
                result = response.json()
                predicted_bikes = result['number_of_bikes']
                station_coords = (df_mapping.loc[df_mapping['stationcode'] == stationcode, 'latitude'].iloc[0],
                                  df_mapping.loc[df_mapping['stationcode'] == stationcode, 'longitude'].iloc[0])
                station_info = {
                    'stationcode': stationcode,
                    'latitude': station_coords[0],
                    'longitude': station_coords[1],
                    'predicted_bikes': predicted_bikes,
                    'capacity': capacity
                }
                all_stations.append(station_info)
                if predicted_bikes < 0.1 * capacity:
                    station_distance = distance(input_coords, station_coords).km
                    station_info['distance_km'] = station_distance
                    closest_stations.append(station_info)
            else:
                st.warning(f"Failed to predict for station code {stationcode}. Error: {response.status_code}")

        # Sort stations by distance and display top 5 closest
        closest_stations.sort(key=lambda x: x['distance_km'])

        # Display results on map
        if closest_stations:
            map_center = input_coords
            m = folium.Map(location=map_center, zoom_start=13, control_scale=True)

            # Add marker for input address in blue color
            folium.Marker(
                location=input_coords,
                popup=f"Your Address: {input_address}",
                icon=folium.Icon(color='blue', icon='home', prefix='fa')
            ).add_to(m)

            # Add markers for closest stations
            for idx, station in enumerate(closest_stations[:5]):
                popup_text = f"Rank: {idx + 1}<br>Station Code: {station['stationcode']}<br>Predicted Bikes: {station['predicted_bikes']}<br>Distance: {station['distance_km']:.2f} km"
                folium.Marker(
                    location=(station['latitude'], station['longitude']),
                    popup=popup_text,
                    icon=folium.Icon(color='green' if station['predicted_bikes'] == 0 else 'orange', icon='bicycle', prefix='fa')
                ).add_to(m)

            folium_static(m)

        else:
            st.warning("No predictions found for stations with less than 10% availability.")

        # Display another map with all stations that have less than 10% capacity
        m_all = folium.Map(location=map_center, zoom_start=13, control_scale=True)

        # Add marker for input address in blue color
        folium.Marker(
            location=input_coords,
            popup=f"Your Address: {input_address}",
            icon=folium.Icon(color='blue', icon='home', prefix='fa')
        ).add_to(m_all)

        for station in all_stations:
            if station['predicted_bikes'] < 0.1 * station['capacity']:
                popup_text = f"Station Code: {station['stationcode']}<br>Predicted Bikes: {station['predicted_bikes']}"
                folium.Marker(
                    location=(station['latitude'], station['longitude']),
                    popup=popup_text,
                    icon=folium.Icon(color='green' if station['predicted_bikes'] == 0 else 'orange', icon='bicycle', prefix='fa')
                ).add_to(m_all)

        st.subheader("All Stations with Less Than 10% Availability")
        folium_static(m_all)

    else:
        st.error("Address not found. Please enter a valid address.")

# # Optionally, display the raw data
# st.subheader("Mapped Station Data:")
# st.write(df_mapping)
