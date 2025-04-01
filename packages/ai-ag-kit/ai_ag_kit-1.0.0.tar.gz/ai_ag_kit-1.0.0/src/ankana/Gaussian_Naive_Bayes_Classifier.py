#!/usr/bin/env python
# coding: utf-8

# # **Gaussian Naive Bayesian Classifier**

# In[ ]:


# Import the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score

# Read the dataset
dataset = pd.read_csv('PlayTennis.csv')

# Data Preprocessing
x = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

# Fit and transform the categorical features
label_encoders = {}
for i in range(x.shape[1]): # Iterate through all columns of x
    label_encoders[i] = LabelEncoder()
    x[:, i] = label_encoders[i].fit_transform(x[:, i]) # Fit and transform the column

# Train-Test split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=11)

# Training into Gaussian-Naive Based Model
nb = GaussianNB()
nb.fit(x_train, y_train)

print("Naive Bayes score: ",nb.score(x_test, y_test))

# Assume 'unknown_sample'
unknown_sample1 = ['sunny','hot','high','true']
unknown_sample2 = ['overcast', 'cool', 'high', 'false']

# Transforming unknown sample into numerical data
unknown_sample_numerical1 = []
for i, feature in enumerate(unknown_sample1):
    try:
        # Attempt to transform the feature
        transformed_feature = label_encoders[i].transform([feature])[0]
    except ValueError:
        # Handle unseen values, e.g., assign a default value
        # Here, we assign -1 for unseen values
        transformed_feature = -1
    unknown_sample_numerical1.append(transformed_feature)


unknown_sample_numerical2 = []
for i, feature in enumerate(unknown_sample2):
    try:
        # Attempt to transform the feature
        transformed_feature = label_encoders[i].transform([feature])[0]
    except ValueError:
       # Handle unseen values, e.g., assign a default value
        # Here, we assign -1 for unseen values
        transformed_feature = -1
    unknown_sample_numerical2.append(transformed_feature)

# Reshape unknown_sample_numerical into a 2D array for prediction
unknown_sample_numerical1 = np.array(unknown_sample_numerical1).reshape(1, -1)
unknown_sample_numerical2 = np.array(unknown_sample_numerical2).reshape(1, -1)

# Make prediction
predicted_class1 = nb.predict(unknown_sample_numerical1)
predicted_class2 = nb.predict(unknown_sample_numerical2)

# Print the predicted class
print("Predicted class for unknown sample 1:", predicted_class1[0])
print("Predicted class for unknown sample 2:", predicted_class2[0])

