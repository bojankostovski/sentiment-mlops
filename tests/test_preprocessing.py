import pytest
from torchtext.data.utils import get_tokenizer

def test_tokenizer():
    """Test basic tokenizer functionality"""
    tokenizer = get_tokenizer('basic_english')
    
    text = "This is a great movie!"
    tokens = tokenizer(text)
    
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    assert 'great' in tokens or 'movie' in tokens

def test_text_length():
    """Test text truncation"""
    tokenizer = get_tokenizer('basic_english')
    
    long_text = " ".join(["word"] * 1000)
    tokens = tokenizer(long_text)
    
    max_length = 256
    truncated = tokens[:max_length]
    
    assert len(truncated) == max_length