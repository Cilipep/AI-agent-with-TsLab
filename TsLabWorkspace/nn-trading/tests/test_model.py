"""Test model module."""
import unittest
import numpy as np
import torch
from model import (
    LSTMModel, TCNModel, AttentionTransformer, 
    TransformerModel, build_model, Ensemble, 
    StackingEnsemble, HybridEnsemble, Config
)


class TestLSTMModel(unittest.TestCase):
    """Test LSTM model architecture."""
    
    def setUp(self):
        """Setup test parameters."""
        self.input_size = 20
        self.hidden_size = 64
        self.num_layers = 2
        
    def test_lstm_forward(self):
        """Test LSTM forward pass."""
        model = LSTMModel(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))
        
    def test_lstm_parameters(self):
        """Test LSTM has learnable parameters."""
        model = LSTMModel(self.input_size, self.hidden_size, self.num_layers)
        
        total_params = sum(p.numel() for p in model.parameters())
        self.assertGreater(total_params, 0)


class TestTCNModel(unittest.TestCase):
    """Test TCN model architecture."""
    
    def setUp(self):
        """Setup test parameters."""
        self.input_size = 20
        self.hidden_size = 64
        self.num_layers = 2
        
    def test_tcn_forward(self):
        """Test TCN forward pass."""
        model = TCNModel(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))


class TestTransformerModel(unittest.TestCase):
    """Test Transformer model architecture."""
    
    def setUp(self):
        """Setup test parameters."""
        self.input_size = 20
        self.hidden_size = 64
        self.num_layers = 2
        
    def test_transformer_forward(self):
        """Test Transformer forward pass."""
        model = TransformerModel(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))


class TestAttentionTransformer(unittest.TestCase):
    """Test AttentionTransformer architecture."""
    
    def setUp(self):
        """Setup test parameters."""
        self.input_size = 20
        self.hidden_size = 64
        self.num_layers = 2
        
    def test_attention_forward(self):
        """Test AttentionTransformer forward pass."""
        model = AttentionTransformer(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))


class TestBuildModel(unittest.TestCase):
    """Test model builder."""
    
    def setUp(self):
        """Setup config."""
        self.input_size = 20
        
    def test_build_lstm(self):
        """Test building LSTM model."""
        config = Config()
        config.model_type = "lstm"
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        model = build_model(config, self.input_size)
        self.assertIsInstance(model, LSTMModel)
        
    def test_build_attention(self):
        """Test building Attention model."""
        config = Config()
        config.model_type = "attention"
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        model = build_model(config, self.input_size)
        self.assertIsInstance(model, AttentionTransformer)
        
    def test_build_transformer(self):
        """Test building Transformer model."""
        config = Config()
        config.model_type = "transformer"
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        model = build_model(config, self.input_size)
        self.assertIsInstance(model, TransformerModel)


class TestEnsemble(unittest.TestCase):
    """Test Ensemble model."""
    
    def setUp(self):
        """Setup models."""
        self.input_size = 20
        config = Config()
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        self.models = [
            build_model(config, self.input_size)
            for _ in range(3)
        ]
        
    def test_ensemble_creation(self):
        """Test ensemble can be created."""
        ensemble = Ensemble(self.models)
        self.assertEqual(len(ensemble.models), 3)
        
    def test_ensemble_forward(self):
        """Test ensemble forward pass."""
        ensemble = Ensemble(self.models)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        
        # Test eval mode
        ensemble.eval()
        output = ensemble(x)
        
        self.assertEqual(output.shape, (batch_size, 1))
        
    def test_ensemble_weights(self):
        """Test ensemble default weights."""
        ensemble = Ensemble(self.models)
        
        # Should have equal weights
        expected_weight = 1.0 / len(self.models)
        for w in ensemble.weights:
            self.assertAlmostEqual(w, expected_weight)


class TestStackingEnsemble(unittest.TestCase):
    """Test StackingEnsemble."""
    
    def setUp(self):
        """Setup models."""
        self.input_size = 20
        config = Config()
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        self.base_models = [
            build_model(config, self.input_size)
            for _ in range(3)
        ]
        
    def test_stacking_creation(self):
        """Test stacking can be created."""
        stacking = StackingEnsemble(self.base_models)
        self.assertEqual(len(stacking.base_models), 3)


class TestHybridEnsemble(unittest.TestCase):
    """Test HybridEnsemble."""
    
    def setUp(self):
        """Setup models."""
        self.input_size = 20
        config = Config()
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        self.neural_models = [
            build_model(config, self.input_size)
            for _ in range(2)
        ]
        
    def test_hybrid_creation(self):
        """Test hybrid ensemble can be created."""
        hybrid = HybridEnsemble(self.neural_models)
        self.assertEqual(len(hybrid.neural_models), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
