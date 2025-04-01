"""
Backend for perceptron
"""

import numpy as np
import pandas as pd

from tqdm import tqdm
from typing import Union

class Perceptron() :
    """Perceptron class"""
    def __init__(self, num_inputs: int, seed : int, weights: np.ndarray=None):
        np.random.seed(seed)
        self.num_inputs = num_inputs
        if weights is not None :
            if len(weights) != num_inputs + 1 :
                self.weights = np.random.uniform(-1, 1, self.num_inputs+1)
            else :
                self.weights = weights.ravel()
        else :
            self.weights = np.random.uniform(-1, 1, self.num_inputs+1)


    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.DataFrame, np.ndarray], epochs: int=20, lr: float=2e-2, thresh: float=1) -> None :
        """Method to fit the perceptron to a dataset
        
        Args
        ----
            X:
                Dataset to fit
            y:
                output of the dataset
            epochs:
                Number of times the learning is repeated before stopping
            lr:
                Learning rate
            thresh:
                THreshold for the activation function
        """

        # Checks
        if isinstance(X, pd.DataFrame) :
            if 'object' in X.dtypes.values :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
            X = X.to_numpy()
        if isinstance(X, np.ndarray) :
            if X.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
        else :
            X = np.array(X)
            if X.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
        
        if isinstance(y, pd.DataFrame) :
            if 'object' in y.dtypes.values :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
            y = y.to_numpy()
        if isinstance(y, np.ndarray) :
            if y.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
        else :
            y = np.array(y)
            if y.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")


        is_fitting = True
        epoch_ctr = 0

        self.thresh = thresh

        while epoch_ctr < epochs and is_fitting :
            epoch_ctr += 1
            with tqdm(total=X.shape[0], ascii=' ⚊⚊', colour="#5eff8a") as pbar :

                has_passed = []

                def row_iter(x: np.ndarray, idx: int) :
                    res_bool = True

                    a = np.insert(x, 0, 1)
                    y_in = np.sum(np.multiply(a, self.weights))

                    y_out = 0
                    if y_in > thresh : y_out = 1
                    elif y_in >= -thresh and y_in <= thresh : y_out = 0
                    elif y_in < -thresh : y_out = -1

                    if y_out != y[idx] :
                        self.weights = np.add(self.weights, np.multiply(a, (lr * y[idx])))
                        res_bool = False

                    pbar.set_description(f'Epoch {epoch_ctr} ')
                    pbar.set_postfix_str("")
                    pbar.update(1)

                    return res_bool

                for idx, row_x in enumerate(X) :
                    res = row_iter(row_x, idx)
                    has_passed.append(res)
                
                if all(has_passed) :
                    is_fitting = False
                    print("\nPerceptron fitted, stopping training!")
                    return
                
        print("Max number of epochs reached. Stopping training!")
        return 

    def predict(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> int :
        """Method to predict test data"""
        if isinstance(X, pd.DataFrame) or isinstance(X, pd.Series) :
            X = X.to_numpy()

        a = np.insert(X, 0, 1)
        y_in = np.sum(np.multiply(a, self.weights))

        y_out = 0
        if y_in > self.thresh : y_out = 1
        elif y_in >= -self.thresh and y_in <= self.thresh : y_out = 0
        elif y_in < -self.thresh : y_out = -1

        return y_out


    def evaluate(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.DataFrame, np.ndarray]) -> None :
        if isinstance(X, pd.DataFrame) :
            X = X.to_numpy()
        if isinstance(y, pd.DataFrame) :
            y = y.to_numpy()
        
        res = [self.predict(x) for x in X]

        total_data = X.shape[0]
        correct_data = 0
        for i, j in zip(res, y) :
            if i == j :
                correct_data += 1
        
        acc = (correct_data / total_data) * 100.0
        
        print(f"Accuracy: {acc}%")
        return acc

    def __call__(self, X: Union[pd.DataFrame, np.ndarray], *args, **kwds):
        return self.predict(X)