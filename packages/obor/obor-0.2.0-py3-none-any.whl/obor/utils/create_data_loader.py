import torch
from torch.utils.data import Dataset, DataLoader

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


def create_data_loader(X, y, batch_size=32, shuffle=False):
    """
    Helper function to create DataLoader instances for train, validation, and test datasets.

    Args:
        X (array-like): Training features.
        y (array-like): Training labels.
        batch_size (int): Batch size for DataLoader.

    Returns:
        train_loader, val_loader, test_loader: DataLoader instances for each dataset.
    """
    dataset = CustomDataset(X, y)

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

    return loader
