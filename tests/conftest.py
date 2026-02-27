import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
import torch
from unittest.mock import MagicMock, patch
from collections import Counter, OrderedDict

@pytest.fixture
def device():
    """Fixture for device"""
    return torch.device('cpu')

@pytest.fixture
def dummy_vocab():
    """Create a simple mock vocab"""
    # Create a simple dictionary-like vocab
    class MockVocab(dict):
        def __init__(self):
            super().__init__()
            self.update({
                '<unk>': 0,
                '<pad>': 1,
                'test': 2,
                'great': 3,
                'amazing': 4,
                'terrible': 5,
                'bad': 6,
                'movie': 7,
                'good': 8,
                'this': 9,
                'is': 10
            })
            self.default_index = 0
        
        def __getitem__(self, item):
            return super().get(item, self.default_index)
    
    return MockVocab()

@pytest.fixture
def mock_model():
    """Create a mock model"""
    mock = MagicMock()
    mock.eval.return_value = None
    
    # Mock the forward pass to return positive sentiment
    def forward_side_effect(text_tensor, lengths):
        # Return tensor that simulates positive prediction (logit > 0 = positive)
        batch_size = text_tensor.size(0) if hasattr(text_tensor, 'size') else 1
        return torch.tensor([[0.8]] * batch_size)
    
    mock.side_effect = forward_side_effect
    return mock

@pytest.fixture
def client(dummy_vocab, mock_model):
    """Create test client with mocked model loading"""
    
    # Patch load_model to inject our mocks
    def mock_load_model(model_path=None):
        """Mock model loading - inject our test doubles"""
        import src.serving.enhanced_inference as app_module
        app_module.model = mock_model
        app_module.vocab = dummy_vocab
        app_module.device = torch.device('cpu')
    
    # Patch before importing
    with patch('src.serving.enhanced_inference.load_model', side_effect=mock_load_model):
        from src.serving.enhanced_inference import app
        
        app.config['TESTING'] = True
        
        # Manually trigger the mock load
        import src.serving.enhanced_inference as app_module
        app_module.model = mock_model
        app_module.vocab = dummy_vocab
        app_module.device = torch.device('cpu')
        
        with app.test_client() as test_client:
            yield test_client