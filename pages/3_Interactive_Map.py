import streamlit as st
import pandas as pd
import numpy as np
from utils.visualization import MapVisualizer
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Interactive Map", page_icon="", layout="wide")

# Custom CSS
def load_css():
    try:
        with open("assets/styles/custom.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 60px 0; text-align: center; color: white; border-radius: 20px; margin-bottom: 40px;">
    <h1 style="margin: 0;"> Interactive Hotspot Map</h1>
    <p style="margin: 10px 0 0 0; font-size: 1.2rem;">Visualize accident hotspots on an interactive map</p>
</div>
""", unsafe_allow_html=True)

# Check if data is available
if 'accident_data' not in st.session_state:
    st.error(" Please upload your data first in the 'Upload Data' page!")
    st.markdown("""
    <div style="text-align: center; margin: 30px 0;">
        <a href="/Upload_Data" target="_self" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 15px 30px; 
            border-radius: 25px; 
            text-decoration: none; 
            font-weight: bold;
            display: inline-block;
        "> Go to Upload Data</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Load data
df = st.session_state['accident_data']
visualizer = MapVisualizer()

# Initialize session state for map
if 'map_generated' not in st.session_state:
    st.session_state.map_generated = False
if 'current_map' not in st.session_state:
    st.session_state.current_map = None
if 'map_type' not in st.session_state:
    st.session_state.map_type = "Point Map"

# Map type selection
st.markdown("##  Choose Map Visualization")

col1, col2 = st.columns(2)

with col1:
    map_type = st.radio(
        "Map Type:",
        ["Point Map", "Heat Map", "Cluster Map"],
        help="Point: Individual accidents. Heat: Density visualization. Cluster: Grouped accidents.",
        key="map_type_selector"
    )

with col2:
    base_map = st.selectbox(
        "Base Map Style:",
        ["OpenStreetMap", "CartoDB Positron", "CartoDB Dark_Matter"],
        help="Choose the underlying map style",
        key="base_map_selector"
    )

# Map customization
st.markdown("##  Map Settings")

col1, col2 = st.columns(2)

with col1:
    zoom_level = st.slider("Zoom Level", 10, 16, 12, key="zoom_slider")
    
    if map_type == "Heat Map":
        radius = st.slider("Heat Radius", 5, 30, 15, key="heat_radius")
    else:
        radius = st.slider("Point Radius", 5, 15, 8, key="point_radius")

with col2:
    opacity = st.slider("Opacity", 0.1, 1.0, 0.7, key="opacity_slider")
    
    if map_type == "Point Map":
        point_size = st.slider("Point Size", 3, 10, 6, key="point_size_slider")

# Generate map button
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    generate_map = st.button(" Generate Map", use_container_width=True, type="primary")

# Generate or display map
if generate_map or st.session_state.map_generated:
    with st.spinner("Creating interactive map..."):
        try:
            # Store map settings in session state
            st.session_state.map_type = map_type
            st.session_state.map_generated = True
            
            if map_type == "Cluster Map":
                # Check if clusters exist, if not create simple clusters
                if 'clusters' in st.session_state:
                    df_with_clusters = st.session_state['clustered_data']
                    m = visualizer.create_cluster_map(df_with_clusters)
                else:
                    # Create simple clustering for visualization
                    st.info("Using simple clustering for visualization")
                    m = visualizer.create_cluster_map(df)
                    
            elif map_type == "Heat Map":
                m = visualizer.create_heat_map(df, radius=radius)
                
            else:  # Point Map
                m = visualizer.create_point_map(df, point_size=point_size, opacity=opacity)
            
            # Set base map
            if base_map == "CartoDB Positron":
                folium.TileLayer('CartoDB positron').add_to(m)
            elif base_map == "CartoDB Dark_Matter":
                folium.TileLayer('CartoDB dark_matter').add_to(m)
            else:
                folium.TileLayer('OpenStreetMap').add_to(m)
            
            # Store the map in session state
            st.session_state.current_map = m
            
            # Display success message
            st.success(f" {map_type} generated successfully!")
            
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            st.info("Try using Point Map instead for simpler visualization")

# Display the map if it exists
if st.session_state.map_generated and st.session_state.current_map is not None:
    st.markdown("###  Interactive Map")
    
    # Display the map
    map_data = st_folium(
        st.session_state.current_map, 
        width=1200, 
        height=600,
        key="main_map"
    )
    
    # Show map interaction info
    if map_data and map_data.get("last_clicked"):
        st.info(f" Last clicked location: {map_data['last_clicked']}")
    
    # Add a button to regenerate map with current settings
    if st.button("🔄 Regenerate Map", key="regenerate_map"):
        st.session_state.map_generated = False
        st.rerun()

# Coimbatore focus areas
st.markdown("---")
st.markdown("##  Coimbatore Focus Areas")

# Define Coimbatore areas
coimbatore_areas = {
    'Kovaipudur': (11.0014, 76.9627),
    'Gandhipuram': (11.0168, 76.9558),
    'Ukkadam': (10.9905, 76.9614),
    'Kuniyamuthur': (11.0189, 76.9565)
}

# Create area analysis
area_data = []
for area, (lat, lon) in coimbatore_areas.items():
    area_accidents = df[
        (df['Latitude'].between(lat-0.02, lat+0.02)) &
        (df['Longitude'].between(lon-0.02, lon+0.02))
    ]
    
    area_data.append({
        'Area': area,
        'Accident_Count': len(area_accidents),
        'Avg_Severity': area_accidents['Severity'].mean() if len(area_accidents) > 0 else 0,
        'Latitude': lat,
        'Longitude': lon
    })

area_df = pd.DataFrame(area_data)

col1, col2 = st.columns(2)

with col1:
    if not area_df.empty:
        fig = px.bar(
            area_df,
            x='Area',
            y='Accident_Count',
            title="Accidents in Coimbatore Areas",
            color='Avg_Severity',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not area_df.empty:
        fig = px.bar(
            area_df,
            x='Area',
            y='Avg_Severity',
            title="Average Severity by Coimbatore Area",
            color='Avg_Severity',
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)

# Export options
st.markdown("---")
st.markdown("##  Export Options")

col1, col2 = st.columns(2)

with col1:
    if st.button(" Save Map as HTML", use_container_width=True):
        if st.session_state.current_map:
            try:
                st.session_state.current_map.save("hotspot_map.html")
                st.success("Map saved as 'hotspot_map.html' in your project folder!")
            except Exception as e:
                st.error(f"Error saving map: {e}")
        else:
            st.warning("Please generate a map first!")

with col2:
    if st.button(" Take Screenshot", use_container_width=True):
        st.info("Use your browser's screenshot functionality (Ctrl+Shift+S) to capture the map")

# Instructions
st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
    <h4> Map Usage Tips</h4>
    <ul style="text-align: left; display: inline-block;">
        <li>Zoom in/out using mouse wheel or +/- buttons</li>
        <li>Click and drag to pan around the map</li>
        <li>Click on points to see accident details</li>
        <li>Use different base maps for better visualization</li>
        <li>The map will stay visible until you regenerate or leave the page</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Debug information (can be removed in production)
with st.expander(" Debug Information"):
    st.write(f"Map generated: {st.session_state.map_generated}")
    st.write(f"Current map type: {st.session_state.map_type}")
    st.write(f"Data points: {len(df)}")
    if 'clusters' in st.session_state:
        st.write(f"Clusters available: {len(np.unique(st.session_state.clusters))}")