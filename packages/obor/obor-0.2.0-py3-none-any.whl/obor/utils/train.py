import torch
from tqdm import tqdm

def train(model, model_name, train_loader, val_loader, optimizer, criterion, scheduler, epochs=16, patience = 4):
    """
    Trains a given model with training and validation data.

    Args:
        model: PyTorch model to be trained.
        model_name: Name of the model (used to save the trained model).
        train_loader: DataLoader for training data.
        val_loader: DataLoader for validation data.
        optimizer: Optimizer for model parameters.
        criterion: Loss function.
        scheduler: Learning rate scheduler.
        epochs: Number of training epochs (default 16).
        patience: Early stopping patience (default 4).

    Returns:
        model: The trained PyTorch model.
        history: Dictionary containing training and validation losses and accuracies for each epoch.
    """
    # Early stopping parameters
    best_val_loss = float('inf')
    patience_counter = 0

    # Move to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    criterion = criterion.to(device)

    history = {
        'train': {
            'losses': [],
            'accs': []
        },
        'val': {
            'losses': [],
            'accs': []
        }
    }

    for epoch in range(epochs):
        # START OF TRAINING
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        with tqdm(total=len(train_loader), desc=f'Epoch {epoch + 1}/{epochs} - Training', unit='batch') as pbar:
            for inputs, targets in train_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                optimizer.zero_grad()

                outputs = model(inputs)
                loss = criterion(outputs.squeeze(), targets)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()
                predictions = (outputs > 0.5).float()
                train_correct += (predictions.squeeze() == targets).sum().item()
                train_total += targets.size(0)

                pbar.update(1)

        # Save to history
        train_loss /= len(train_loader)
        history['train']['losses'].append(train_loss)
        train_acc = train_correct / train_total
        history['train']['accs'].append(train_acc)
        # END OF TRAINING

        # START OF VALIDATION
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad(), tqdm(total=len(val_loader), desc=f'Epoch {epoch + 1}/{epochs} - Validation', unit='batch') as pbar:
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                loss = criterion(outputs.squeeze(), targets)

                val_loss += loss.item()
                predictions = (outputs > 0.5).float()
                val_correct += (predictions.squeeze() == targets).sum().item()
                val_total += targets.size(0)

                pbar.update(1)

        #Save to history
        val_loss /= len(val_loader)
        history['val']['losses'].append(val_loss)
        val_acc = val_correct/val_total
        history['val']['accs'].append(val_acc)

        # Print epoch metrics
        print(f'Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')

        # Check for early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0  # Reset counter if improvement
            torch.save(model, f'{model_name}-{epoch+1}.pt')
        else:
            patience_counter += 1
            print(f'No improvement. Patience progress{patience_counter}/{patience}')

        if patience_counter >= patience:
            print('Early stopping triggered')
            break

        # Step the scheduler
        scheduler.step()

    return model, history
