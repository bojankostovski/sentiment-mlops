from flask import Flask, request, jsonify, Response
import torch
import pickle  # nosemgrep: python.lang.security.audit.pickle.avoid-pickle
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os

app = Flask(__name__)

# Prometheus metrics
PREDICTIONS = Counter('model_predictions_total', 'Total predictions made')
PREDICTION_TIME = Histogram('model_prediction_duration_seconds', 'Prediction duration')
POSITIVE_PREDICTIONS = Counter('model_positive_predictions_total', 'Positive sentiment predictions')
NEGATIVE_PREDICTIONS = Counter('model_negative_predictions_total', 'Negative sentiment predictions')

# Global variables
model = None
vocab = None
device = None
MAX_LENGTH = 256

def load_model(model_path='models/sentiment_model_best.pt'):
    """Load trained model"""
    global model, vocab, device
    
    print(f"Loading model from {model_path}...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    checkpoint = torch.load(model_path, map_location=device)
    vocab = checkpoint['vocab']
    args = checkpoint['args']
    
    # Import model class
    import sys
    sys.path.insert(0, '/app/src/training')
    from model import SentimentLSTM
    
    model = SentimentLSTM(
        vocab_size=len(vocab),
        embedding_dim=args['embedding_dim'],
        hidden_dim=args['hidden_dim'],
        output_dim=1,
        n_layers=args['n_layers'],
        bidirectional=args['bidirectional'],
        dropout=args['dropout'],
        pad_idx=vocab['<pad>']
    )
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    print(f"Model loaded successfully on {device}")
    print(f"Vocabulary size: {len(vocab)}")

def simple_tokenize(text):
    """Simple word tokenization"""
    return text.lower().split()

def predict_sentiment(text):
    """Predict sentiment of text"""
    # Tokenize
    tokens = simple_tokenize(text)[:MAX_LENGTH]
    
    # Numericalize
    numericalized = [vocab.get(token, vocab['<unk>']) for token in tokens]
    
    # Pad
    numericalized = numericalized + [vocab['<pad>']] * (MAX_LENGTH - len(numericalized))
    
    # Convert to tensor
    tensor = torch.LongTensor(numericalized).unsqueeze(0).to(device)
    length = torch.LongTensor([len(tokens)])
    
    # Predict
    with torch.no_grad():
        prediction = model(tensor, length)
        probability = torch.sigmoid(prediction).item()
    
    return {
        'sentiment': 'positive' if probability > 0.5 else 'negative',
        'confidence': probability if probability > 0.5 else 1 - probability,
        'probability': probability
    }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'vocab_size': len(vocab) if vocab else 0
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint"""
    start_time = time.time()
    
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (max 5000 characters)'}), 400
        
        # Make prediction
        result = predict_sentiment(text)
        
        # Update metrics
        PREDICTIONS.inc()
        if result['sentiment'] == 'positive':
            POSITIVE_PREDICTIONS.inc()
        else:
            NEGATIVE_PREDICTIONS.inc()
        
        duration = time.time() - start_time
        PREDICTION_TIME.observe(duration)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    model_path = os.getenv('MODEL_PATH', '/app/models/sentiment_model_best.pt')
    load_model(model_path)
    
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
