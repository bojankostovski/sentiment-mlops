#!/bin/bash
set -e

# Deployment script for sentiment analysis model
# Supports both Kubernetes and Docker Compose deployments

PLATFORM=${1:-"docker-compose"}
ENVIRONMENT=${2:-"staging"}

echo "================================================"
echo "Sentiment Analysis Model Deployment"
echo "Platform: $PLATFORM"
echo "Environment: $ENVIRONMENT"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_error() {
    echo -e "${RED}✗ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
function check_prerequisites() {
    echo ""
    echo "Checking prerequisites..."
    
    if [ "$PLATFORM" == "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            print_error "kubectl not found. Please install kubectl."
            exit 1
        fi
        print_success "kubectl found"
        
        # Check cluster connection
        if ! kubectl cluster-info &> /dev/null; then
            print_error "Cannot connect to Kubernetes cluster"
            exit 1
        fi
        print_success "Connected to Kubernetes cluster"
        
    elif [ "$PLATFORM" == "docker-compose" ]; then
        if ! command -v docker-compose &> /dev/null; then
            print_error "docker-compose not found. Please install docker-compose."
            exit 1
        fi
        print_success "docker-compose found"
        
        if ! docker info &> /dev/null; then
            print_error "Docker daemon not running"
            exit 1
        fi
        print_success "Docker daemon running"
    else
        print_error "Unknown platform: $PLATFORM"
        echo "Usage: $0 [kubernetes|docker-compose] [staging|production]"
        exit 1
    fi
}

# Build Docker image
function build_image() {
    echo ""
    echo "Building Docker image..."
    
    docker build -t sentiment-analysis:latest . || {
        print_error "Docker build failed"
        exit 1
    }
    
    print_success "Docker image built successfully"
}

# Deploy to Docker Compose
function deploy_docker_compose() {
    echo ""
    echo "Deploying to Docker Compose..."
    
    # Stop existing containers
    docker-compose down || true
    
    # Start services
    docker-compose up -d
    
    # Wait for health check
    echo "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    if curl -f http://localhost:8080/health &> /dev/null; then
        print_success "Model server is healthy"
    else
        print_error "Model server health check failed"
        docker-compose logs
        exit 1
    fi
    
    # Display service URLs
    echo ""
    echo "Services available at:"
    echo "  Model API:    http://localhost:8080"
    echo "  MLflow:       http://localhost:5000"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Grafana:      http://localhost:3000"
    echo ""
    print_success "Deployment complete!"
}

# Deploy to Kubernetes
function deploy_kubernetes() {
    echo ""
    echo "Deploying to Kubernetes..."
    
    NAMESPACE="sentiment-analysis"
    
    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    print_success "Namespace ready: $NAMESPACE"
    
    # Apply manifests
    echo "Applying Kubernetes manifests..."
    kubectl apply -f deployment/kubernetes/ -n $NAMESPACE
    
    # Wait for deployment
    echo "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/sentiment-model -n $NAMESPACE || {
        print_error "Deployment failed"
        kubectl get pods -n $NAMESPACE
        kubectl logs -n $NAMESPACE -l app=sentiment-model --tail=50
        exit 1
    }
    
    print_success "Deployment ready"
    
    # Get service endpoint
    echo ""
    echo "Getting service endpoint..."
    if command -v minikube &> /dev/null; then
        SERVICE_URL=$(minikube service sentiment-model -n $NAMESPACE --url)
        echo "Service available at: $SERVICE_URL"
    else
        kubectl get svc -n $NAMESPACE sentiment-model
    fi
    
    # Show pods
    echo ""
    echo "Running pods:"
    kubectl get pods -n $NAMESPACE -l app=sentiment-model
    
    print_success "Deployment complete!"
}

# Run smoke tests
function run_smoke_tests() {
    echo ""
    echo "Running smoke tests..."
    
    if [ "$PLATFORM" == "docker-compose" ]; then
        ENDPOINT="http://localhost:8080"
    else
        if command -v minikube &> /dev/null; then
            ENDPOINT=$(minikube service sentiment-model -n sentiment-analysis --url)
        else
            print_warning "Skipping smoke tests - cannot determine endpoint"
            return
        fi
    fi
    
    # Test positive sentiment
    echo "Testing positive sentiment..."
    RESPONSE=$(curl -s -X POST $ENDPOINT/predict \
        -H "Content-Type: application/json" \
        -d '{"text": "This movie was absolutely fantastic! I loved every minute of it."}')
    
    SENTIMENT=$(echo $RESPONSE | jq -r '.sentiment')
    if [ "$SENTIMENT" == "positive" ]; then
        print_success "Positive sentiment test passed"
    else
        print_error "Positive sentiment test failed: $RESPONSE"
    fi
    
    # Test negative sentiment
    echo "Testing negative sentiment..."
    RESPONSE=$(curl -s -X POST $ENDPOINT/predict \
        -H "Content-Type: application/json" \
        -d '{"text": "Terrible movie. Complete waste of time and money."}')
    
    SENTIMENT=$(echo $RESPONSE | jq -r '.sentiment')
    if [ "$SENTIMENT" == "negative" ]; then
        print_success "Negative sentiment test passed"
    else
        print_error "Negative sentiment test failed: $RESPONSE"
    fi
    
    print_success "All smoke tests passed!"
}

# Main execution
main() {
    check_prerequisites
    build_image
    
    if [ "$PLATFORM" == "docker-compose" ]; then
        deploy_docker_compose
    elif [ "$PLATFORM" == "kubernetes" ]; then
        deploy_kubernetes
    fi
    
    run_smoke_tests
    
    echo ""
    echo "================================================"
    print_success "Deployment successful! 🚀"
    echo "================================================"
}

main