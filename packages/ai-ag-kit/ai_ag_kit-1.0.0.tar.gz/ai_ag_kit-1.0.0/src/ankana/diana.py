import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
import pathlib
from tqdm import tqdm

def diana(data: np.ndarray, max_clusters : int=3) :
    distance_matrix = squareform(pdist(data))

    clusters = [np.arange(data.shape[0], dtype=np.uint16)]

    counter = 0
    while len(clusters) < max_clusters :
        counter += 1
        print(f"Iteration: {counter}")

        cluster_sizes = [True if c.shape[0] <= 1 else False for c in clusters]
        if all(cluster_sizes) :
            break

        can_divide = True

        # Find diameter
        diameter_list = []
        for cluster in clusters :
            diameter_indv_list = []
            if len(cluster) == 1 :
                diameter_indv_list.append(-99)
            for point_a in cluster :
                for point_b in cluster :
                    if point_a == point_b :
                        continue

                    diameter_indv_list.append(distance_matrix[point_a][point_b])
            diameter_list.append(diameter_indv_list[np.argmax(diameter_indv_list)])

        chosen_cluster_idx = np.argmax(diameter_list)

        C_i = clusters.pop(chosen_cluster_idx)
        C_j = np.array([], dtype=np.uint16)

        while can_divide :
            # Calculate dissimilarity
            dis_list = []
            for point_a in C_i :
                dis_total_a = 0
                if len(C_i) > 1 :
                    dis_factor_a = 1 / (len(C_i)-1)
                    for point_b in C_i :
                        if point_a == point_b :
                            continue

                        dis_total_a += distance_matrix[point_a][point_b]
                    dis_total_a = dis_factor_a * dis_total_a
                
                dis_total_b = 0
                if len(C_j) > 0 :
                    dis_factor_b = 1 / len(C_j)
                    for point_b in C_j :
                        if point_a == point_b :
                            continue

                        dis_total_b += distance_matrix[point_a][point_b]
                    dis_total_b = dis_factor_b * dis_total_b

                dissimilarity = dis_total_a - dis_total_b
                dis_list.append(dissimilarity)
            
            chosen_point_idx = np.argmax(dis_list)
            if dis_list[chosen_point_idx] < 0 :
                can_divide = False
                break

            C_j = np.append(C_j, C_i[chosen_point_idx])
            C_i = np.delete(C_i, chosen_point_idx)

        clusters.append(C_j)
        clusters.append(C_i)

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
final_clusters = diana(dataset_np, max_clusters=max_clusters)

# Print final clusters with IDs
print("\nFinal Clusters (IDs):")
for i, cluster in enumerate(final_clusters):
    print(f"Cluster {i+1}: {cluster}")