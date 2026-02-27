#!/usr/bin/env python3
"""Training script optimized for Katib metric collection"""
import sys
import os
sys.path.insert(0, '/app')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import argparse
import pickle  # nosemgrep: python.lang.security.audit.pickle.avoid-pickle

from src.training.model import SentimentLSTM
from src.preprocessing.preprocess import IMDBDataset, collate_batch

def train_epoch(model, iterator, optimizer, criterion, device):
    model.train()
    correct = 0
    total = 0
    
    for texts, labels, lengths in iterator:
        texts, labels = texts.to(device), labels.to(device)
        optimizer.zero_grad()
        predictions = model(texts, lengths).squeeze(1)
        loss = criterion(predictions, labels)
        loss.backward()
        optimizer.step()
        
        # Calculate accuracy
        pred_labels = (torch.sigmoid(predictions) > 0.5).float()
        correct += (pred_labels == labels).sum().item()
        total += labels.size(0)
    
    return correct / total

def evaluate(model, iterator, criterion, device):
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for texts, labels, lengths in iterator:
            texts, labels = texts.to(device), labels.to(device)
            predictions = model(texts, lengths).squeeze(1)
            pred_labels = (torch.sigmoid(predictions) > 0.5).float()
            correct += (pred_labels == labels).sum().item()
            total += labels.size(0)
    
    return correct / total

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--learning-rate', type=float, required=True)
    parser.add_argument('--hidden-dim', type=int, required=True)
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--batch-size', type=int, default=64)
    args = parser.parse_args()
    
    device = torch.device('cpu')
    
    # Load data
    with open('/app/data/processed/imdb_processed.pkl', 'rb') as f:
        data_dict = pickle.load(f)
    
    vocab = data_dict['vocab']
    # Use subset for faster training
    train_data = data_dict['train_data'][:5000]
    test_data = data_dict['test_data'][:1000]
    
    train_dataset = IMDBDataset(train_data, vocab, 256)
    test_dataset = IMDBDataset(test_data, vocab, 256)
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, 
                              shuffle=True, collate_fn=collate_batch)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, 
                             shuffle=False, collate_fn=collate_batch)
    
    # Model
    model = SentimentLSTM(
        vocab_size=len(vocab),
        embedding_dim=100,
        hidden_dim=args.hidden_dim,
        output_dim=1,
        n_layers=2,
        bidirectional=True,
        dropout=0.5,
        pad_idx=vocab['<pad>']
    ).to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss()
    
    # Training
    best_acc = 0
    for epoch in range(args.epochs):
        train_acc = train_epoch(model, train_loader, optimizer, criterion, device)
        test_acc = evaluate(model, test_loader, criterion, device)
        
        if test_acc > best_acc:
            best_acc = test_acc
        
        print(f'Epoch {epoch+1}: train_acc={train_acc:.4f} test_acc={test_acc:.4f}')
    
    # CRITICAL: Output in exact format Katib expects
    # Must be on its own line, no other text
    print(f'accuracy={best_acc}')