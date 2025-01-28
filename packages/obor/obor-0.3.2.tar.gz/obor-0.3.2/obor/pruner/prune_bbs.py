import torch
import numpy as np
from tqdm import tqdm

def prune_bbs(model: torch.nn.Module, bankNum: int, sparsity: float) -> torch.nn.Module:
    """
    Prunes a PyTorch model using the Bank Balance Sparsity (BBS) method.

    This method divides each row of the weight matrix into smaller blocks (banks) and prunes
    the smallest magnitude weights within each bank based on the specified sparsity level.
    This ensures that pruning is distributed evenly across the weight matrix.

    Args:
        model (torch.nn.Module): The PyTorch model to prune. Must contain weight matrices to be pruned.
        bankNum (int): The number of banks (blocks) to divide each weight matrix row into.
        sparsity (float): The fraction of weights to prune within each bank (e.g., 0.2 for 20%).

    Returns:
        torch.nn.Module: The pruned model with specified sparsity applied to its weight matrices.

    Example:
        >>> model = SimpleModel()  # A simple PyTorch model
        >>> pruned_model = prune_bbs(model, bankNum=4, sparsity=0.2)  # Prune with 4 banks and 20% sparsity
    """
    
    print("[OBOR] START OF PRUNING USING BANK BALANCE SPARSITY METHOD")
    for name, param in model.named_parameters():
        # Only prune the weights
        if 'weight' in name and 'embedding' not in name:
            Mp = param.data.clone()

            for row in tqdm(Mp, desc=f'Pruning {name}', leave=True):
                block_size = len(row) // bankNum

                for i in range(bankNum):
                    # Get the current bank (block)
                    start = i * block_size
                    end = start + block_size if i < bankNum - 1 else len(row)
                    bank = row[start:end]

                    # Sort the elements in the bank
                    sorted_bank = np.sort(abs(bank))

                    # Calculate the threshold T for pruning
                    threshold_index = int(len(sorted_bank) * sparsity)
                    T = sorted_bank[threshold_index] if threshold_index < len(sorted_bank) else float('inf')

                    # Prune elements below the threshold T
                    for k in range(start, end):
                        if abs(row[k]) < T:
                            row[k] = 0

            param.data = Mp
            
    print("\n[OBOR] END OF PRUNING")

    return model