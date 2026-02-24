# Sentiment Analysis MLOps Platform

Complete end-to-end MLOps solution for sentiment analysis using PyTorch, Kubeflow, and Kubernetes.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Security](https://img.shields.io/badge/Security-Passing-brightgreen)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Security](#security)
- [Development](#development)
- [Documentation](#documentation)

---

## 🎯 Overview

This project demonstrates a production-ready MLOps pipeline for sentiment analysis of movie reviews (IMDB dataset). It showcases best practices in machine learning operations, including automated training, deployment, monitoring, and security.

**Model**: Bidirectional LSTM for binary sentiment classification  
**Dataset**: IMDB 50k movie reviews  
**Accuracy**: ~89%  
**Latency**: <50ms per prediction

---

## ✨ Features

### Machine Learning
- ✅ PyTorch-based LSTM model
- ✅ Automated data preprocessing
- ✅ Hyperparameter tracking with MLflow
- ✅ Model versioning and registry

### MLOps Pipeline
- ✅ Kubeflow Pipelines for orchestration
- ✅ Automated training workflow
- ✅ Model evaluation and validation
- ✅ Conditional deployment based on metrics

### Multi-Platform Deployment
- ✅ Kubernetes (Production-grade orchestration)
- ✅ Docker Compose (Development/Simple deployment)
- ✅ Container portability across platforms

### Security & Compliance
- ✅ SAST with Semgrep
- ✅ Secret detection (Gitleaks, TruffleHog)
- ✅ Container scanning (Trivy, Grype)
- ✅ Dependency vulnerability scanning (Safety)
- ✅ SBOM generation (CycloneDX)
- ✅ Non-root containers
- ✅ Security contexts & pod policies

### CI/CD
- ✅ GitHub Actions workflow
- ✅ Automated testing (unit, integration)
- ✅ Code quality checks (flake8, black)
- ✅ Multi-stage deployment (staging → production)
- ✅ Rollback capabilities

### Monitoring & Observability
- ✅ Prometheus metrics collection
- ✅ Grafana dashboards
- ✅ Custom application metrics
- ✅ Health checks and alerts

---

## 🏗️ Architecture
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Dataset    │────▶│ Preprocessing│────▶│   Training   │
│  (IMDB 50k)  │     │  & Vocab     │     │  (PyTorch)   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Monitoring  │◀────│  Deployment  │◀────│  Evaluation  │
│ (Prometheus) │     │ (K8s/Compose)│     │  & Testing   │
└──────────────┘     └──────────────┘     └──────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Minikube (for Kubernetes deployment)
- 8GB RAM minimum
- 10GB disk space

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/sentiment-mlops.git
cd sentiment-mlops

# Install dependencies
pip install -r requirements.txt

# Download and preprocess data
python src/preprocessing/preprocess.py
```

### Train Model
```bash
# Option 1: Quick training (2 epochs)
./scripts/train.sh

# Option 2: Custom parameters
EPOCHS=5 BATCH_SIZE=64 LEARNING_RATE=0.001 ./scripts/train.sh

# Option 3: Direct Python
python src/training/train.py --epochs 5 --batch-size 64
```

### Deploy

**Option A: Docker Compose (Recommended for Development)**
```bash
./scripts/deploy.sh docker-compose staging
```

Access services:
- Model API: http://localhost:8080
- MLflow: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**Option B: Kubernetes (Production-like)**
```bash
# Start minikube
minikube start --cpus=4 --memory=8192

# Deploy
./scripts/deploy.sh kubernetes staging

# Get service URL
minikube service sentiment-model -n sentiment-analysis --url
```

### Test API
```bash
# Positive sentiment
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie was absolutely fantastic!"}'

# Negative sentiment
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Terrible movie, waste of time."}'
```

---

## 📦 Deployment

### Docker Compose
```bash
docker-compose up -d
```

Services included:
- `model-server`: Flask API serving predictions
- `mlflow`: Experiment tracking
- `prometheus`: Metrics collection
- `grafana`: Visualization dashboards

### Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
```

Features:
- Auto-scaling (HPA)
- Rolling updates
- Health checks
- Resource limits
- Security contexts

---

## 📊 Monitoring

### Metrics

Access Prometheus: http://localhost:9090

**Available metrics:**
- `model_predictions_total` - Total predictions made
- `model_prediction_duration_seconds` - Prediction latency
- `model_positive_predictions_total` - Positive predictions
- `model_negative_predictions_total` - Negative predictions

### Dashboards

Access Grafana: http://localhost:3000
- Username: `admin`
- Password: `admin`

**Pre-configured dashboards:**
- Prediction rate over time
- Latency percentiles (p50, p95, p99)
- Sentiment distribution
- Error rates

---

## 🔒 Security

### Security Scans
```bash
# Run all security scans
./scripts/security-scan.sh

# Individual scans
semgrep --config=auto .
trivy image sentiment-analysis:latest
safety check
gitleaks detect
```

### Security Report

See [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) for complete audit.

**Summary:**
- ✅ No critical vulnerabilities
- ✅ All containers run as non-root
- ✅ Input validation implemented
- ✅ Secrets managed securely
- ✅ SBOM generated

---

## 💻 Development

### Project Structure
```
.
├── src/
│   ├── preprocessing/      # Data preprocessing
│   ├── training/          # Model training
│   └── serving/           # Inference API
├── pipelines/             # Kubeflow pipelines
├── deployment/
│   ├── kubernetes/        # K8s manifests
│   └── docker-compose.yml # Compose config
├── monitoring/            # Prometheus & Grafana
├── tests/                 # Unit & integration tests
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

### Running Tests
```bash
./scripts/test.sh
```

### Code Quality
```bash
# Format code
black src/

# Lint
flake8 src/

# Type check
mypy src/
```

---

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Cost Analysis](docs/COST_ANALYSIS.md) - Infrastructure costs
- [Security Audit](docs/SECURITY_AUDIT.md) - Security assessment
- [Multi-Platform](docs/MULTI_PLATFORM.md) - Deployment strategies

---

## 🔧 Configuration

### Environment Variables
```bash
# Model configuration
MODEL_PATH=/app/models/sentiment_model_best.pt

# API configuration
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=8080

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Accuracy | 89% |
| F1 Score | 0.88 |
| Inference Latency (p50) | 25ms |
| Inference Latency (p95) | 45ms |
| Throughput | 100 req/s |
| Model Size | 25 MB |

---

## 🗺️ Roadmap

- [ ] A/B testing framework
- [ ] Automated retraining on data drift
- [ ] Multi-model deployment
- [ ] GPU support
- [ ] Streaming predictions (Kafka)
- [ ] Feature store integration

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Authors

- Your Name - Initial work

---

## 🙏 Acknowledgments

- IMDB dataset from Stanford AI Lab
- PyTorch team for excellent framework
- Kubeflow community
- All open-source contributors

---

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/sentiment-mlops/issues)
- Email: your.email@example.com

---

