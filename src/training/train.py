import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import argparse
import pickle
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import json
from pathlib import Path
from tqdm import tqdm

# Import from local modules
from model import SentimentLSTM

# Import preprocessing utilities
import_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'preprocessing')
sys.path.insert(0, import_path)
from preprocess import IMDBDataset, collate_batch

def binary_accuracy(preds, y):
    """Calculate accuracy"""
    rounded_preds = torch.round(torch.sigmoid(preds))
    correct = (rounded_preds == y).float()
    acc = correct.sum() / len(correct)
    return acc

def train_epoch(model, iterator, optimizer, criterion, device):
    """Train for one epoch"""
    epoch_loss = 0
    epoch_acc = 0
    model.train()
    
    for batch in tqdm(iterator, desc='Training'):
        texts, labels, lengths = batch
        texts, labels = texts.to(device), labels.to(device)
        
        optimizer.zero_grad()
        predictions = model(texts, lengths).squeeze(1)
        
        loss = criterion(predictions, labels)
        acc = binary_accuracy(predictions, labels)
        
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item()
        epoch_acc += acc.item()
    
    return epoch_loss / len(iterator), epoch_acc / len(iterator)

def evaluate(model, iterator, criterion, device):
    """Evaluate model"""
    epoch_loss = 0
    epoch_acc = 0
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(iterator, desc='Evaluating'):
            texts, labels, lengths = batch
            texts, labels = texts.to(device), labels.to(device)
            
            predictions = model(texts, lengths).squeeze(1)
            
            loss = criterion(predictions, labels)
            acc = binary_accuracy(predictions, labels)
            
            epoch_loss += loss.item()
            epoch_acc += acc.item()
            
            # Store predictions for metrics
            probs = torch.sigmoid(predictions)
            all_preds.extend(probs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Calculate additional metrics
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    pred_labels = (all_preds > 0.5).astype(int)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, pred_labels, average='binary'
    )
    
    try:
        auc = roc_auc_score(all_labels, all_preds)
    except:
        auc = 0.0
    
    metrics = {
        'loss': epoch_loss / len(iterator),
        'accuracy': epoch_acc / len(iterator),
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc
    }
    
    return metrics

def count_parameters(model):
    """Count trainable parameters"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def train(args):
    """Main training function"""
    
    # Set random seeds for reproducibility
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load preprocessed data
    print("Loading data...")
    with open('data/processed/imdb_processed.pkl', 'rb') as f:
        data_dict = pickle.load(f)
    
    vocab = data_dict['vocab']
    train_data = data_dict['train_data']
    test_data = data_dict['test_data']
    
    # Create datasets
    train_dataset = IMDBDataset(train_data, vocab, args.max_length)
    test_dataset = IMDBDataset(test_data, vocab, args.max_length)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collate_batch
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_batch
    )
    
    print(f"Train batches: {len(train_loader)}")
    print(f"Test batches: {len(test_loader)}")
    
    # Create model
    print("Creating model...")
    model = SentimentLSTM(
        vocab_size=len(vocab),
        embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
        output_dim=1,
        n_layers=args.n_layers,
        bidirectional=args.bidirectional,
        dropout=args.dropout,
        pad_idx=vocab['<pad>']
    ).to(device)
    
    print(f"Model has {count_parameters(model):,} trainable parameters")
    
    # Optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss().to(device)
    
    # Training loop
    best_valid_acc = 0
    
    for epoch in range(args.epochs):
        print(f'\nEpoch {epoch+1}/{args.epochs}')
        
        train_loss, train_acc = train_epoch(
            model, train_loader, optimizer, criterion, device
        )
        valid_metrics = evaluate(model, test_loader, criterion, device)
        
        print(f'Train Loss: {train_loss:.3f} | Train Acc: {train_acc*100:.2f}%')
        print(f'Val Loss: {valid_metrics["loss"]:.3f} | Val Acc: {valid_metrics["accuracy"]*100:.2f}%')
        print(f'Val F1: {valid_metrics["f1"]:.3f} | Val AUC: {valid_metrics["auc"]:.3f}')
        
        # Save best model
        if valid_metrics['accuracy'] > best_valid_acc:
            best_valid_acc = valid_metrics['accuracy']
            
            # Save model
            Path('models').mkdir(exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'vocab': vocab,
                'metrics': valid_metrics,
                'args': vars(args)
            }, 'models/sentiment_model_best.pt')
            
            print(f'✓ Saved best model (acc: {best_valid_acc*100:.2f}%)')
    
    # Save final metrics
    final_metrics = evaluate(model, test_loader, criterion, device)
    
    with open('models/metrics.json', 'w') as f:
        json.dump(final_metrics, f, indent=2)
    
    print(f'\n{"="*50}')
    print(f'Training Complete!')
    print(f'Best Validation Accuracy: {best_valid_acc*100:.2f}%')
    print(f'Final Test Metrics:')
    for k, v in final_metrics.items():
        print(f'  {k}: {v:.4f}')
    print(f'{"="*50}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train Sentiment Analysis Model')
    
    # Model hyperparameters
    parser.add_argument('--embedding-dim', type=int, default=100)
    parser.add_argument('--hidden-dim', type=int, default=256)
    parser.add_argument('--n-layers', type=int, default=2)
    parser.add_argument('--bidirectional', type=bool, default=True)
    parser.add_argument('--dropout', type=float, default=0.5)
    
    # Training hyperparameters
    parser.add_argument('--learning-rate', type=float, default=0.001)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--max-length', type=int, default=256)
    parser.add_argument('--seed', type=int, default=42)
    
    # Other
    parser.add_argument('--run-name', type=str, default='sentiment-lstm')
    
    args = parser.parse_args()
    
    train(args)
