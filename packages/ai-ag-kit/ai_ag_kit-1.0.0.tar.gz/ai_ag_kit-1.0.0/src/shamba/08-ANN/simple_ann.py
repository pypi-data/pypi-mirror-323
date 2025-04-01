import numpy as np
import shamboflow as sf

# Training data
x_data = np.array([[1, 0, 1]])
y_data = np.array([[1]])

# Parameters
learning_rate = 0.9
epochs = 20

# Create model
model = sf.models.Sequential()

model.add(sf.layers.Dense(3))
model.add(sf.layers.Dense(2, 'sigmoid'))
model.add(sf.layers.Dense(1, 'sigmoid'))

model.compile(learning_rate=learning_rate, loss='mean_squared_error', verbose=True)
model.summary()

# Train model
model.fit(x_data, y_data, epochs)
model.save("SavedModel.sf")

# Inference
test_x = np.array([
    [0, 0, 0],
    [0, 0, 1],
    [0, 1, 0],
    [0, 1, 1],
    [1, 0, 0],
    [1, 1, 0],
    [1, 1, 1]
])

for data in test_x :
    print(f"Prediction: {model.predict(data.reshape((1, 3)))}")