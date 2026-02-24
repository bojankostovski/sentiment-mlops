#!/bin/bash
set -e

# Training script for sentiment analysis model

echo "================================================"
echo "Sentiment Analysis Model Training"
echo "================================================"

# Default parameters
EPOCHS=${EPOCHS:-5}
BATCH_SIZE=${BATCH_SIZE:-64}
LEARNING_RATE=${LEARNING_RATE:-0.001}
RUN_NAME=${RUN_NAME:-"training-$(date +%Y%m%d-%H%M%S)"}

echo "Configuration:"
echo "  Epochs: $EPOCHS"
echo "  Batch Size: $BATCH_SIZE"
echo "  Learning Rate: $LEARNING_RATE"
echo "  Run Name: $RUN_NAME"
echo ""

# Create directories
mkdir -p data/processed models logs

# Step 1: Preprocess data
echo "Step 1: Preprocessing data..."
python src/preprocessing/preprocess.py || {
    echo "❌ Preprocessing failed"
    exit 1
}
echo "✅ Preprocessing complete"

# Step 2: Train model
echo ""
echo "Step 2: Training model..."
python src/training/train.py \
    --epochs $EPOCHS \
    --batch-size $BATCH_SIZE \
    --learning-rate $LEARNING_RATE \
    --run-name "$RUN_NAME" \
    2>&1 | tee logs/training-$RUN_NAME.log || {
    echo "❌ Training failed"
    exit 1
}
echo "✅ Training complete"

# Step 3: Evaluate model
echo ""
echo "Step 3: Evaluating model..."
if [ -f models/sentiment_model_best.pt ]; then
    echo "✅ Model saved successfully"
    ls -lh models/sentiment_model_best.pt
else
    echo "❌ Model file not found"
    exit 1
fi

# Step 4: Show metrics
echo ""
echo "Step 4: Model metrics:"
if [ -f models/metrics.json ]; then
    cat models/metrics.json | jq .
else
    echo "⚠️  Metrics file not found"
fi

echo ""
echo "================================================"
echo "✅ Training pipeline complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Review training logs: logs/training-$RUN_NAME.log"
echo "  2. Check MLflow UI: http://localhost:5000"
echo "  3. Deploy model: ./scripts/deploy.sh"