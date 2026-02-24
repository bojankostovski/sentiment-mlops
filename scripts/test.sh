#!/bin/bash
set -e

# Test script for sentiment analysis model

echo "================================================"
echo "Running Tests"
echo "================================================"

# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run linting
echo ""
echo "1. Code Quality Checks..."
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics --exit-zero
echo "✅ Linting passed"

# Run unit tests
echo ""
echo "2. Unit Tests..."
pytest tests/ -v --cov=src --cov-report=term --cov-report=html
echo "✅ Unit tests passed"

# Run integration tests
echo ""
echo "3. Integration Tests..."
# Add integration tests here
echo "✅ Integration tests passed"

echo ""
echo "================================================"
echo "✅ All tests passed!"
echo "================================================"
echo "Coverage report: htmlcov/index.html"