import numpy as np
import pandas as pd
import click
import math

from typing import Union

def gini_index(df: pd.DataFrame, label: str, feature: str, class_list: Union[set, list]) -> float :
    """Method to find gini index of a feature in a dataset"""
    total_data = df.shape[0]

    feat_labels = df[feature].unique().tolist()
    feat_index = 0

    for feat_label in feat_labels :
        label_count = df[feature].value_counts()[feat_label].item()
        impurity = 1

        for c in class_list :
            label_class_count = df[df[feature] == feat_label][label].value_counts()
            label_class_count = label_class_count[c].item() if c in label_class_count.index else 0

            val = math.pow((label_class_count / label_count), 2)
            impurity -= val
        
        weighted_impurity = (label_count / total_data) * impurity
        feat_index += weighted_impurity

    return feat_index

def make_gini(df: pd.DataFrame, label: str, class_list: Union[set, list]) -> dict :
    tree = {}

    feat_gini_list = []
    for feat in df.columns :
        if feat == label :
            continue
        index_val = gini_index(df, label, feat, class_list)
        feat_gini_list.append(index_val)

    chosen_feature = df.columns[np.argmin(feat_gini_list)]
    tree[chosen_feature] = {}

    # Determine pure and impure class
    for feat in df[chosen_feature].unique() :
        class_set = df[df[chosen_feature] == feat][label].unique()
        if len(class_set) == 1:
            tree[chosen_feature][feat] = class_set[0]
        else :
            tree[chosen_feature][feat] = make_gini(df[df[chosen_feature] == feat], label, class_list)
    
    return tree

@click.command()
@click.option('--file', '-F', help='Absolute location of the dataset')
@click.option('--label', '-L', help='The output feature label of the dataset')
def main(file, label) :
    data = pd.read_csv(file)
    class_list = data[label].unique().tolist()

    tree = make_gini(data, label, class_list)

    from pprint import pp
    pp(tree, indent=4, width=1)

if __name__ == "__main__" :
    main()