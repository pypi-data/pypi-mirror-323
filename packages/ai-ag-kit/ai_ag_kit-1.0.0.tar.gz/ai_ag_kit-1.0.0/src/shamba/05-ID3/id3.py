import numpy as np
import pandas as pd
import click

from typing import Union

def dataset_entropy(df: pd.DataFrame, label: str, class_list: Union[set, list]) -> float :
    """Method to calculate the entropy for the whole dataset

    Args
        df:
            The training dataframe
        label:
            The class label
    Returns
        entropy for the dataset
    """

    total_data = df.shape[0]
    entropy = 0.0

    for c in class_list :
        total_class_count = df[label].value_counts()
        if c not in total_class_count.index :
                continue
        total_class_count = total_class_count[c].item()
        class_prob = total_class_count / total_data
        class_entropy = - (class_prob) * np.log2(class_prob)
        entropy += class_entropy

    return entropy

def calc_feature_entropy(df: pd.DataFrame, output_label: str, feature_label: str, class_list: Union[set, list]) -> float :
    """Method to calculate entropy for a specific feature"""

    total_data = df.shape[0]
    feature_classes = df[feature_label].unique().tolist()
    feature_entropy = 0

    for label_class in feature_classes :
        total_count = df[feature_label].value_counts()[label_class].item()
        local_entropy = 0

        for c in class_list :
            class_count = df[df[feature_label] == label_class][output_label].value_counts()
            if c not in class_count.index :
                continue
            class_count = class_count[c].item()
            prob = class_count / total_count
            entropy = - (prob) * np.log2(prob)
            local_entropy += entropy

        entropy = (total_count / total_data) * local_entropy
        feature_entropy += entropy

    return feature_entropy

def make_id3(df: pd.DataFrame, label: str, class_list: Union[set, list]) -> dict :
    df_entropy = dataset_entropy(df, label, class_list)
    tree = {}

    feat_ent_list = []
    for feature in df.columns :
        if feature == label :
            continue
        feat_ent = calc_feature_entropy(df, label, feature, class_list)
        feat_ent_list.append(feat_ent)
    
    # gain calculation
    gain_list = np.subtract(df_entropy, feat_ent_list)
    chosen_feature = df.columns[np.argmax(gain_list)]
    tree[chosen_feature] = {}

    # Determine pure and impure class
    for feat in df[chosen_feature].unique() :
        class_set = df[df[chosen_feature] == feat][label].unique()
        if len(class_set) == 1:
            tree[chosen_feature][feat] = class_set[0]
        else :
            tree[chosen_feature][feat] = make_id3(df[df[chosen_feature] == feat], label, class_list)
    
    return tree


@click.command()
@click.option('--file', '-F', help='Absolute location of the dataset')
@click.option('--label', '-L', help='The output feature label of the dataset')
def main(file, label) :
    data = pd.read_csv(file)
    class_list = data[label].unique().tolist()

    tree = make_id3(data, label, class_list)

    from pprint import pp
    pp(tree, indent=4, width=1)

if __name__ == "__main__" :
    main()