from flask import Flask, request, jsonify, Response, send_from_directory
import torch
import pickle
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os
from collections import defaultdict
from datetime import datetime

app = Flask(__name__, static_folder='static')

# In-memory movie database
movies_db = defaultdict(lambda: {
    "reviews": [],
    "positive_count": 0,
    "negative_count": 0
})

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

def simple_tokenize(text):
    """Simple word tokenization"""
    return text.lower().split()

def predict_sentiment(text):
    """Predict sentiment of text"""
    tokens = simple_tokenize(text)[:MAX_LENGTH]
    numericalized = [vocab.get(token, vocab['<unk>']) for token in tokens]
    numericalized = numericalized + [vocab['<pad>']] * (MAX_LENGTH - len(numericalized))
    
    tensor = torch.LongTensor(numericalized).unsqueeze(0).to(device)
    length = torch.LongTensor([len(tokens)])
    
    with torch.no_grad():
        prediction = model(tensor, length)
        probability = torch.sigmoid(prediction).item()
    
    return {
        'sentiment': 'positive' if probability > 0.5 else 'negative',
        'confidence': probability if probability > 0.5 else 1 - probability,
        'probability': probability
    }

@app.route('/')
def index():
    """Serve the web UI"""
    return send_from_directory('static', 'index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'movies_tracked': len(movies_db)
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Simple prediction endpoint"""
    start_time = time.time()
    
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        result = predict_sentiment(text)
        
        PREDICTIONS.inc()
        if result['sentiment'] == 'positive':
            POSITIVE_PREDICTIONS.inc()
        else:
            NEGATIVE_PREDICTIONS.inc()
        
        duration = time.time() - start_time
        PREDICTION_TIME.observe(duration)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_review', methods=['POST'])
def add_review():
    """Add a review for a specific movie"""
    try:
        data = request.json
        movie = data.get('movie', '').lower()
        review_text = data.get('review', '')
        
        if not movie or not review_text:
            return jsonify({'error': 'Movie name and review required'}), 400
        
        # Predict sentiment
        sentiment_result = predict_sentiment(review_text)
        
        # Store review
        movies_db[movie]["reviews"].append({
            "text": review_text,
            "sentiment": sentiment_result['sentiment'],
            "confidence": sentiment_result['confidence'],
            "timestamp": datetime.now().isoformat()
        })
        
        # Update counts
        if sentiment_result['sentiment'] == 'positive':
            movies_db[movie]["positive_count"] += 1
        else:
            movies_db[movie]["negative_count"] += 1
        
        return jsonify({
            "movie": movie,
            "review_added": True,
            "sentiment": sentiment_result['sentiment'],
            "total_reviews": len(movies_db[movie]["reviews"])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/movie/<movie_name>', methods=['GET'])
def get_movie_summary(movie_name):
    """Get summary and recommendation for a movie"""
    movie = movie_name.lower()
    
    if movie not in movies_db:
        return jsonify({'error': f'No reviews found for {movie_name}'}), 404
    
    data = movies_db[movie]
    total = len(data["reviews"])
    positive = data["positive_count"]
    negative = data["negative_count"]
    
    if total == 0:
        return jsonify({'error': 'No reviews yet'}), 404
    
    # Calculate score
    positive_percentage = (positive / total) * 100
    score = (positive / total) * 10
    
    # Generate recommendation
    if positive_percentage >= 80:
        advice = "🌟 Highly recommended! Most viewers loved it."
    elif positive_percentage >= 60:
        advice = "👍 Worth watching. Generally positive reviews."
    elif positive_percentage >= 40:
        advice = "🤔 Mixed reviews. Watch at your own discretion."
    else:
        advice = "👎 Not recommended. Most viewers disliked it."
    
    return jsonify({
        "movie": movie_name,
        "total_reviews": total,
        "positive_reviews": positive,
        "negative_reviews": negative,
        "positive_percentage": round(positive_percentage, 1),
        "score": round(score, 1),
        "recommendation": advice,
        "recent_reviews": [
            {
                "text": r["text"][:100] + "..." if len(r["text"]) > 100 else r["text"],
                "sentiment": r["sentiment"]
            }
            for r in data["reviews"][-5:]
        ]
    })

@app.route('/movies', methods=['GET'])
def list_movies():
    """List all tracked movies"""
    movies = []
    for movie_name, data in movies_db.items():
        total = len(data["reviews"])
        if total > 0:
            positive_pct = (data["positive_count"] / total) * 100
            movies.append({
                "movie": movie_name,
                "total_reviews": total,
                "positive_percentage": round(positive_pct, 1)
            })
    
    movies.sort(key=lambda x: x["total_reviews"], reverse=True)
    
    return jsonify({"movies": movies})

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    model_path = os.getenv('MODEL_PATH', '/app/models/sentiment_model_best.pt')
    load_model(model_path)
    
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
