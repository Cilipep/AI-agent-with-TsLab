"""Test training module."""
import unittest
import torch
from train import set_seed, FocalLoss, train_epoch, eval_epoch, train


class TestSetSeed(unittest.TestCase):
    """Test seed setting."""
    
    def test_reproducibility(self):
        """Test that seed produces reproducible results."""
        set_seed(42)
        a = torch.randn(5)
        
        set_seed(42)
        b = torch.randn(5)
        
        self.assertTrue(torch.allclose(a, b))
        
    def test_different_seeds(self):
        """Test different seeds produce different results."""
        set_seed(42)
        a = torch.randn(5)
        
        set_seed(123)
        b = torch.randn(5)
        
        self.assertFalse(torch.allclose(a, b))


class TestFocalLoss(unittest.TestCase):
    """Test Focal Loss implementation."""
    
    def test_focal_loss_forward(self):
        """Test focal loss forward pass."""
        criterion = FocalLoss(alpha=0.25, gamma=2.0)
        
        batch_size = 4
        logits = torch.randn(batch_size, 1)
        targets = torch.randint(0, 2, (batch_size, 1)).float()
        
        loss = criterion(logits, targets)
        
        self.assertIsInstance(loss.item(), float)
        self.assertGreater(loss.item(), 0)
        
    def test_focal_loss_different_alpha(self):
        """Test focal loss with different alpha."""
        criterion1 = FocalLoss(alpha=0.25, gamma=2.0)
        criterion2 = FocalLoss(alpha=0.75, gamma=2.0)
        
        batch_size = 4
        logits = torch.randn(batch_size, 1)
        targets = torch.randint(0, 2, (batch_size, 1)).float()
        
        loss1 = criterion1(logits, targets)
        loss2 = criterion2(logits, targets)
        
        # Losses should be different with different alpha
        self.assertNotAlmostEqual(loss1.item(), loss2.item(), places=2)
        
    def test_focal_loss_zero_loss(self):
        """Test focal loss with perfect predictions."""
        criterion = FocalLoss(alpha=0.25, gamma=2.0)
        
        # Perfect predictions
        logits = torch.tensor([[10.0], [-10.0], [10.0], [-10.0]]).float()
        targets = torch.tensor([[1.0], [0.0], [1.0], [0.0]]).float()
        
        loss = criterion(logits, targets)
        
        # Should be very small but not exactly zero
        self.assertLess(loss.item(), 0.01)


class TestTrainEpoch(unittest.TestCase):
    """Test training epoch."""
    
    def test_train_epoch(self):
        """Test train epoch runs without error."""
        from model import LSTMModel
        from torch.utils.data import DataLoader, TensorDataset
        
        input_size = 20
        hidden_size = 32
        num_layers = 1
        
        model = LSTMModel(input_size, hidden_size, num_layers)
        
        # Create dummy dataset
        batch_size = 4
        seq_len = 30
        X = torch.randn(16, seq_len, input_size)
        y = torch.randint(0, 2, (16, 1)).float()
        
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=batch_size)
        
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = torch.nn.BCEWithLogitsLoss()
        device = torch.device("cpu")
        
        loss, acc = train_epoch(model, loader, optimizer, criterion, device)
        
        self.assertIsInstance(loss, float)
        self.assertIsInstance(acc, float)
        self.assertGreaterEqual(acc, 0)
        self.assertLessEqual(acc, 1)


class TestEvalEpoch(unittest.TestCase):
    """Test evaluation epoch."""
    
    def test_eval_epoch(self):
        """Test eval epoch runs without error."""
        from model import LSTMModel
        from torch.utils.data import DataLoader, TensorDataset
        
        input_size = 20
        hidden_size = 32
        num_layers = 1
        
        model = LSTMModel(input_size, hidden_size, num_layers)
        model.eval()
        
        # Create dummy dataset
        batch_size = 4
        seq_len = 30
        X = torch.randn(16, seq_len, input_size)
        y = torch.randint(0, 2, (16, 1)).float()
        
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=batch_size)
        
        criterion = torch.nn.BCEWithLogitsLoss()
        device = torch.device("cpu")
        
        loss, acc = eval_epoch(model, loader, criterion, device)
        
        self.assertIsInstance(loss, float)
        self.assertIsInstance(acc, float)


if __name__ == "__main__":
    unittest.main(verbosity=2)
