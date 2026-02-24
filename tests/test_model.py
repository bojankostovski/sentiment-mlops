import pytest
import torch
from src.training.model import SentimentLSTM

def test_model_initialization():
    """Test model can be initialized"""
    model = SentimentLSTM(
        vocab_size=10000,
        embedding_dim=100,
        hidden_dim=256,
        output_dim=1,
        n_layers=2,
        bidirectional=True,
        dropout=0.5,
        pad_idx=1
    )
    
    assert model is not None
    assert isinstance(model, torch.nn.Module)

def test_model_forward_pass():
    """Test forward pass with dummy data"""
    model = SentimentLSTM(
        vocab_size=10000,
        embedding_dim=100,
        hidden_dim=256,
        output_dim=1,
        n_layers=2,
        bidirectional=True,
        dropout=0.5,
        pad_idx=1
    )
    
    # Create dummy input
    batch_size = 4
    seq_len = 50
    text = torch.randint(0, 10000, (batch_size, seq_len))
    lengths = torch.LongTensor([50, 45, 40, 35])
    
    # Forward pass
    output = model(text, lengths)
    
    # Check output shape
    assert output.shape == (batch_size, 1)

def test_model_parameters_trainable():
    """Test that model has trainable parameters"""
    model = SentimentLSTM(
        vocab_size=10000,
        embedding_dim=100,
        hidden_dim=256,
        output_dim=1,
        n_layers=2,
        bidirectional=True,
        dropout=0.5,
        pad_idx=1
    )
    
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    assert total_params > 0
    assert total_params > 1000000  # Should have over 1M parameters