import torch
from tqdm import tqdm

def prune_low_magnitude(model: torch.nn.Module, sparsity: float) -> torch.nn.Module:
    """
    Prunes the model using the low-magnitude detection method.

    Args:
        model (torch.nn.Module): The model to prune.
        sparsity (float): The fraction of weights to prune (e.g., 0.2 for 20%).

    Returns:
        torch.nn.Module: The pruned model.
    """
    print("[OBOR] START OF PRUNING USING LOW MAGNITUDE DETECTION METHOD")
    
    # Iterate over all parameters in the model
    for name, param in tqdm(model.named_parameters(), desc=f'Pruning', leave=True):
        # Only prune the weights (ignore biases and embedding layers)
        if 'weight' in name and 'embedding' not in name:
            # Clone the weight matrix
            Mp = param.data.clone()
            
            # Flatten the weight matrix and calculate the number of weights to prune
            flat_weights = torch.abs(Mp.view(-1))  # Flatten and take absolute values
            k = int(sparsity * flat_weights.numel())  # Number of weights to prune
            
            # Find the threshold for pruning (k-th smallest magnitude)
            if k > 0:
                threshold = torch.topk(flat_weights, k, largest=False).values[-1]
                
                # Create a binary mask for pruning
                mask = torch.abs(Mp) > threshold
                
                # Apply the mask to prune the weights
                Mp *= mask.float()
            
            # Update the parameter with the pruned weights
            param.data = Mp
    
    print("\n[OBOR] END OF PRUNING")
    return model