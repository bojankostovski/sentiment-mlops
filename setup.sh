#!/bin/bash
set -e

echo "================================================"
echo "Sentiment Analysis MLOps - Initial Setup"
echo "================================================"

# Create all directories
echo "Creating project structure..."
mkdir -p {data/processed,models,logs,notebooks}
mkdir -p {tests,docs,scripts,monitoring/{prometheus,grafana}}
mkdir -p {deployment/{kubernetes,docker-compose}}

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download data (will happen during preprocessing)
echo ""
echo "Data will be downloaded during preprocessing step"

# Initialize git
if [ ! -d .git ]; then
    echo ""
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Sentiment Analysis MLOps Platform"
fi

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "================================================"
echo "✅ Setup complete!"
echo "================================================"
echo ""
echo "⚠️  IMPORTANT: Activate virtual environment before running:"
echo "   source venv/bin/activate"
echo ""
echo "Next steps:"
echo "  1. Activate venv:  source venv/bin/activate"
echo "  2. Train model:    ./scripts/train.sh"
echo "  3. Run tests:      ./scripts/test.sh"
echo "  4. Deploy:         ./scripts/deploy.sh docker-compose"
echo ""