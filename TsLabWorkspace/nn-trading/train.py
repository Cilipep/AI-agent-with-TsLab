import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def train_epoch(model, loader, optimizer, criterion, device, max_grad_norm=1.0):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    for x, y in loader:
        x, y = x.to(device), y.to(device).unsqueeze(1)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        optimizer.step()
        total_loss += loss.item() * x.size(0)
        correct += ((out > 0.5).float() == y).sum().item()
        total += x.size(0)
    return total_loss / total, correct / total


def eval_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device).unsqueeze(1)
            out = model(x)
            loss = criterion(out, y)
            total_loss += loss.item() * x.size(0)
            correct += ((out > 0.5).float() == y).sum().item()
            total += x.size(0)
    return total_loss / total, correct / total


def train(model, train_ds, val_ds, config, device, quiet=False):
    model = model.to(device)
    # Weight decay for regularization
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=0.01)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs, eta_min=1e-6)

    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size)

    best_val_loss = float("inf")
    patience_counter = 0
    best_state = None

    for epoch in range(config.epochs):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = eval_epoch(model, val_loader, criterion, device)
        scheduler.step()

        if not quiet:
            print(f"Epoch {epoch+1:3d} | "
                  f"train_loss={train_loss:.4f} acc={train_acc:.3f} | "
                  f"val_loss={val_loss:.4f} acc={val_acc:.3f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= config.patience:
                if not quiet:
                    print(f"Early stopping at epoch {epoch+1}")
                break

    if best_state:
        model.load_state_dict(best_state)
    return model
