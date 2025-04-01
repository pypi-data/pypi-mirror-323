import numpy as np
import pandas as pd
import click

@click.command()
@click.option('--file', '-F', help="Absolute location of the dataset")
@click.option('--label', '-L', help="Output label of the dataset")
def main(file, label) :
    df = pd.read_csv(file)
    class_list = df[label].unique().tolist()
    total_data = df.shape[0]

    feats = df.columns
    input_labels = {}
    print("Enter data to predict (case sensitive): ")
    for feat in feats:
        if feat == label :
            continue
        feat_labels = df[feat].unique().tolist()
        while True:
            input_label = input(f"{feat}[{'/'.join(feat_labels)}]: ")
            if input_label not in feat_labels :
                print("Unkown label, Enter again!")
                continue
            input_labels[feat] = input_label
            break

    all_class_prob = []

    for c in class_list :
        class_count = df[label].value_counts()[c].item()
        class_prob = class_count / total_data

        class_bayes_prob = 1

        # label probabilities
        for k, v in input_labels.items() :
            feat_class_count = df[df[k] == v][label].value_counts()
            feat_class_count = feat_class_count[c].item() if c in feat_class_count.index else 0
            feat_class_prob = feat_class_count / class_count
            class_bayes_prob *= feat_class_prob

        classify_prob = class_prob * class_bayes_prob
        all_class_prob.append(classify_prob)
    
    print("All probabilities: ")
    for k,v in zip(class_list, all_class_prob) :
        print(f'{k}: {v}')

    print(f"Result class: {class_list[np.argmax(all_class_prob)]}")


if __name__ == "__main__" :
    main()    