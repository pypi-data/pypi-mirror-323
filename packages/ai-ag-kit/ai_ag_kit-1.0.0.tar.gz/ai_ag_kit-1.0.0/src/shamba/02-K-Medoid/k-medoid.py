import math

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


if __name__ == "__main__" :
    # Get the number of clusters
    k = int(input("Enter the number of clusters: "))

    # Import libraries
    import pathlib
    import pandas as pd
    import numpy as np

    # Constants
    DATASET_URI = f"{pathlib.Path().resolve()}\\..\\Dataset\\IRIS\\iris.data"
    DATASET_HEADERS = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'type']
    FLOWER_TYPES = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']

    # Open dataset file and read it using pandas
    datasetFile = open(DATASET_URI)
    dataFrame = pd.read_csv(datasetFile, header=None, names=DATASET_HEADERS)
    datasetFile.close()
    del datasetFile

    # Choose random data rows as initial clusters
    data_amount = dataFrame.shape[0]

    import random
    cluster_indices = random.sample(range(data_amount), k)
    cluster_rows = [dataFrame.loc[x] for x in cluster_indices]
    cluster_dict = {}
    cluster_dict0 = {}
    cluster_dict_df = {}
    for cluster in cluster_rows :
        cluster_dict[cluster.name] = []

    # Perform clustering
    i = 0 # Number of iterations
    while True :
        i += 1
        for index, row in dataFrame.iterrows() :
            cluster_distance = np.array([
                euclid_distance(
                    [row['sepal_length'], row['sepal_width'], row['petal_length'], row['petal_width']],
                    [cluster['sepal_length'], cluster['sepal_width'], cluster['petal_length'], cluster['petal_width']]
                    )
                    for cluster in cluster_rows
                ])

            chosen_cluster = cluster_rows[np.argmin(cluster_distance)]
            cluster_dict[chosen_cluster.name].append(row)

        for key, value in cluster_dict.items():
            data = pd.DataFrame(value)
            cluster_dict_df[key] = data

        flag = True
        if len(cluster_dict0.items()) > 0 :
            for (k, v), (k2, v2) in zip(cluster_dict.items(), cluster_dict0.items()) :
                if v != v2 :
                    flag = False
        else :
            flag = False

        if flag :
            print(f"Iterations: {i}")
            break
        else :
            cluster_dict0 = cluster_dict
            cluster_dict.clear()

            new_cluster_rows = []

            for cluster in cluster_rows:
                cluster[DATASET_HEADERS[0]] = cluster_dict_df[cluster.name].mean(numeric_only=True)[DATASET_HEADERS[0]]
                cluster[DATASET_HEADERS[1]] = cluster_dict_df[cluster.name].mean(numeric_only=True)[DATASET_HEADERS[1]]
                cluster[DATASET_HEADERS[2]] = cluster_dict_df[cluster.name].mean(numeric_only=True)[DATASET_HEADERS[2]]
                cluster[DATASET_HEADERS[3]] = cluster_dict_df[cluster.name].mean(numeric_only=True)[DATASET_HEADERS[3]]

                cluster_distance = np.array([
                    euclid_distance(
                        [row['sepal_length'], row['sepal_width'], row['petal_length'], row['petal_width']],
                        [cluster['sepal_length'], cluster['sepal_width'], cluster['petal_length'], cluster['petal_width']]
                        )
                        for index, row in dataFrame.iterrows()
                    ])
                
                chosen_cluster = dataFrame.loc[np.argmin(cluster_distance)]
                new_cluster_rows.append(chosen_cluster)

                cluster_dict[chosen_cluster.name] = []
            
            cluster_dict_df.clear()
            cluster_rows.clear()
            cluster_rows.extend(new_cluster_rows)

    # Plot data
    x_labels = [f'Cluster{x}' for x in range(len(cluster_rows))]

    y1 = np.array([df.value_counts('type')[FLOWER_TYPES[0]].item() if FLOWER_TYPES[0] in df.value_counts('type') else 0 for df in cluster_dict_df.values()])
    y2 = np.array([df.value_counts('type')[FLOWER_TYPES[1]].item() if FLOWER_TYPES[1] in df.value_counts('type') else 0 for df in cluster_dict_df.values()])
    y3 = np.array([df.value_counts('type')[FLOWER_TYPES[2]].item() if FLOWER_TYPES[2] in df.value_counts('type') else 0 for df in cluster_dict_df.values()])

    import matplotlib.pyplot as plt

    plt.bar(x_labels, y1, color='r')
    plt.bar(x_labels, y2, bottom=y1, color='g')
    plt.bar(x_labels, y3, bottom=y1+y2, color='b')

    plt.xlabel("Clusters")
    plt.ylabel("Count")

    plt.legend(FLOWER_TYPES, loc="right", bbox_to_anchor=(1.1, 0.5), framealpha=0.5, fancybox=True)
    plt.title("K-Means Clustering in IRIS dataset")
    plt.show()