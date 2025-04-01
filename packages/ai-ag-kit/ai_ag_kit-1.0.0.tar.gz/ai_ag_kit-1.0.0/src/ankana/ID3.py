#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt
import math
from sklearn.preprocessing import LabelEncoder # import LabelEncoder

df = pd.read_csv('PlayTennis.csv')


def calculate_entropy(data, target_column): # for each categorical variable
	total_rows = len(data)
	target_values = data[target_column].unique()

	entropy = 0
	for value in target_values:
		# Calculate the proportion of instances with the current value
		value_count = len(data[data[target_column] == value])
		proportion = value_count / total_rows
		entropy -= proportion * math.log2(proportion) if proportion != 0 else 0

	return entropy

def calculate_information_gain(data, feature, target_column):

	# Calculate weighted average entropy for the feature
	unique_values = data[feature].unique()
	weighted_entropy = 0

	for value in unique_values:
		subset = data[data[feature] == value]
		proportion = len(subset) / len(data)
		weighted_entropy += proportion * calculate_entropy(subset, target_column)

	# Calculate information gain
	information_gain = entropy_outcome - weighted_entropy

	return information_gain

def id3(data, target_column, features):
	if len(data[target_column].unique()) == 1:
		return data[target_column].iloc[0]


	if len(features) == 0:
		return data[target_column].mode().iloc[0]

	best_feature = max(features, key=lambda x: calculate_information_gain(data, x, target_column))

	tree = {best_feature: {}}

	features = [f for f in features if f != best_feature]

	for value in data[best_feature].unique():
		subset = data[data[best_feature] == value]
		tree[best_feature][value] = id3(subset, target_column, features)

	return tree

entropy_outcome = calculate_entropy(df, 'play')
print(f"Entropy for 'play' column: {entropy_outcome:.3f}")

for column in df.columns[:-1]:
	entropy = calculate_entropy(df, column)
	information_gain = calculate_information_gain(df, column, 'play')
	print(f"{column} - Entropy: {entropy:.3f}, Information Gain: {information_gain:.3f}")


# Feature selection for the first step in making decision tree
selected_feature = 'outlook'

# Create a decision tree
clf = DecisionTreeClassifier(criterion='entropy', max_depth=1)

# Encode categorical features
le = LabelEncoder() # create a LabelEncoder object
df[selected_feature] = le.fit_transform(df[selected_feature]) # transform the selected_feature column

X = df[[selected_feature]]
y = df['play']
clf.fit(X, y)

# Plot the decision tree
plt.figure(figsize=(8, 6))
plot_tree(clf, feature_names=[selected_feature], class_names=['0', '1'], filled=True, rounded=True)
plt.show()

