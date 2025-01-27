import inspect
import torch
from torchinfo import summary as torchinfo_summary

def train(model, train_loader, test_loader, loss_fn, optimizer, epochs, device):
    """
    Training loop for a PyTorch model.

    Args:
        model (torch.nn.Module): The neural network model to train.
        train_loader (DataLoader): DataLoader for the training dataset.
        test_loader (DataLoader): DataLoader for the test dataset.
        loss_fn (torch.nn.Module): Loss function to optimize.
        optimizer (torch.optim.Optimizer): Optimizer for training.
        epochs (int): Number of training epochs.
        device (torch.device): Device to run the computations (e.g., 'cpu' or 'cuda').
    """
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss, train_correct = 0, 0
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)

            # Forward pass
            y_pred = model(X)
            loss = loss_fn(y_pred, y)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Accumulate loss and correct predictions
            train_loss += loss.item()
            train_correct += (y_pred.argmax(1) == y).sum().item()

        train_accuracy = train_correct / len(train_loader.dataset) * 100

        # Evaluation phase
        model.eval()
        test_loss, test_correct = 0, 0
        with torch.inference_mode():
            for X, y in test_loader:
                X, y = X.to(device), y.to(device)

                # Forward pass
                test_pred = model(X)
                loss = loss_fn(test_pred, y)

                # Accumulate loss and correct predictions
                test_loss += loss.item()
                test_correct += (test_pred.argmax(1) == y).sum().item()

        test_accuracy = test_correct / len(test_loader.dataset) * 100

        # Print metrics for the current epoch
        print(f"Epoch: {epoch + 1}/{epochs} | "
              f"Train Loss: {train_loss:.4f} | Train Accuracy: {train_accuracy:.2f}% | "
              f"Test Loss: {test_loss:.4f} | Test Accuracy: {test_accuracy:.2f}%")


def train_code():
    """Display the source code of the train function."""
    code = inspect.getsource(train)
    print(code)

def summary(model, input_shape, col_names=None, depth=None):
    """
    Wrapper function for torchinfo.summary with default arguments and flexibility.

    Parameters:
    - model (torch.nn.Module): The model to analyze.
    - input_shape (list or tuple): The shape of the input, including batch size.
    - col_names (list, optional): Column names to display. Default is
      ["input_size", "output_size", "num_params", "trainable"].
    - depth (int, optional): Depth of the model to display. Default is None.

    Returns:
    - str: A summary string of the model.
    """
    if col_names is None:
        col_names = ["input_size", "output_size", "num_params", "trainable"]
    
    return torchinfo_summary(
        model=model,
        input_size=tuple(input_shape),
        col_names=col_names,
        depth=depth,
    )


class Embedding(nn.Module):
    def __init__(self, in_channels, embedding_dim, patch_size, height, width):
        super().__init__()
        self.Embedding = nn.Conv2d(
            in_channels, embedding_dim, kernel_size=patch_size, stride=patch_size, padding=0
        )
        self.flatten = nn.Flatten(start_dim=2)
        self.class_embedding = nn.Parameter(torch.randn(1, 1, embedding_dim))
        self.positional_embedding = nn.Parameter(
            torch.randn(1, (height // patch_size) * (width // patch_size) + 1, embedding_dim)
        )

    def forward(self, x):
        batch_size = x.shape[0]
        z = self.Embedding(x)
        z = self.flatten(z)
        z = z.permute(0, 2, 1)
        z = torch.cat((self.class_embedding.expand(batch_size, -1, -1), z), dim=1)
        z += self.positional_embedding.expand(batch_size, -1, -1)
        return z
