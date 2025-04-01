#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import random

# Define the logic gate data
gates = {
    "AND": {"inputs": [[0, 0], [0, 1], [1, 0], [1, 1]], "outputs": [0, 0, 0, 1]},
    "OR": {"inputs": [[0, 0], [0, 1], [1, 0], [1, 1]], "outputs": [0, 1, 1, 1]},
    "NAND": {"inputs": [[0, 0], [0, 1], [1, 0], [1, 1]], "outputs": [1, 1, 1, 0]},
    "NOR": {"inputs": [[0, 0], [0, 1], [1, 0], [1, 1]], "outputs": [1, 0, 0, 0]},
    "XOR": {"inputs": [[0, 0], [0, 1], [1, 0], [1, 1]], "outputs": [0, 1, 1, 0]},
    "XNOR": {"inputs": [[0, 0], [0, 1], [1, 0], [1, 1]], "outputs": [1, 0, 0, 1]}
}

learning_rate = random.uniform(0.1, 1.0)
print(f"Learning Rate: {learning_rate}")

# Train and test perceptron for each logic gate
for gate_name, gate_data in gates.items():
    print(f"Training perceptron for {gate_name} gate")

    # Extract inputs and outputs
    X = gate_data["inputs"]
    y = gate_data["outputs"]

    # Split the data into training and testing sets (80-20 split)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the Perceptron model
    perceptron = Perceptron(max_iter=10000, eta0=learning_rate, random_state=42, fit_intercept=True)

    # Set intercept for desired threshold
    perceptron.intercept_ = 1

    # Train the model
    perceptron.fit(X, y)

    # Make predictions
    y_pred = perceptron.predict(X)

    # Evaluate the model
    accuracy = accuracy_score(y, y_pred)

    print(f"Testing Inputs: {X}")
    print(f"Expected Outputs: {y}")
    print(f"Predicted Outputs: {y_pred}")
    print(f"Accuracy: {accuracy * 100:.2f}%\n")

