import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import click

from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering

def plot_dendrogram(model : AgglomerativeClustering, **kwargs) :
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)

    for i, merge in enumerate(model.children_) :
        current_count = 0
        for child_idx in merge :
            if child_idx < n_samples :
                current_count += 1
            else :
                current_count += counts[child_idx - n_samples]
        
        counts[i] = current_count
    
    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    dendrogram(linkage_matrix, **kwargs)

@click.command()
@click.option('--linkage', '-L', type=click.Choice(['single', 'average', 'complete'], case_sensitive=False), help='Linkage type')
def main(linkage : str) :
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

    model = AgglomerativeClustering(distance_threshold=0, n_clusters=None, linkage=linkage.strip().lower())
    model = model.fit(dataset_np)

    plt.title("AGNES")
    plot_dendrogram(model)
    plt.xlabel("Number of points or index")
    plt.show()

if __name__ == '__main__' :
    main()