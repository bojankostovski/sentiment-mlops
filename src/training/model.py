import torch
import torch.nn as nn

class SentimentLSTM(nn.Module):
    """
    LSTM-based sentiment analysis model
    
    Architecture:
    - Embedding layer
    - Bidirectional LSTM
    - Dropout for regularization
    - Fully connected output layer
    """
    
    def __init__(
        self, 
        vocab_size, 
        embedding_dim=100, 
        hidden_dim=256, 
        output_dim=1,
        n_layers=2, 
        bidirectional=True, 
        dropout=0.5,
        pad_idx=1
    ):
        super().__init__()
        
        self.embedding = nn.Embedding(
            vocab_size, 
            embedding_dim, 
            padding_idx=pad_idx
        )
        
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=n_layers,
            bidirectional=bidirectional,
            dropout=dropout if n_layers > 1 else 0,
            batch_first=True
        )
        
        self.fc = nn.Linear(
            hidden_dim * 2 if bidirectional else hidden_dim, 
            output_dim
        )
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text, text_lengths):
        """
        Args:
            text: [batch_size, seq_len]
            text_lengths: [batch_size]
        
        Returns:
            predictions: [batch_size, 1]
        """
        # text = [batch_size, seq_len]
        embedded = self.dropout(self.embedding(text))
        # embedded = [batch_size, seq_len, embedding_dim]
        
        # Pack sequence
        packed_embedded = nn.utils.rnn.pack_padded_sequence(
            embedded, 
            text_lengths.cpu(), 
            batch_first=True, 
            enforce_sorted=False
        )
        
        packed_output, (hidden, cell) = self.lstm(packed_embedded)
        
        # Concatenate the final forward and backward hidden states
        if self.lstm.bidirectional:
            hidden = self.dropout(
                torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
            )
        else:
            hidden = self.dropout(hidden[-1,:,:])
        
        # hidden = [batch_size, hidden_dim * num_directions]
        
        return self.fc(hidden)


class SentimentCNN(nn.Module):
    """
    CNN-based sentiment analysis model (alternative architecture)
    """
    
    def __init__(
        self, 
        vocab_size, 
        embedding_dim=100,
        n_filters=100,
        filter_sizes=[3, 4, 5],
        output_dim=1,
        dropout=0.5,
        pad_idx=1
    ):
        super().__init__()
        
        self.embedding = nn.Embedding(
            vocab_size, 
            embedding_dim, 
            padding_idx=pad_idx
        )
        
        self.convs = nn.ModuleList([
            nn.Conv2d(
                in_channels=1,
                out_channels=n_filters,
                kernel_size=(fs, embedding_dim)
            )
            for fs in filter_sizes
        ])
        
        self.fc = nn.Linear(len(filter_sizes) * n_filters, output_dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text):
        # text = [batch_size, seq_len]
        embedded = self.embedding(text)
        # embedded = [batch_size, seq_len, embedding_dim]
        
        embedded = embedded.unsqueeze(1)
        # embedded = [batch_size, 1, seq_len, embedding_dim]
        
        conved = [torch.relu(conv(embedded)).squeeze(3) for conv in self.convs]
        # conved_n = [batch_size, n_filters, seq_len - filter_sizes[n] + 1]
        
        pooled = [torch.max_pool1d(conv, conv.shape[2]).squeeze(2) for conv in conved]
        # pooled_n = [batch_size, n_filters]
        
        cat = self.dropout(torch.cat(pooled, dim=1))
        # cat = [batch_size, n_filters * len(filter_sizes)]
        
        return self.fc(cat)