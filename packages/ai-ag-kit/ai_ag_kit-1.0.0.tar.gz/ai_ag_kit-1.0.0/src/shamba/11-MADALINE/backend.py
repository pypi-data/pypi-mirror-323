"""
Backend for MADALINE network
"""

import numpy as np
import pandas as pd

from tqdm import tqdm
from typing import Union

class MADALINE :
    def __init__(self, num_layers : int, layer_data : list, seed : int) -> None:
        np.random.seed(seed)

        self.num_layers = num_layers
        self.layer_data = layer_data

        # Initialize layers
        self.layer_in : list[np.ndarray] = []
        self.layer_out : list[np.ndarray] = []
        self.bias_weight : list[np.ndarray] = []

        for i in range(num_layers) :
            layer = np.zeros((layer_data[i], 1))
            layer_b = np.zeros((layer_data[i], 1))
            layer_c = np.random.uniform(-0.5, 0.5, (layer_data[i], 1))
            self.layer_in.append(layer)
            self.layer_out.append(layer_b)

            if i == num_layers - 1:
                layer_c = np.full((layer_data[i], 1), 0.5)

            self.bias_weight.append(layer_c)

        # Initialize weight matrices
        self.weight_mats : list[np.ndarray] = []
        for i in range(num_layers-1) :
            layer = np.random.uniform(-0.5, 0.5, (layer_data[i+1], layer_data[i]))
            if i == num_layers - 2 :
                layer = np.full((layer_data[i+1], layer_data[i]), 0.5)

            self.weight_mats.append(layer)
        
        # TODO: implement parameter calculation

    def fit(self, x_data : Union[pd.DataFrame, np.ndarray], y_data : Union[pd.DataFrame, np.ndarray], epochs : int, lr: int) :
        """
        Method to fit data to the network
        """

        # Checks
        if isinstance(x_data, pd.DataFrame) :
            if 'object' in x_data.dtypes.values :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
            x_data = x_data.to_numpy()
        if isinstance(x_data, np.ndarray) :
            if x_data.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
        else :
            x_data = np.array(x_data)
            if x_data.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
        
        if isinstance(y_data, pd.DataFrame) :
            if 'object' in y_data.dtypes.values :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
            y_data = y_data.to_numpy()
        if isinstance(y_data, np.ndarray) :
            if y_data.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
        else :
            y_data = np.array(y_data)
            if y_data.dtype == 'O' :
                raise ValueError("Object type data in dataset. Please only use numerical data.")
            
        
        
        data_count = x_data.shape[0]
        current_epoch = 0
        fitting = True

        while current_epoch < epochs and fitting :
            current_epoch += 1
            with tqdm(total=data_count, ascii=' ⚊⚊', colour="#5eff8a") as pbar :
                has_passed = []

                def row_iter(x : np.ndarray, idx: int) -> bool :
                    res_bool = True
                    for i in range(self.num_layers) :
                        if i == 0 :
                            self.layer_in[i] = x.T
                            self.layer_out[i] = x.T.reshape((self.layer_in[i].shape[0], 1))
                            continue

                        intermediate_array = np.matmul(self.weight_mats[i-1], self.layer_out[i-1])
                        self.layer_in[i] = np.add(intermediate_array, self.bias_weight[i])

                        for j in range(self.layer_in[i].shape[0]) :
                            self.layer_out[i][j] = 1 if self.layer_in[i][j].item() >= 0 else -1

                    if not np.array_equal(y_data[idx], self.layer_out[self.num_layers - 1]) :
                        res_bool = False

                        if y_data[idx].item() == 1 :
                            for i in range(self.num_layers - 2, 0, -1) :
                                node = np.argmin(np.abs(self.layer_in[i]))

                                weight_mat = self.weight_mats[i-1][node]
                                weight_mat = weight_mat + (lr * (1 - self.layer_in[i][node]) * self.layer_in[i-1])
                                self.weight_mats[i-1][node] = weight_mat

                                bias_weight = self.bias_weight[i][node]
                                bias_weight = bias_weight + (lr * (1 - self.layer_in[i][node]))
                                self.bias_weight[i][node] = bias_weight

                        elif y_data[idx].item() == -1 :
                            for i in range(self.num_layers -2, 0, -1) :
                                for node in range(len(self.layer_in[i])) :
                                    if self.layer_in[i][node] < 0 :
                                        continue

                                    weight_mat = self.weight_mats[i-1][node]
                                    weight_mat = weight_mat + (lr * (1 - self.layer_in[i][node]) * self.layer_in[i-1])
                                    self.weight_mats[i-1][node] = weight_mat

                                    bias_weight = self.bias_weight[i][node]
                                    bias_weight = bias_weight + (lr * (1 - self.layer_in[i][node]))
                                    self.bias_weight[i][node] = bias_weight

                    pbar.set_description(f"Epoch {current_epoch}")
                    pbar.set_postfix_str("")
                    pbar.update(1)

                    return res_bool
                
                for idx, row_x in enumerate(x_data) :
                    res = row_iter(row_x, idx)
                    has_passed.append(res)
                
                if all(has_passed) :
                    fitting = False
                    print("\MADALINE fitted, stopping training!")
                    return
                
        print("Max number of epochs reached. Stopping training!")
        return
    
    def predict(self, X :Union[pd.DataFrame, pd.Series, np.ndarray]) -> int :
        if isinstance(X, pd.DataFrame) or isinstance(X, pd.Series) :
            X = X.to_numpy()

        for i in range(self.num_layers) :
            if i == 0 :
                self.layer_in[i] = X.T
                self.layer_out[i] = X.T.reshape((self.layer_in[i].shape[0], 1))
                continue

            intermediate_array = np.matmul(self.weight_mats[i-1], self.layer_out[i-1])
            self.layer_in[i] = np.add(intermediate_array, self.bias_weight[i])

            for j in range(self.layer_in[i].shape[0]) :
                self.layer_out[i][j] = 1 if self.layer_in[i][j].item() >= 0 else -1

        res = self.layer_out[-1].item()
        return res

    def evaluate(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.DataFrame, np.ndarray]) -> None :
        if isinstance(X, pd.DataFrame) :
            X = X.to_numpy()
        if isinstance(y, pd.DataFrame) :
            y = y.to_numpy()

        res = [self.predict(x) for x in tqdm(X, ascii=' ⚊⚊', colour="#5eff8a")]

        total_data = X.shape[0]
        correct_data = 0
        for i, j in zip(res, y) :
            if i == j :
                correct_data += 1

        acc = (correct_data / total_data) * 100.0
        
        print(f"Accuracy: {acc}%")
        return acc


def create_madaline(topology : str, seed : int) :
    """
    Method to parse topology of a network and return the madaline object

    pass topology in the following format:\n
    `num_nodes-num_nodes-...-num_nodes`
    """
    topology = topology.strip()

    if topology.startswith("-") or topology.endswith("-") :
        raise ValueError("Incorrect formatting of topology(Starts or ends with '-')")
    if not topology.endswith("1") :
        raise ValueError("MADALINE can only have one output unit")
    
    layer_data = [int(token) for token in topology.split("-")]

    return MADALINE(len(layer_data), layer_data, seed)