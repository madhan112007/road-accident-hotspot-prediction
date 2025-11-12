import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

class HotspotModel:
    def __init__(self):
        self.dbscan = DBSCAN(eps=0.01, min_samples=3)
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
    
    def detect_hotspots_dbscan(self, coordinates):
        """Detect hotspots using DBSCAN clustering"""
        try:
            coords_scaled = self.scaler.fit_transform(coordinates)
            clusters = self.dbscan.fit_predict(coords_scaled)
            return clusters
        except Exception as e:
            print(f"DBSCAN Error: {e}")
            return np.zeros(len(coordinates))
    
    def detect_hotspots_kmeans(self, coordinates, n_clusters=5):
        """Detect hotspots using K-Means clustering"""
        try:
            self.kmeans.n_clusters = n_clusters
            coords_scaled = self.scaler.fit_transform(coordinates)
            clusters = self.kmeans.fit_predict(coords_scaled)
            return clusters, self.kmeans.cluster_centers_
        except Exception as e:
            print(f"K-Means Error: {e}")
            return np.zeros(len(coordinates)), None
    
    def evaluate_clustering(self, coordinates, clusters):
        """Evaluate clustering quality using silhouette score"""
        if len(set(clusters)) > 1 and -1 not in clusters:
            return silhouette_score(coordinates, clusters)
        elif len(set(clusters)) > 2:  # DBSCAN with noise
            valid_points = clusters != -1
            if sum(valid_points) > 1 and len(set(clusters[valid_points])) > 1:
                return silhouette_score(coordinates[valid_points], clusters[valid_points])
        return 0.0