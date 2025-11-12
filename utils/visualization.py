import folium
from folium.plugins import HeatMap
import pandas as pd
import numpy as np

class MapVisualizer:
    def __init__(self):
        self.coimbatore_center = [11.0168, 76.9558]  # Gandhipuram as center
    
    def create_cluster_map(self, df, algorithm=None):
        """Create a map showing accident clusters"""
        m = folium.Map(location=self.coimbatore_center, zoom_start=12)
        
        # Check if Cluster column exists
        if 'Cluster' not in df.columns:
            # Create simple clusters based on location
            try:
                from sklearn.cluster import KMeans
                coords = df[['Latitude', 'Longitude']].values
                n_clusters = min(5, len(df))
                if n_clusters > 1:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    df = df.copy()
                    df['Cluster'] = kmeans.fit_predict(coords)
                else:
                    # If only one point, assign to cluster 0
                    df = df.copy()
                    df['Cluster'] = 0
            except Exception as e:
                st.warning(f"Could not create clusters: {e}. Using point map instead.")
                return self.create_point_map(df)
        
        # Color scheme for clusters
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige']
        
        # Add clusters to map
        for cluster_id in df['Cluster'].unique():
            cluster_data = df[df['Cluster'] == cluster_id]
            color = colors[cluster_id % len(colors)]
            
            for _, row in cluster_data.iterrows():
                popup_text = f"""
                <b>Cluster {cluster_id}</b><br>
                Severity: {row['Severity']}<br>
                Vehicles: {row['Vehicles_Involved']}<br>
                Weather: {row['Weather']}<br>
                Road: {row['Road_Type']}
                """
                
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=8,
                    popup=folium.Popup(popup_text, max_width=300),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.6,
                    weight=2
                ).add_to(m)
        
        return m
    
    def create_heat_map(self, df, radius=15):
        """Create a heat map of accident density"""
        m = folium.Map(location=self.coimbatore_center, zoom_start=12)
        
        # Prepare heat data
        heat_data = [[row['Latitude'], row['Longitude']] for _, row in df.iterrows()]
        
        # Add heat map
        if heat_data:
            HeatMap(heat_data, radius=radius).add_to(m)
        
        return m
    
    def create_point_map(self, df, point_size=6, opacity=0.7):
        """Create a map with individual accident points"""
        m = folium.Map(location=self.coimbatore_center, zoom_start=12)
        
        # Color by severity
        severity_colors = {
            1: 'green',
            2: 'yellow', 
            3: 'orange',
            4: 'red'
        }
        
        for _, row in df.iterrows():
            color = severity_colors.get(row['Severity'], 'gray')
            
            popup_text = f"""
            <b>Accident Details</b><br>
            Severity: {row['Severity']}<br>
            Weather: {row['Weather']}<br>
            Road: {row['Road_Type']}<br>
            Vehicles: {row['Vehicles_Involved']}
            """
            
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=point_size,
                popup=folium.Popup(popup_text, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=opacity,
                weight=1
            ).add_to(m)
        
        return m
    
    def get_map_bounds(self, df):
        """Get map bounds to fit all data"""
        if len(df) == 0:
            return [[10.9, 76.9], [11.1, 77.0]]
        
        min_lat = df['Latitude'].min()
        max_lat = df['Latitude'].max() 
        min_lon = df['Longitude'].min()
        max_lon = df['Longitude'].max()
        
        # Add padding
        lat_padding = (max_lat - min_lat) * 0.1
        lon_padding = (max_lon - min_lon) * 0.1
        
        return [
            [min_lat - lat_padding, min_lon - lon_padding],
            [max_lat + lat_padding, max_lon + lon_padding]
        ]