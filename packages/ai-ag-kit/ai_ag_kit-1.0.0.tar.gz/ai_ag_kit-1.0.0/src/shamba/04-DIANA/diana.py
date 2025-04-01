import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.cluster.hierarchy import dendrogram
from split import SplittingClustering

def plot_dendrogram(model: SplittingClustering, **kwargs):
    """
    Plots the dendrogram for the given SplittingClustering model.

    Parameters
    ----------
    model : SplittingClustering
        The fitted SplittingClustering model.
    kwargs : dict
        Additional arguments to pass to the dendrogram function.
    """
    # Create linkage matrix
    counts = np.zeros(model.labels_.shape)
    n_samples = len(model.labels_)
    linkage_matrix = np.column_stack([model.labels_, np.arange(n_samples), counts, np.zeros(n_samples)]).astype(float)

    # Plot the dendrogram
    dendrogram(linkage_matrix, **kwargs)
    plt.xlabel("Sample index")
    plt.ylabel("Cluster distance")
    plt.show()

def main() :
    import pathlib

    # Constants
    DATASET_URI = f"{pathlib.Path().resolve()}\\..\\Dataset\\IRIS\\iris.data"
    DATASET_HEADERS = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'type']

    # Open dataset file and read it using pandas
    datasetFile = open(DATASET_URI)
    dataFrame = pd.read_csv(datasetFile, header=None, names=DATASET_HEADERS)
    dataFrame = dataFrame.drop(columns=['type'])
    # dataFrame["id"] = (dataFrame.index + 1).astype(int)
    dataset_np = dataFrame.to_numpy()
    datasetFile.close()
    del datasetFile

    model = SplittingClustering(n_clusters=2)
    model = model.fit(dataset_np)

if __name__ == '__main__' :
    main()