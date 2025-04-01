#!/usr/bin/env python
# coding: utf-8

# # Madaline XOR wrt the solved problem in class
# 
# 
# 
# > Topology used : (2 - 2 - 1)
# 
# 

# In[ ]:


# Import the libraries
import numpy as np
from sklearn.model_selection import train_test_split

# XOR Input and Target
data = np.array([
    [-1, -1],  # Input 1
    [-1, 1],   # Input 2
    [1, -1],   # Input 3
    [1, 1]     # Input 4
])
targets = np.array([-1, 1, 1, -1])  # XOR outputs in bipolar format

# Initialize weights
v0, v1, v2 = 0.5, 0.5, 0.5  # Weights of the output layer
w = np.random.uniform(-0.1, 0.1, (2, 3))  # Weights of the hidden layer (2 hidden units, 2 inputs + 1 bias)
bias = 1
learning_rate = 0.5

# Split the data into training and testing sets (80-20 split)
train_data, test_data, train_targets, test_targets = train_test_split(data, targets, test_size=0.2, random_state=42)

# Activation function (bipolar step function)
def bipolar_step(x):
    return 1 if x >= 0 else -1

# MADALINE Algorithm Implementation
def train_madaline(data, targets, v0, v1, v2, w, bias, learning_rate, max_epochs=100):
    epoch = 0
    while epoch < max_epochs:
        weight_updated = False
        for i, x in enumerate(data):

            x1, x2 = x
            zin1 = bias * w[0][0] + x1 * w[0][1] + x2 * w[0][2]
            zin2 = bias * w[1][0] + x1 * w[1][1] + x2 * w[1][2]
            zout1 = bipolar_step(zin1)
            zout2 = bipolar_step(zin2)

            yin = bias * v0 + zout1 * v1 + zout2 * v2
            yout = bipolar_step(yin)

            # Check and adjust weights if required
            t = targets[i]
            if yout != t:
                weight_updated = True
                if t == 1:  # Case I
                    if abs(zin1) < abs(zin2):
                        j = 0
                    else:
                        j = 1
                    w[j][0] += learning_rate * (1 - zin1 if j == 0 else 1 - zin2) * bias
                    w[j][1] += learning_rate * (1 - zin1 if j == 0 else 1 - zin2) * x1
                    w[j][2] += learning_rate * (1 - zin1 if j == 0 else 1 - zin2) * x2
                elif t == -1:  # Case II
                    if zout1 > 0:
                        w[0][0] += learning_rate * (1 - zin1) * bias
                        w[0][1] += learning_rate * (1 - zin1) * x1
                        w[0][2] += learning_rate * (1 - zin1) * x2
                    if zout2 > 0:
                        w[1][0] += learning_rate * (1 - zin2) * bias
                        w[1][1] += learning_rate * (1 - zin2) * x1
                        w[1][2] += learning_rate * (1 - zin2) * x2

        # Check stopping condition
        if not weight_updated:
            break
        epoch += 1

    return w, epoch

# Testing the MADALINE
def test_madaline(data, targets, v0, v1, v2, w, bias):
    correct = 0
    for i, x in enumerate(data):
        x1, x2 = x
        zin1 = bias * w[0][0] + x1 * w[0][1] + x2 * w[0][2]
        zin2 = bias * w[1][0] + x1 * w[1][1] + x2 * w[1][2]
        zout1 = bipolar_step(zin1)
        zout2 = bipolar_step(zin2)

        yin = bias * v0 + zout1 * v1 + zout2 * v2
        yout = bipolar_step(yin)

        # Print testing output
        print(f"Testing - Input: {x}, Predicted: {yout}, Target: {targets[i]}")

        if yout == targets[i]:
            correct += 1

    accuracy = (correct / len(data)) * 100
    return accuracy

# Train the network
w, epochs = train_madaline(train_data, train_targets, v0, v1, v2, w, bias, learning_rate)

# Test the network
accuracy = test_madaline(test_data, test_targets, v0, v1, v2, w, bias)

# Print results
print(f"Training completed in {epochs} epochs.")
print(f"Testing Accuracy: {accuracy:.2f}%")


# # Madaline XOR with variable topology
# 
# > Topology Used : (3 - 2 - 1)

# In[ ]:


# Import the libraries
import numpy as np
from sklearn.model_selection import train_test_split

