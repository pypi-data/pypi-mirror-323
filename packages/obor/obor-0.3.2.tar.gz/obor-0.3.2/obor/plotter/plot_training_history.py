import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

def plot_training_history(history: dict):
    """
    Plots the training and validation loss and accuracy from the history dictionary.

    Args:
        history (dict): A dictionary containing training and validation losses and accuracies.
                        Expected structure:
                        {
                            'train': {
                                'losses': [list of training losses],
                                'accs': [list of training accuracies]
                            },
                            'val': {
                                'losses': [list of validation losses],
                                'accs': [list of validation accuracies]
                            }
                        }
    """
    # Check if Arial font is available
    if 'Arial' in [f.name for f in fm.fontManager.ttflist]:
        plt.rcParams['font.family'] = 'Arial'  # Use Arial if available
    else:
        plt.rcParams['font.family'] = 'sans-serif'  # Fallback to default sans-serif font
    plt.rcParams['font.size'] = 11  

    # Extract data from history
    train_losses = history['train']['losses']
    val_losses = history['val']['losses']
    train_accs = history['train']['accs']
    val_accs = history['val']['accs']

    epochs = range(1, len(train_losses) + 1)

    # Create a figure with two subplots
    plt.figure(figsize=(14, 6))

    # Plot loss
    plt.subplot(1, 2, 1)
    plt.plot(epochs, train_losses, label='Training Loss', linewidth=0.8, marker='o')
    plt.plot(epochs, val_losses, label='Validation Loss', linewidth=0.8, marker='x')
    plt.title('Training and Validation Loss', fontsize=11, weight='bold')
    plt.xlabel('Epochs', fontsize=11)
    plt.ylabel('Loss', fontsize=11)
    plt.legend(fontsize=11)
    plt.grid(visible=True, linestyle='--', alpha=0.6)
    plt.xticks(np.arange(min(epochs), max(epochs) + 1, 1))

    # Plot accuracy
    plt.subplot(1, 2, 2)
    plt.plot(epochs, train_accs, label='Training Accuracy', linewidth=0.8, marker='o')
    plt.plot(epochs, val_accs, label='Validation Accuracy', linewidth=0.8, marker='x')
    plt.title('Training and Validation Accuracy', fontsize=11, weight='bold')
    plt.xlabel('Epochs', fontsize=11)
    plt.ylabel('Accuracy', fontsize=11)
    plt.legend(fontsize=11)
    plt.grid(visible=True, linestyle='--', alpha=0.6)
    plt.xticks(np.arange(min(epochs), max(epochs) + 1, 1))

    # Adjust layout and show the plot
    plt.tight_layout(pad=4)  # Match the padding in plot_dynamic
    plt.show()