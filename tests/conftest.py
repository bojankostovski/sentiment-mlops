import pytest
import torch

@pytest.fixture
def device():
    """Fixture for device"""
    return torch.device('cpu')

@pytest.fixture
def dummy_vocab():
    """Fixture for dummy vocabulary"""
    from torchtext.vocab import vocab as build_vocab
    from collections import Counter
    
    counter = Counter(['hello', 'world', 'test'])
    vocabulary = build_vocab(counter, specials=['<unk>', '<pad>'])
    vocabulary.set_default_index(vocabulary['<unk>'])
    
    return vocabulary