import torch
from typing import Union, List
from torch.utils.data import Dataset, DataLoader
import numpy as np

class CustomDataset(Dataset):
    def __init__(self, X, y):
        """
        Args:
            X (array-like): Input features, typically a list or array of tokenized text data.
            y (array-like): Target labels corresponding to each input example.
        """
        self.X = torch.tensor(X, dtype=torch.long)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        """Returns the number of samples in the dataset."""
        return len(self.X)

    def __getitem__(self, idx):
        """Fetches the sample at index `idx`."""
        return self.X[idx], self.y[idx]


import torch
from torch.utils.data import DataLoader, Dataset

def create_data_loader(
    X: Union[np.ndarray, List, torch.Tensor], 
    y: Union[np.ndarray, List, torch.Tensor], 
    batch_size: int = 32, 
    shuffle: bool = False
) -> DataLoader:
    """
    Helper function to create DataLoader instances for train, validation, and test datasets.

    Args:
        X (array-like): Training features. Can be a NumPy array, list, or PyTorch tensor.
        y (array-like): Training labels. Can be a NumPy array, list, or PyTorch tensor.
        batch_size (int): Batch size for DataLoader.
        shuffle (bool): Whether to shuffle the data.

    Returns:
        DataLoader: A DataLoader instance for the dataset.
    """
    dataset = CustomDataset(X, y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
    return loader