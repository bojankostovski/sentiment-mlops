#!/bin/bash

echo "=========================================="
echo "Starting All Services for Live Demo"
echo "=========================================="

# Start Minikube
echo ""
echo "🚀 Starting Minikube..."
minikube start --cpus=10 --memory=12288 --memory=15972 --disk-size=50g --driver=docker --container-runtime=containerd
sleep 5

# Start Docker Compose services
echo ""
echo "🐳 Starting Docker Compose services..."
cd ~/MLOps/final_project
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready (30 seconds)..."
sleep 30

# Check status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "☸️  Kubeflow Status:"
kubectl get pods -n kubeflow | grep -E "NAME|Running" | head -10

# Port forward Kubeflow (in background)
echo ""
echo "🔗 Setting up Kubeflow port-forward..."
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80 > /dev/null 2>&1 &
PORTFORWARD_PID=$!
echo "Port-forward PID: $PORTFORWARD_PID"
sleep 5

echo ""
echo "=========================================="
echo "✅ ALL SERVICES STARTED"
echo "=========================================="
echo ""
echo "🌐 Access URLs:"
echo "  Web UI:              http://localhost:8081"
echo "  Kubeflow Pipelines:  http://localhost:8080"
echo "  Grafana:             http://localhost:3000"
echo "  Prometheus:          http://localhost:9090"
echo "  MLflow:              http://localhost:5001"
echo ""
echo "💡 To stop port-forward: kill $PORTFORWARD_PID"
echo "💡 To stop all: docker-compose down && minikube stop"
echo ""
echo "🎬 READY FOR LIVE DEMO!"
echo ""