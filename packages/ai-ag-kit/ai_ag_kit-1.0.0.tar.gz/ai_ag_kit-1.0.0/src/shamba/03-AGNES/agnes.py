# create cluster class
# Cluster class has attribute to store the data in the cluster
# The data is stored in the cluster in an array.
# Define a method to find out distance between two clusters
# Method has argument for single linkage distance, average linkage, complete linkage
# Define all the starting data points as clusters with just a single data.
# Create distance matrices for the clusters and find out the minimum distance between the clusters.
# Merge closest clusters iteratively (or maybe recursively)
# Continue until only 1 cluster is left.

import numpy as np
import math
from itertools import product

class Cluster :
    def __init__(self, data : np.ndarray) -> None:
        self.points = []
        self.points.append(data)
    
    def add(self, data) -> None :
        self.points.append(data)

    def __str__(self) -> str:
        return_str = ""
        for i in range(len(self.points)) :
            if i == 0:
                return_str += "("
            else :
                return_str += ","
            
            if type(self.points[i]) == np.ndarray :
                return_str += str(self.points[i][-1].item())
            else :
                return_str += str(self.points[i])
        return_str += ")"
            
        return return_str
        

def euclid_distance(pointA, pointB) -> float :
    """A method to calculate the euclidean distance between two points

    Parameters
    ----------
    pointA : Any
        The first point
    pointB : Any
        The second point

    Returns
    -------
    float
        The euclidean distance between the points
    """

    sqDistance = 0.0

    for i in range(len(pointA)) :
        sqDistance += pow(pointA[i] - pointB[i], 2)

    distance = math.sqrt(sqDistance)
    return distance

def distance_cluster(cluster_A : Cluster, cluster_B : Cluster, type_link : str) -> float :
    """
    Method to calculate distance between two clusters based on the distance type
    Single linkage, Average linkage, Complete linkage
    """

    type_link = type_link.strip().lower()

    def ret_points(x : Cluster, ret_list : list) -> list :
        for data_point in x.points :
            if type(data_point) == np.ndarray :
                ret_list.append(data_point)
            elif type(data_point) == Cluster :
                ret_list = ret_points(data_point, ret_list)
        
        return ret_list

    cluster_A_Points = []
    cluster_A_Points = ret_points(cluster_A, cluster_A_Points)        
    cluster_A_pts_np = np.array(cluster_A_Points)

    cluster_B_Points = []
    cluster_B_Points = ret_points(cluster_B, cluster_B_Points)   
    cluster_B_pts_np = np.array(cluster_B_Points)

    del cluster_A_Points
    del cluster_B_Points

    cross_matrix = np.array(list(product(cluster_A_pts_np, cluster_B_pts_np)))
    distance_list = []

    # def cross_iter(x : np.ndarray) :
    #     print(x)
    #     # Distance without last column as that the id
    #     distance = euclid_distance(x[0][:-1], x[1][:-1])
    #     distance_list.append(distance)
        
    # np.apply_along_axis(cross_iter, 2, cross_matrix)

    for row in cross_matrix :
        distance = euclid_distance(row[0][:-1], row[1][:-1])
        distance_list.append(distance)

    if type_link == "single" :
        # Single linkage, minimum distance between two clusters        
        return np.amin(distance_list).item()
    
    elif type_link == "average" :
        # Average linkage, average of all distances
        return np.mean(distance_list).item()
    
    elif type_link == "complete" :
        # Complete linkage, max distance
        return np.amax(distance_list).item()
    

if __name__ == "__main__" :

    # Import libraries
    import pathlib
    import pandas as pd
    from tqdm import tqdm, trange

    # Constants
    DATASET_URI = f"{pathlib.Path().resolve()}\\..\\Dataset\\IRIS\\iris.data"
    DATASET_HEADERS = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'type']

    # Open dataset file and read it using pandas
    datasetFile = open(DATASET_URI)
    dataFrame = pd.read_csv(datasetFile, header=None, names=DATASET_HEADERS)
    dataFrame = dataFrame.drop(columns=['type'])
    dataFrame["id"] = (dataFrame.index + 1).astype(int)
    dataset_np = dataFrame.to_numpy()
    datasetFile.close()
    del datasetFile

    # Creating initial clusters
    print("Creating initial cluster")
    cluster_list = []
    for row in tqdm(dataset_np) :
        cluster = Cluster(row)
        cluster_list.append(cluster)

    epoch = 0
    while len(cluster_list) > 1 :
        cluster_matrix = list(product(cluster_list, cluster_list))
        epoch += 1

        print(f"Epoch:{epoch}")

        distance_matrix = []
        m = len(cluster_list)
        n = 1

        for i in trange(len(cluster_list)) :
            for j in range(i + 1, len(cluster_list)) :
                filtered_index = i * len(cluster_list) + j
                
                # distance_row = distance_cluster(cluster_matrix[filtered_index][0], cluster_matrix[filtered_index][1], 'single')
                # distance_row = distance_cluster(cluster_matrix[filtered_index][0], cluster_matrix[filtered_index][1], 'average')
                distance_row = distance_cluster(cluster_matrix[filtered_index][0], cluster_matrix[filtered_index][1], 'complete')

                distance_matrix.append(distance_row)
        
        distance_matrix_np = np.array(distance_matrix)
        del distance_matrix
        index = np.argmin(distance_matrix_np)

        cluster_matrix[index][0].add(cluster_matrix[index][1])
        pop_index = index - ((index // len(cluster_list)) * len(cluster_list))
        cluster_list.pop(pop_index)

    print("Result\n--------------------")
    print(cluster_list[0])