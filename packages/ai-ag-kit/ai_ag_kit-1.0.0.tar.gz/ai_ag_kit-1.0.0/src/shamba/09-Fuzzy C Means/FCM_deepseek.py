import pandas as pd
import numpy as np
import skfuzzy as fuzz
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load the Boston Housing dataset
df = pd.read_csv("F:\College Crap\AI\CU-MSC-AI-SEM3\Dataset\HousingData.csv")

# Standardize the data (important for clustering)
scaler = StandardScaler()
data_std = scaler.fit_transform(df)

# Define the number of clusters
n_clusters = 3

# Perform Fuzzy C-Means clustering
cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
    data_std.T, n_clusters, 2, error=0.005, maxiter=1000, init=None
)

# Predict cluster membership for each data point
cluster_membership = np.argmax(u, axis=0)

# Add the cluster membership to the original dataframe
df['Cluster'] = cluster_membership

# Print the first few rows of the dataframe with cluster assignments
print(df.head())

# Plot the clusters (for 2D visualization, using the first two features)
plt.scatter(data_std[:, 0], data_std[:, 1], c=cluster_membership, cmap='viridis')
plt.title('Fuzzy C-Means Clustering on Boston Housing Dataset')
plt.xlabel('CRIM')
plt.ylabel('ZN')
plt.show()

# Print the Fuzzy Partition Coefficient (FPC)
print(f"Fuzzy Partition Coefficient (FPC): {fpc:.3f}")