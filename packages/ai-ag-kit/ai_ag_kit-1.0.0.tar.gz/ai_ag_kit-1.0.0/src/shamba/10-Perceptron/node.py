import numpy as np
import pandas as pd

from backend import Perceptron
from sklearn.model_selection import train_test_split

# import optuna

X = pd.read_csv('3_NAND.csv')
# X = pd.read_csv('3_NOR.csv')
# X = pd.read_csv('3_XOR.csv')
# X = pd.read_csv('3_XNOR.csv')

y = X.pop('output')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

percept = Perceptron(X.shape[1], 2024)
percept.fit(X_train, y_train, 36, 1.0831674723006262, 1)
percept.evaluate(X_test, y_test)

# def objective(trial) :
#     epochs = trial.suggest_int('epochs', 10, 100)
#     lr = trial.suggest_float('lr', 0.1, 1.1)

#     percept = Perceptron(X.shape[1], 2024)
#     percept.fit(X_train, y_train, epochs, lr, 1)
#     return percept.evaluate(X_test, y_test)

# study = optuna.create_study(direction="maximize")
# study.optimize(objective, n_trials=100)

# print(f'best params: {study.best_params}')