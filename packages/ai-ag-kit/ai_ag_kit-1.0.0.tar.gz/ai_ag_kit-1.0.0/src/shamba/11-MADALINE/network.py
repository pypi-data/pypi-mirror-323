import numpy as np
import pandas as pd

from backend import create_madaline
from sklearn.model_selection import train_test_split

# import optuna

# X = pd.read_csv('3_NAND.csv')
# X = pd.read_csv('3_NOR.csv')
X = pd.read_csv('3_XOR.csv')
# X = pd.read_csv('3_XNOR.csv')

y = X.pop('output')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

MADALINE = create_madaline("3-2-1", 2025)

MADALINE.fit(X_train, y_train, 68, 0.8746449317913777)
MADALINE.evaluate(X_test, y_test)

# def objective(trial) :
#     epochs = trial.suggest_int('epochs', 10, 100)
#     lr = trial.suggest_float('lr', 0.1, 1.1)

#     MADALINE = create_madaline("3-2-1", 2025)

#     MADALINE.fit(X_train, y_train, epochs, lr)
#     return MADALINE.evaluate(X_test, y_test)

# study = optuna.create_study(direction="maximize")
# study.optimize(objective, n_trials=100)

# print(f'best params: {study.best_params}')