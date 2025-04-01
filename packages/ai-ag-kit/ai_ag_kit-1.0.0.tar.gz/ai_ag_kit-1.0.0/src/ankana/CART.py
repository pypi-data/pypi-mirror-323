#!/usr/bin/env python
# coding: utf-8

# # CART Algorithm

# In[ ]:


# Importing the libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.preprocessing import LabelEncoder

# Read the dataset
dataset = pd.read_csv('buycom.csv')

# Data Preprocessing
x = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

# Create a LabelEncoder object
label_encoder = LabelEncoder()

# Iterate through each column of x and encode if it contains strings
for i in range(x.shape[1]):
    if isinstance(x[0, i], str):  # Check if the column contains strings
        x[:, i] = label_encoder.fit_transform(x[:, i])

# Encode the target variable if it contains strings
if isinstance(y[0], str):
    y = label_encoder.fit_transform(y)

# Train-Test Split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# Train the classification Tree
clf = DecisionTreeClassifier(criterion='gini', random_state=42)
clf.fit(x_train, y_train)

# Feature names
feature_names = ['age', 'income', 'student', 'credit_rating']

# Get the unique values of the target variable
target_names = dataset['buys_computer'].unique()

# Make Predictions and Evaluate
y_pred = clf.predict(x_test)
print("Accuracy Score:", accuracy_score(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=target_names))

# Visualize the Decision Tree
plt.figure(figsize=(15,15))
tree.plot_tree(clf, feature_names=feature_names, class_names=target_names, filled=True)
plt.show()

