import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def get_coordinates_cached(location_name):
    """Mengembalikan (lat, lng) dengan cache berbasis session."""
    if "geocode_cache" not in st.session_state:
        st.session_state.geocode_cache = {}

    if location_name in st.session_state.geocode_cache:
        return st.session_state.geocode_cache[location_name]
    
    try:
        geolocator = Nominatim(user_agent="mscrape_tool_v1")
        loc_obj = geolocator.geocode(location_name, timeout=10)
        if loc_obj:
            coords = (loc_obj.latitude, loc_obj.longitude)
            st.session_state.geocode_cache[location_name] = coords
            return coords
        else:
            return None
    except (GeocoderTimedOut, GeocoderServiceError):
        return None
