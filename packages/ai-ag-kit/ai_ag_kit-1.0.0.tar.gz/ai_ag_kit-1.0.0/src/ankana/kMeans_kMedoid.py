#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# K-means clustering

# import the libraries
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

# read the dataset
ds = pd.read_csv('iris.csv')

# drop the species column
x = ds.drop('species', axis=1)

# select no. of clusters
k = 3

#select k no. of random centroids
centroids = x.sample(n=k)

#iterate all entries and find their respective distances from each centroid
def find_distance(x, centroids):
  cluster = {}
  for i in range(len(x)):
    distances = euclidean_distances(x.iloc[[i]], centroids)
    min_distance_index = np.argmin(distances)
    centroid_key = tuple(centroids.iloc[min_distance_index])
    if centroid_key not in cluster:
      cluster[centroid_key] = []
    cluster[centroid_key].append(x.iloc[i].values.tolist())
  return cluster

# Calculate new centroids
def calculate_new_centroids(cluster, x):
  centroid_values = []
  for centroid, points in cluster.items():
    if points:
      centroid_values.append(np.mean(points, axis=0))
    else:
      centroid_values.append(np.array(centroid))
  return pd.DataFrame(centroid_values, columns=x.columns)

# Apply K-means algorithm
def k_means(x, k):
  centroids = x.sample(n=k)
  cluster = {}
  while True:
    cluster_new = find_distance(x, centroids)
    if cluster == cluster_new:
      break
    cluster = cluster_new
    centroids = calculate_new_centroids(cluster, x)
  return cluster


cluster = k_means(x, k)

print("The clusters are :")
for i,(centroid, points) in enumerate(cluster.items()):
  print(f"Centroid {i+1}: {centroid}, Points: {points}")

#Plotting into Scatter Plot
colors = ['deeppink', 'maroon', 'blue']

for i, (centroid, points) in enumerate(cluster.items()):
  df = pd.DataFrame(points, columns = x.columns)
  plt.scatter(df[x.columns[0]], df[x.columns[2]], c=colors[i], label=f'Cluster {i+1}')

plt.xlabel(x.columns[0])
plt.ylabel(x.columns[2])
plt.legend()
plt.show()

#Plotting into Bar graph
cluster_counts = [len(cluster[key]) for key in cluster]

# Create a bar graph
plt.bar(range(len(cluster)), cluster_counts, 0.4, color='deeppink')

# Set labels and title
plt.xlabel('Cluster')
plt.ylabel('Number of Points')
plt.title('Number of Points in Each Cluster')

# Show the plot
plt.show()


# In[ ]:


# K-medoid Clustering

# import the libraries
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

# read the dataset
ds = pd.read_csv('iris.csv')

# drop the species column
x = ds.drop('species', axis=1)

# select no. of clusters
k = 3

#select k no. of random centroids
centroids = x.sample(n=k)

#iterate all entries and find their respective distances from each centroid
def find_distance(x, medoids):
  cluster = {}
  for i in range(len(x)):
    distances = euclidean_distances(x.iloc[[i]], medoids)
    min_distance_index = np.argmin(distances)
    medoid_key = tuple(medoids.iloc[min_distance_index])
    if medoid_key not in cluster:
      cluster[medoid_key] = []
    cluster[medoid_key].append(x.iloc[i].values.tolist())
  return cluster

# Calculate new medoids
def calculate_new_medoids(cluster, x):
  medoid_values = []
  for centroid, points in cluster.items():
    centroid = np.array(centroid)
    distances = euclidean_distances(x, [centroid])
    min_distance_index = np.argmin(distances)
    medoid_values.append(x.iloc[min_distance_index])
  return pd.DataFrame(medoid_values, columns=x.columns)

# Implement K-medoid algorithm
def k_medoid(x, k):
  centroids = x.sample(n=k)
  medoid_values = []
  for centroid in centroids.values:
    centroid = np.array(centroid)
    distances = euclidean_distances(x, [centroid])
    min_distance_index = np.argmin(distances)
    medoid_values.append(x.iloc[min_distance_index])
  medoids = pd.DataFrame(medoid_values, columns=x.columns)

  cluster = {}
  while True:
    cluster_new = find_distance(x, medoids)
    if cluster == cluster_new:
      break
    cluster = cluster_new
    centroids = calculate_new_medoids(cluster, x)
  return cluster


cluster = k_medoid(x, k)

print("The clusters are :")
for i,(centroid, points) in enumerate(cluster.items()):
  print(f"Medoid {i+1}: {centroid}, Points: {points}")

#Plotting into Graph
colors = ['red', 'green', 'blue']

for i, (centroid, points) in enumerate(cluster.items()):
  df = pd.DataFrame(points, columns = x.columns)
  plt.scatter(df[x.columns[0]], df[x.columns[2]], c=colors[i], label=f'Cluster {i+1}')

plt.xlabel(x.columns[0])
plt.ylabel(x.columns[2])
plt.legend()
plt.show()

#Plotting into Bar graph
cluster_counts = [len(cluster[key]) for key in cluster]

# Create a bar graph
plt.bar(range(len(cluster)), cluster_counts, 0.4, color='magenta')

# Set labels and title
plt.xlabel('Cluster')
plt.ylabel('Number of Points')
plt.title('Number of Points in Each Cluster')

# Show the plot
plt.show()

