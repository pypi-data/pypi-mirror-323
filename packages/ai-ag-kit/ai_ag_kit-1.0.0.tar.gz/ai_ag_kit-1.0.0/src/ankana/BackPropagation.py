#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np

# Sigmoid activation function and its derivative
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

# Initialize network topology: 3-2-2-2
input_size = 3
hidden_size1 = 2
hidden_size2 = 2
output_size = 2

# Initialize weights and biases randomly
np.random.seed(0)
weights_input_hidden1 = np.random.uniform(-1, 1, (input_size, hidden_size1))
bias_hidden1 = np.random.uniform(-1, 1, (1, hidden_size1))

weights_hidden1_hidden2 = np.random.uniform(-1, 1, (hidden_size1, hidden_size2))
bias_hidden2 = np.random.uniform(-1, 1, (1, hidden_size2))

weights_hidden2_output = np.random.uniform(-1, 1, (hidden_size2, output_size))
bias_output = np.random.uniform(-1, 1, (1, output_size))

# Training data
train_input = np.array([[1, 0, 1]])  # Single input example
train_target = np.array([[1, 0]])    # Corresponding target

# Learning rate
lr = 0.9

# Forward pass
def forward_pass(input_data):
    z1 = np.dot(input_data, weights_input_hidden1) + bias_hidden1
    a1 = sigmoid(z1)

    z2 = np.dot(a1, weights_hidden1_hidden2) + bias_hidden2
    a2 = sigmoid(z2)

    z3 = np.dot(a2, weights_hidden2_output) + bias_output
    output = sigmoid(z3)

    return a1, a2, output

# Backpropagation
def backpropagation(input_data, target_label, a1, a2, output):
    global weights_input_hidden1, bias_hidden1
    global weights_hidden1_hidden2, bias_hidden2
    global weights_hidden2_output, bias_output

    # Calculate output error
    error_output = target_label - output
    delta_output = error_output * sigmoid_derivative(output)

    # Calculate error for hidden layer 2
    error_hidden2 = np.dot(delta_output, weights_hidden2_output.T)
    delta_hidden2 = error_hidden2 * sigmoid_derivative(a2)

    # Calculate error for hidden layer 1
    error_hidden1 = np.dot(delta_hidden2, weights_hidden1_hidden2.T)
    delta_hidden1 = error_hidden1 * sigmoid_derivative(a1)

    # Update weights and biases
    weights_hidden2_output += lr * np.dot(a2.T, delta_output)
    bias_output += lr * delta_output

    weights_hidden1_hidden2 += lr * np.dot(a1.T, delta_hidden2)
    bias_hidden2 += lr * delta_hidden2

    weights_input_hidden1 += lr * np.dot(input_data.T, delta_hidden1)
    bias_hidden1 += lr * delta_hidden1

# Training loop
epochs = 10000  # Train for 10,000 iterations
for epoch in range(epochs):
    a1, a2, output = forward_pass(train_input)
    backpropagation(train_input, train_target, a1, a2, output)

# Test on all possible inputs
all_possible_inputs = np.array([[0, 0, 0],
                                 [0, 0, 1],
                                 [0, 1, 0],
                                 [0, 1, 1],
                                 [1, 0, 0],
                                 [1, 0, 1],
                                 [1, 1, 0],
                                 [1, 1, 1]])

print("Outputs for all possible inputs:")
for input_data in all_possible_inputs:
    _, _, output = forward_pass(input_data)
    print(f"Input: {input_data} -> Output: {output}")

