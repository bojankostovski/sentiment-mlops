#!/bin/bash
cd ~/MLOps/final_project
echo "Starting MLOps Platform..."
docker-compose up -d
echo ""
echo "✅ Services started!"
echo ""
echo "Access your services at:"
echo "  🎬 Web UI:       http://localhost:8081"
echo "  📊 MLflow:       http://localhost:5001"
echo "  📈 Prometheus:   http://localhost:9090"
echo "  📉 Grafana:      http://localhost:3000"
echo ""
docker-compose ps