# XOR Input and Target
data = np.array([
    [-1, -1, -1],  # Input 1
    [-1, -1, 1],   # Input 2
    [-1, 1, -1],   # Input 3
    [-1, 1, 1],   # Input 4
    [1, -1, -1],  # Input 5
    [1, -1, 1],  # Input 6
    [1, 1, -1],  # Input 7
    [1, 1, 1]    # Input 8
])
targets = np.array([-1, 1, 1, -1, 1, -1, -1, -1])  # XOR outputs in bipolar format

# Initialize weights
v0, v1, v2 = 0.5, 0.5, 0.5  # Weights of the output layer
w = np.random.uniform(-0.1, 0.1, (2, 4))  # Weights of the hidden layer (2 hidden units, 3 inputs + 1 bias)
bias = 1
learning_rate = 0.5

# Split the data into training and testing sets (80-20 split)
train_data, test_data, train_targets, test_targets = train_test_split(data, targets, test_size=0.2, random_state=42)

# Activation function (bipolar step function)
def bipolar_step(x):
    return 1 if x >= 0 else -1

# MADALINE Algorithm Implementation
def train_madaline(data, targets, v0, v1, v2, w, bias, learning_rate, max_epochs=100):
    epoch = 0
    while epoch < max_epochs:
        weight_updated = False
        for i, x in enumerate(data):

            x1, x2, x3 = x
            zin1 = bias * w[0][0] + x1 * w[0][1] + x2 * w[0][2] + x3 * w[0][3]
            zin2 = bias * w[1][0] + x1 * w[1][1] + x2 * w[1][2] + x3 * w[1][3]
            zout1 = bipolar_step(zin1)
            zout2 = bipolar_step(zin2)

            yin = bias * v0 + zout1 * v1 + zout2 * v2
            yout = bipolar_step(yin)

            # Check and adjust weights if required
            t = targets[i]
            if yout != t:
                weight_updated = True
                if t == 1:  # Case I
                    if abs(zin1) < abs(zin2):
                        j = 0
                    else:
                        j = 1
                    w[j][0] += learning_rate * (1 - zin1 if j == 0 else 1 - zin2) * bias
                    w[j][1] += learning_rate * (1 - zin1 if j == 0 else 1 - zin2) * x1
                    w[j][2] += learning_rate * (1 - zin1 if j == 0 else 1 - zin2) * x2
                    w[j][3] += learning_rate * (1 - zin1 if j == 0 else 1 - zin2) * x3
                elif t == -1:  # Case II
                    if zout1 > 0:
                        w[0][0] += learning_rate * (1 - zin1) * bias
                        w[0][1] += learning_rate * (1 - zin1) * x1
                        w[0][2] += learning_rate * (1 - zin1) * x2
                        w[0][3] += learning_rate * (1 - zin1) * x3
                    if zout2 > 0:
                        w[1][0] += learning_rate * (1 - zin2) * bias
                        w[1][1] += learning_rate * (1 - zin2) * x1
                        w[1][2] += learning_rate * (1 - zin2) * x2
                        w[1][3] += learning_rate * (1 - zin2) * x3

        # Check stopping condition
        if not weight_updated:
            break
        epoch += 1

    return w, epoch

# Testing the MADALINE
def test_madaline(data, targets, v0, v1, v2, w, bias):
    correct = 0
    for i, x in enumerate(data):
        x1, x2, x3 = x
        zin1 = bias * w[0][0] + x1 * w[0][1] + x2 * w[0][2] + x3 * w[0][3]
        zin2 = bias * w[1][0] + x1 * w[1][1] + x2 * w[1][2] + x3 * w[1][3]
        zout1 = bipolar_step(zin1)
        zout2 = bipolar_step(zin2)

        yin = bias * v0 + zout1 * v1 + zout2 * v2
        yout = bipolar_step(yin)

        # Print testing output
        print(f"Testing - Input: {x}, Predicted: {yout}, Target: {targets[i]}")

        if yout == targets[i]:
            correct += 1

    accuracy = (correct / len(data)) * 100
    return accuracy

# Train the network
w, epochs = train_madaline(train_data, train_targets, v0, v1, v2, w, bias, learning_rate)

# Test the network
accuracy = test_madaline(test_data, test_targets, v0, v1, v2, w, bias)

# Print results
print(f"Training completed in {epochs} epochs.")
print(f"Testing Accuracy: {accuracy:.2f}%")

