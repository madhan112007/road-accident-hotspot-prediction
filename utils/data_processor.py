import pandas as pd
import numpy as np
from datetime import datetime

class DataProcessor:
    def __init__(self):
        self.coimbatore_areas = {
            'Kovaipudur': (11.0014, 76.9627),
            'Gandhipuram': (11.0168, 76.9558),
            'Ukkadam': (10.9905, 76.9614),
            'Kuniyamuthur': (11.0189, 76.9565)
        }
    
    def load_data(self, file_path):
        """Load and preprocess accident data"""
        if hasattr(file_path, 'read'):
            # It's a file upload object
            df = pd.read_csv(file_path)
        else:
            # It's a file path
            df = pd.read_csv(file_path)
        
        # Convert Date_Time to datetime
        df['Date_Time'] = pd.to_datetime(df['Date_Time'])
        
        # Extract time features
        df['Hour'] = df['Date_Time'].dt.hour
        df['DayOfWeek'] = df['Date_Time'].dt.day_name()
        df['Month'] = df['Date_Time'].dt.month_name()
        
        return df
    
    def validate_coordinates(self, df):
        """Validate if coordinates are within India range"""
        valid_lat = (df['Latitude'] >= 8) & (df['Latitude'] <= 37)
        valid_lon = (df['Longitude'] >= 68) & (df['Longitude'] <= 97)
        return df[valid_lat & valid_lon]
    
    def get_area_name(self, lat, lon):
        """Get approximate area name for coordinates"""
        for area, (area_lat, area_lon) in self.coimbatore_areas.items():
            if abs(lat - area_lat) < 0.02 and abs(lon - area_lon) < 0.02:
                return area
        return "Other Area"
    
    def preprocess_for_clustering(self, df):
        """Prepare data for clustering algorithms"""
        # Select relevant features
        features = df[['Latitude', 'Longitude', 'Severity']].copy()
        
        # Normalize features
        features['Latitude'] = (features['Latitude'] - features['Latitude'].mean()) / features['Latitude'].std()
        features['Longitude'] = (features['Longitude'] - features['Longitude'].mean()) / features['Longitude'].std()
        features['Severity'] = (features['Severity'] - features['Severity'].mean()) / features['Severity'].std()
        
        return features.values