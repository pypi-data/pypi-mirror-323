import torch
import numpy as np
from tqdm import tqdm

def prune_bbs(model: torch.nn.Module, bankNum: int, sparsity: float) -> torch.nn.Module:
    print("[OBOR] START OF PRUNING USING BANK BALANCE SPARSITY METHOD")
    for name, param in model.named_parameters():
        # Only prune the weights
        if 'weight' in name:
            Mp = param.data.clone()

            for row in tqdm(Mp, desc=f'Pruning {name}', leave=False):
                block_size = len(row) // bankNum
                
                for i in range(bankNum):
                    # Get the current bank (block)
                    start = i * block_size
                    end = start + block_size if i < bankNum - 1 else len(row)
                    bank = row[start:end]

                    # Sort the elements in the bank
                    sorted_bank = np.sort(bank)

                    # Calculate the threshold T for pruning
                    threshold_index = int(len(sorted_bank) * sparsity)
                    T = sorted_bank[threshold_index] if threshold_index < len(sorted_bank) else float('inf')

                    # Prune elements below the threshold T
                    for k in range(start, end):
                        if row[k] < T:
                            row[k] = 0

            param.data = Mp
    print("[OBOR] END OF PRUNING")
            
    return model