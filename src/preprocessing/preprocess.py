import torch
from torch.utils.data import Dataset
import pickle
import os
from collections import Counter

class IMDBDataset(Dataset):
    def __init__(self, data, vocab, max_length=256):
        self.data = data
        self.vocab = vocab
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        label, text = self.data[idx]
        
        # Simple word tokenization
        tokens = text.lower().split()[:self.max_length]
        
        # Numericalize
        numericalized = [self.vocab.get(token, self.vocab['<unk>']) for token in tokens]
        
        # Pad sequence
        numericalized = numericalized + [self.vocab['<pad>']] * (self.max_length - len(numericalized))
        
        return {
            'text': torch.LongTensor(numericalized),
            'label': torch.FloatTensor([1 if label == 'pos' else 0]),
            'length': len(tokens)
        }

def collate_batch(batch):
    texts = torch.stack([item['text'] for item in batch])
    labels = torch.cat([item['label'] for item in batch])
    lengths = torch.LongTensor([item['length'] for item in batch])
    
    return texts, labels, lengths

def build_vocab(data, min_freq=5):
    """Build vocabulary from dataset"""
    counter = Counter()
    
    for _, text in data:
        tokens = text.lower().split()
        counter.update(tokens)
    
    # Create vocab with special tokens
    vocab = {'<unk>': 0, '<pad>': 1}
    idx = 2
    
    for word, freq in counter.items():
        if freq >= min_freq:
            vocab[word] = idx
            idx += 1
    
    return vocab

def download_imdb_dataset():
    """Download IMDB dataset using datasets library"""
    try:
        from datasets import load_dataset
        print("Downloading IMDB dataset from HuggingFace...")
        dataset = load_dataset('imdb')
        
        # Convert to our format
        train_data = [(
            'pos' if item['label'] == 1 else 'neg',
            item['text']
        ) for item in dataset['train']]
        
        test_data = [(
            'pos' if item['label'] == 1 else 'neg',
            item['text']
        ) for item in dataset['test']]
        
        return train_data, test_data
        
    except ImportError:
        print("datasets library not found. Installing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'datasets'])
        return download_imdb_dataset()

def prepare_data(save_dir='data/processed'):
    """Download and preprocess IMDB dataset"""
    os.makedirs(save_dir, exist_ok=True)
    
    print("Loading IMDB dataset...")
    train_data, test_data = download_imdb_dataset()
    
    print(f"Train samples: {len(train_data)}")
    print(f"Test samples: {len(test_data)}")
    
    # Build vocabulary
    print("Building vocabulary...")
    vocab = build_vocab(train_data, min_freq=5)
    print(f"Vocabulary size: {len(vocab)}")
    
    # Save preprocessed data
    data_dict = {
        'train_data': train_data,
        'test_data': test_data,
        'vocab': vocab,
        'vocab_size': len(vocab)
    }
    
    with open(f'{save_dir}/imdb_processed.pkl', 'wb') as f:
        pickle.dump(data_dict, f)
    
    print(f"Data saved to {save_dir}/imdb_processed.pkl")
    
    return data_dict

if __name__ == '__main__':
    prepare_data()
