#!/usr/bin/env python
# coding: utf-8

# # Fuzzy c-means clustering

# In[ ]:


get_ipython().system('pip install scikit-fuzzy')


# In[ ]:


# Import the libraries
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the Dataset
data = pd.read_csv('iris.csv')

# Data Preprocessing
x = data.iloc[:, :-1].values

# Define the number of clusters
n_clusters = 3

# Apply fuzzy c-means clustering
cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
	x.T, n_clusters, 2, error=0.005, maxiter=1000, init=None
)

# Predict cluster membership for each data point
cluster_membership = np.argmax(u, axis=0)

# Print the cluster centers
print('Cluster Centers:', cntr)

# Print the cluster membership for each data point
print('Cluster Membership:', cluster_membership)

# Visualization
plt.figure(figsize=(8, 6))
plt.scatter(data['sepal_length'], data['sepal_width'], c=cluster_membership, cmap='viridis')
plt.xlabel('Sepal Length (cm)')
plt.ylabel('Sepal Width (cm)')
plt.title('Fuzzy C-Means Clustering of Iris Dataset')
plt.colorbar(label='Cluster')
plt.show()

