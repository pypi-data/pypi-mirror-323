#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Aglomerative Clustering using single, complete and average linkage

# Import Libraries
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt

# Read the dataset
ds = pd.read_csv('iris.csv')

# Drop lablelled features
filtered_data = ds.drop(['species'], axis=1)

# Aglomertive Clustering using Single Linkage
single_clustering = linkage(filtered_data, method="single", metric="euclidean")

# Aglomertive Clustering using Complete Linkage
complete_clustering = linkage(filtered_data, method="complete", metric="euclidean")

# Aglomertive Clustering using Average Linkage
average_clustering = linkage(filtered_data, method="average", metric="euclidean")

# Craeting a subplot with 1 row and 3 columns
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Plot the dendrogram for each linkage method
dendrogram(single_clustering, ax=axes[0])
axes[0].set_title('Single Linkage')

dendrogram(complete_clustering, ax=axes[1])
axes[1].set_title('Complete Linkage')

dendrogram(average_clustering, ax=axes[2])
axes[2].set_title('Average Linkage')

# Labelling x-axis and y-axis for each dendrogram
for ax in axes.flat:
    ax.set(xlabel='Object', ylabel='Lifetime')

# Display the plots
plt.show()

