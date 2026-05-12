import streamlit as st
import pandas as pd

def render_maps_page():
    """Render the maps page with city selection and map display"""
    st.title("🗺️ City Maps")
    
    # City selection with coordinates
    city_options = {
        "Moscow": {"lat": 55.7558, "lon": 37.6176},
        "Saint Petersburg": {"lat": 59.9311, "lon": 30.3609},
        "Novosibirsk": {"lat": 55.0084, "lon": 82.9357}
    }
    
    selected_city = st.radio(
        "Choose a city:",
        options=list(city_options.keys()),
        index=0
    )
    
    # Get coordinates for selected city
    city_coords = city_options[selected_city]
    
    # Create DataFrame with city coordinates for st.map
    map_data = pd.DataFrame({
        'lat': [city_coords["lat"]],
        'lon': [city_coords["lon"]]
    })
    
    # Display city information
    st.subheader(f"📍 {selected_city}")
    st.write(f"Latitude: {city_coords['lat']}")
    st.write(f"Longitude: {city_coords['lon']}")
    
    # Display the map with the selected city marked
    st.map(map_data, zoom=10)