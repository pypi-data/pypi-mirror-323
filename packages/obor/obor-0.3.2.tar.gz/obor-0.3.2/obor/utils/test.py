import torch
from tqdm import tqdm  # Import tqdm for progress bar

def test(model: torch.nn.Module, test_loader: torch.utils.data.DataLoader) -> tuple[float, float]:
    """
    Evaluate a PyTorch model on a test dataset and compute accuracy and F1 score.

    Args:
        model (torch.nn.Module): The trained PyTorch model to evaluate.
        test_loader (torch.utils.data.DataLoader): DataLoader for the test dataset.

    Returns:
        tuple[float, float]: A tuple containing:
            - accuracy (float): The proportion of correctly predicted instances.
            - f1 (float): The F1 score, which balances precision and recall.

    Example:
        >>> model = MyModel()  # Assume this is a trained model
        >>> test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=32)
        >>> accuracy, f1 = test(model, test_loader)
        >>> print(f"Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}")
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    y_pred = []
    y_true = []
    
    model.eval()  # Set the model to evaluation mode
    with torch.no_grad():  # Disable gradient computation
        # Wrap test_loader with tqdm for a progress bar
        for inputs, targets in tqdm(test_loader, desc="Testing", unit="batch"):
            inputs = inputs.to(device)
            targets = targets.to(device)
            
            # Forward pass
            outputs = model(inputs)
            
            # Convert outputs to binary predictions (0 or 1)
            predicted = (outputs > 0.5).int().cpu().numpy()
            y_pred.extend(predicted.flatten())
            
            # Collect ground truth labels
            y_true.extend(targets.cpu().numpy().flatten())
    
    # Convert to tensors for easier calculations
    y_pred = torch.tensor(y_pred)
    y_true = torch.tensor(y_true)
    
    # Calculate accuracy
    correct = (y_pred == y_true).sum().item()
    total = y_true.size(0)
    accuracy = correct / total
    
    # Calculate F1 score
    true_positives = ((y_pred == 1) & (y_true == 1)).sum().item()
    false_positives = ((y_pred == 1) & (y_true == 0)).sum().item()
    false_negatives = ((y_pred == 0) & (y_true == 1)).sum().item()
    
    precision = true_positives / (true_positives + false_positives + 1e-10)  # Add epsilon to avoid division by zero
    recall = true_positives / (true_positives + false_negatives + 1e-10)     # Add epsilon to avoid division by zero
    f1 = 2 * (precision * recall) / (precision + recall + 1e-10)             # Add epsilon to avoid division by zero
    
    return accuracy, f1