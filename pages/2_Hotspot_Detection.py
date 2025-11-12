import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor
from utils.ml_model import HotspotModel
from utils.visualization import MapVisualizer
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import silhouette_score

st.set_page_config(page_title="Hotspot Detection", page_icon="", layout="wide")

# Custom CSS
def load_css():
    with open("assets/styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Header
st.markdown("""
<div class="hero-section" style="padding: 60px 0; margin-bottom: 40px;">
    <h1 style="text-align: center; margin: 0;"> Hotspot Detection</h1>
    <p style="text-align: center; margin: 10px 0 0 0; font-size: 1.2rem;">AI-powered clustering to identify high-risk accident zones</p>
</div>
""", unsafe_allow_html=True)

# Check if data is uploaded
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
processor = DataProcessor()
model = HotspotModel()
visualizer = MapVisualizer()

# Algorithm selection
st.markdown("##  Choose Clustering Algorithm")

col1, col2 = st.columns(2)

with col1:
    algorithm = st.radio(
        "Select clustering method:",
        ["DBSCAN", "K-Means"],
        help="DBSCAN: Density-based, automatically finds clusters. K-Means: Specify number of clusters."
    )

with col2:
    st.markdown("""
    <div style="background: #e8f4fd; padding: 20px; border-radius: 10px;">
        <h4>🔍 Algorithm Info</h4>
        <p><strong>DBSCAN:</strong> Good for finding irregular-shaped clusters, automatically determines number of clusters</p>
        <p><strong>K-Means:</strong> Faster for large datasets, requires specifying number of clusters</p>
    </div>
    """, unsafe_allow_html=True)

# Parameters
st.markdown("##  Algorithm Parameters")

if algorithm == "DBSCAN":
    col1, col2 = st.columns(2)
    with col1:
        eps = st.slider("EPS (Neighborhood radius)", 0.001, 0.05, 0.01, 0.001,
                       help="Larger values form larger clusters")
    with col2:
        min_samples = st.slider("Minimum samples", 2, 10, 3,
                               help="Minimum points to form a cluster")
    
    model.dbscan = model.dbscan.set_params(eps=eps, min_samples=min_samples)

else:  # K-Means
    n_clusters = st.slider("Number of clusters", 2, 10, 5,
                          help="Number of hotspot clusters to identify")

# Perform clustering
if st.button(" Detect Hotspots", use_container_width=True):
    with st.spinner("🔍 Analyzing accident patterns and detecting hotspots..."):
        coordinates = df[['Latitude', 'Longitude']].values
        
        if algorithm == "DBSCAN":
            clusters = model.detect_hotspots_dbscan(coordinates)
            n_clusters_found = len(set(clusters)) - (1 if -1 in clusters else 0)
            noise_points = np.sum(clusters == -1)
            
            # Store results
            st.session_state['clusters'] = clusters
            st.session_state['algorithm'] = 'DBSCAN'
            st.session_state['n_clusters'] = n_clusters_found
            
            # Display results
            st.success(f" Found {n_clusters_found} hotspots with {noise_points} noise points")
            
        else:  # K-Means
            clusters, centers = model.detect_hotspots_kmeans(coordinates, n_clusters)
            
            # Store results
            st.session_state['clusters'] = clusters
            st.session_state['centers'] = centers
            st.session_state['algorithm'] = 'K-Means'
            st.session_state['n_clusters'] = n_clusters
            
            st.success(f" Identified {n_clusters} hotspots using K-Means")
        
        # Add clusters to dataframe
        df['Cluster'] = st.session_state['clusters']
        st.session_state['clustered_data'] = df

# Display results if clustering is done
if 'clusters' in st.session_state:
    df = st.session_state['clustered_data']
    
    st.markdown("##  Hotspot Analysis Results")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_hotspots = st.session_state['n_clusters']
        st.metric("Total Hotspots", total_hotspots)
    
    with col2:
        total_accidents = len(df)
        st.metric("Total Accidents", total_accidents)
    
    with col3:
        if st.session_state['algorithm'] == 'DBSCAN':
            noise_points = np.sum(st.session_state['clusters'] == -1)
            st.metric("Noise Points", noise_points)
        else:
            avg_cluster_size = len(df) / st.session_state['n_clusters']
            st.metric("Avg Cluster Size", f"{avg_cluster_size:.1f}")
    
    with col4:
        if st.session_state['algorithm'] == 'K-Means':
            silhouette_avg = silhouette_score(df[['Latitude', 'Longitude']], df['Cluster'])
            st.metric("Cluster Quality", f"{silhouette_avg:.3f}")
        else:
            cluster_accidents = len(df[df['Cluster'] != -1])
            st.metric("Clustered Accidents", cluster_accidents)
    
    # Cluster statistics
    st.markdown("###  Cluster Statistics")
    
    if st.session_state['algorithm'] == 'DBSCAN':
        cluster_df = df[df['Cluster'] != -1].copy()
    else:
        cluster_df = df.copy()
    
    cluster_stats = cluster_df.groupby('Cluster').agg({
        'Severity': ['count', 'mean', 'max'],
        'Vehicles_Involved': 'mean',
        'Speed_Limit': 'mean'
    }).round(2)
    
    cluster_stats.columns = ['Accident_Count', 'Avg_Severity', 'Max_Severity', 'Avg_Vehicles', 'Avg_Speed_Limit']
    cluster_stats = cluster_stats.sort_values('Accident_Count', ascending=False)
    
    st.dataframe(cluster_stats, use_container_width=True)
    
    # Visualizations
    st.markdown("###  Hotspot Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cluster distribution
        cluster_counts = df['Cluster'].value_counts().sort_index()
        fig = px.bar(
            x=cluster_counts.index,
            y=cluster_counts.values,
            title=f"Accidents per Cluster ({st.session_state['algorithm']})",
            labels={'x': 'Cluster ID', 'y': 'Number of Accidents'},
            color=cluster_counts.values,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Severity by cluster
        severity_by_cluster = df.groupby('Cluster')['Severity'].mean().sort_index()
        fig = px.line(
            x=severity_by_cluster.index,
            y=severity_by_cluster.values,
            title="Average Severity by Cluster",
            labels={'x': 'Cluster ID', 'y': 'Average Severity'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Area analysis within clusters
    st.markdown("###  Area-wise Cluster Analysis")
    
    if st.session_state['algorithm'] == 'DBSCAN':
        valid_clusters = df[df['Cluster'] != -1]
    else:
        valid_clusters = df
    
    area_cluster = pd.crosstab(valid_clusters['Area'], valid_clusters['Cluster'])
    st.dataframe(area_cluster.style.background_gradient(cmap='Blues'), use_container_width=True)
    
    # Generate map
    st.markdown("### Interactive Hotspot Map")
    
    if st.button(" Generate Hotspot Map", use_container_width=True):
        with st.spinner("Creating interactive map..."):
            try:
                # Create map
                hotspot_map = visualizer.create_cluster_map(df, st.session_state['algorithm'])
                
                # Display map
                st.components.v1.html(hotspot_map._repr_html_(), height=600)
                
                # Download clustered data
                st.markdown("###  Download Results")
                csv = df.to_csv(index=False)
                st.download_button(
                    label=" Download Clustered Data",
                    data=csv,
                    file_name="hotspot_analysis_results.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error creating map: {str(e)}")

else:
    # Instructions
    st.info("""
     **Click the 'Detect Hotspots' button above to start the analysis!**
    
    The algorithm will:
    - Analyze spatial patterns in your accident data
    - Identify high-density accident zones
    - Provide detailed statistics for each hotspot
    - Generate interactive visualizations
    """)

# Next steps
st.markdown("---")
st.markdown("""
<div style="text-align: center; background: #f8f9fa; padding: 20px; border-radius: 10px;">
    <h4>Next Steps</h4>
    <p>After detecting hotspots, explore them on interactive maps or analyze detailed insights!</p>
    <div style="margin-top: 15px;">
        <a href="/Interactive_Map" target="_self" style="
            background: linear-gradient(135deg, #45B7D1 0%, #96C93D 100%); 
            color: white; 
            padding: 10px 20px; 
            border-radius: 25px; 
            text-decoration: none; 
            font-weight: bold;
            margin: 5px;
            display: inline-block;
        ">View Interactive Map</a>
    </div>
</div>
""", unsafe_allow_html=True)