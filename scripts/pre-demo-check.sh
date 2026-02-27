#!/bin/bash

echo "=========================================="
echo "Live Demo - System Check"
echo "=========================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

echo ""
echo "🔧 SERVICES STATUS"
echo "=================="

# Check Docker
echo -n "Docker daemon... "
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    ((ERRORS++))
fi

# Check Minikube
echo -n "Minikube... "
if minikube status | grep -q "Running"; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "  Run: minikube start"
    ((ERRORS++))
fi

# Check Docker Compose services
echo ""
echo "Docker Compose Services:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "Not running"

# Check Kubeflow pods
echo ""
echo "Kubeflow Pods:"
kubectl get pods -n kubeflow 2>/dev/null | head -10

echo ""
echo "🌐 ENDPOINT CHECKS"
echo "=================="

# Function to check URL
check_url() {
    echo -n "$1 ... "
    if curl -s -o /dev/null -w "%{http_code}" "$2" | grep -q "200\|302"; then
        echo -e "${GREEN}✓ Accessible${NC}"
        return 0
    else
        echo -e "${RED}✗ Not accessible${NC}"
        ((ERRORS++))
        return 1
    fi
}

check_url "Web UI" "http://localhost:8081"
check_url "MLflow" "http://localhost:5001"
check_url "Prometheus" "http://localhost:9090"
check_url "Grafana" "http://localhost:3000"

# Check Kubeflow (may need port-forward)
echo -n "Kubeflow Pipelines ... "
if kubectl get svc ml-pipeline-ui -n kubeflow > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Needs port-forward${NC}"
    echo "  Run: kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80"
else
    echo -e "${RED}✗ Not available${NC}"
fi

echo ""
echo "📊 DATA CHECKS"
echo "=============="

# Check model exists
echo -n "Trained model... "
if [ -f "models/sentiment_model_best.pt" ]; then
    SIZE=$(ls -lh models/sentiment_model_best.pt | awk '{print $5}')
    echo -e "${GREEN}✓ Present ($SIZE)${NC}"
else
    echo -e "${RED}✗ Missing - run training!${NC}"
    ((ERRORS++))
fi

# Check data processed
echo -n "Processed data... "
if [ -f "data/processed/imdb_processed.pkl" ]; then
    echo -e "${GREEN}✓ Present${NC}"
else
    echo -e "${RED}✗ Missing - run preprocessing!${NC}"
    ((ERRORS++))
fi

echo ""
echo "🧪 QUICK FUNCTIONALITY TEST"
echo "==========================="

# Test API
echo -n "API prediction test... "
RESPONSE=$(curl -s -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Great movie!"}' 2>/dev/null)

if echo "$RESPONSE" | grep -q "sentiment"; then
    echo -e "${GREEN}✓ Working${NC}"
    echo "  Response: $RESPONSE"
else
    echo -e "${RED}✗ Failed${NC}"
    ((ERRORS++))
fi

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL SYSTEMS GO - READY FOR DEMO!${NC}"
else
    echo -e "${RED}❌ Found $ERRORS issue(s) - FIX BEFORE DEMO${NC}"
fi
echo "=========================================="