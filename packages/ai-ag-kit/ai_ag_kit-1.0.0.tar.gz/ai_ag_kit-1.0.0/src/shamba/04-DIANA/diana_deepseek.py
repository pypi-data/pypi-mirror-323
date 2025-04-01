import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
import pathlib
from tqdm import tqdm  # Import tqdm for progress bar

def diana_clustering(data, max_clusters=None):
    def split_cluster(cluster):
        if len(cluster) <= 1:
            return [cluster]
        
        # Calculate the average distance of each point to all other points in the cluster
        distances = squareform(pdist(data[cluster]))
        avg_distances = np.mean(distances, axis=1)
        
        # Select the point with the highest average distance as the new cluster center
        new_center_idx = np.argmax(avg_distances)
        new_center = cluster[new_center_idx]
        
        # Split the cluster into two based on the distance to the new center
        distances_to_center = np.linalg.norm(data[cluster] - data[new_center], axis=1)
        median_distance = np.median(distances_to_center)
        
        cluster1 = cluster[distances_to_center <= median_distance]
        cluster2 = cluster[distances_to_center > median_distance]
        
        return [cluster1, cluster2]
    
    # Initialize with all data points in one cluster (using IDs)
    clusters = [np.arange(len(data))]
    
    # Use tqdm to show progress for epochs
    with tqdm(total=max_clusters - 1, desc="Clustering Progress") as pbar:
        while True:
            if max_clusters and len(clusters) >= max_clusters:
                break
            
            # Find the cluster with the largest diameter to split
            max_diameter = -1
            cluster_to_split = None
            for cluster in clusters:
                if len(cluster) > 1:
                    diameter = np.max(pdist(data[cluster]))
                    if diameter > max_diameter:
                        max_diameter = diameter
                        cluster_to_split = cluster
            
            if cluster_to_split is None:
                break
            
            # Remove the cluster to split using list comprehension
            clusters = [c for c in clusters if not np.array_equal(c, cluster_to_split)]
            
            # Split the cluster
            new_clusters = split_cluster(cluster_to_split)
            clusters.extend(new_clusters)
            
            # Update the progress bar
            pbar.update(1)
    
    return clusters

# Load IRIS dataset
DATASET_URI = f"{pathlib.Path().resolve()}\\..\\Dataset\\IRIS\\iris.data"
DATASET_HEADERS = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'type']

# Open dataset file and read it using pandas
datasetFile = open(DATASET_URI)
dataFrame = pd.read_csv(datasetFile, header=None, names=DATASET_HEADERS)
dataFrame = dataFrame.drop(columns=['type'])
dataset_np = dataFrame.to_numpy()

# Perform DIANA clustering
max_clusters = 3  # Set the maximum number of clusters
final_clusters = diana_clustering(dataset_np, max_clusters=max_clusters)

# Print final clusters with IDs
print("\nFinal Clusters (IDs):")
for i, cluster in enumerate(final_clusters):
    print(f"Cluster {i+1}: {cluster + 1}")  # Adding 1 to match ID starting from 1