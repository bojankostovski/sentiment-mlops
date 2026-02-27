# Sentiment Analysis MLOps Platform

End-to-end MLOps pipeline for sentiment analysis using PyTorch, Kubeflow, and Kubernetes.

[![CI/CD](https://github.com/bojankostovski/sentiment-mlops/actions/workflows/mlops-complete.yaml/badge.svg)](https://github.com/bojankostovski/sentiment-mlops/actions)
[![Security](https://img.shields.io/badge/security-passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)]()

---

## 🎯 Project Overview

A complete, production-ready MLOps system demonstrating:

- **Machine Learning:** Bidirectional LSTM for movie review sentiment classification (80.6% accuracy)
- **Kubeflow Integration:** Automated pipelines with Katib hyperparameter optimization
- **Multi-Platform Deployment:** Kubernetes and Docker Compose
- **CI/CD:** Automated security scanning, testing, and deployment
- **Monitoring:** Real-time metrics with Prometheus and Grafana
- **Security:** Multi-layer scanning with zero critical vulnerabilities

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Kubernetes (Minikube for local)
- 8GB+ RAM recommended

### 5-Minute Setup
```bash
# Clone repository
git clone https://github.com/yourusername/sentiment-mlops.git
cd sentiment-mlops

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Train model
./scripts/train.sh

# Deploy services
docker-compose up -d

# Access web UI
open http://localhost:8081
```

**That's it!** 🎉

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 80.6% |
| **F1 Score** | 0.827 |
| **Precision** | 74.6% |
| **Recall** | 92.7% |
| **AUC-ROC** | 0.909 |
| **Latency (p50)** | ~25ms |

Trained on 50,000 IMDB movie reviews using Katib-optimized hyperparameters.

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────┐
│                  USER INTERFACE                      │
│              http://localhost:8081                   │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│               KUBEFLOW PIPELINE                      │
├─────────────────────────────────────────────────────┤
│  1. Data Preprocessing (IMDB dataset)               │
│  2. Hyperparameter Tuning (Katib)                   │
│  3. Model Training (PyTorch LSTM)                   │
│  4. Model Evaluation (Metrics validation)           │
│  5. Model Deployment (Multi-platform)               │
│  6. Monitoring Setup (Prometheus/Grafana)           │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│                 MODEL SERVING                        │
├─────────────────────────────────────────────────────┤
│  Flask REST API + PyTorch Model                     │
│  • POST /predict - Sentiment analysis               │
│  • POST /add_review - Store review                  │
│  • GET /movie/{name} - Get recommendations          │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│              MONITORING STACK                        │
├─────────────────────────────────────────────────────┤
│  • Prometheus - Metrics collection                  │
│  • Grafana - Visualization                          │
│  • MLflow - Experiment tracking                     │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 Key Features

### ✅ Kubeflow Integration

- **Katib HPO:** Automated hyperparameter optimization
  - Random search across learning rate and hidden dimensions
  - 4 trials executed, best parameters discovered
  - Results: LR=0.003, Hidden=384

- **Kubeflow Pipelines:** 6-component workflow
  - Successfully uploaded and executed
  - End-to-end automation from data to deployment

### ✅ Multi-Platform Deployment

**Kubernetes (Production):**
- Auto-scaling (HPA: 1-5 pods)
- Rolling updates (zero downtime)
- Health checks and resource limits
- Production-grade orchestration

**Docker Compose (Development):**
- Lightweight single-host deployment
- Fast iteration and testing
- Lower resource requirements

**Portability:** Same Docker image, zero code changes

### ✅ Security & CI/CD

**5-Layer Security Scanning:**
1. SAST (Semgrep)
2. Secret Detection (Gitleaks + TruffleHog)
3. Dependency Scanning (Safety)
4. Container Scanning (Trivy + Grype)
5. SBOM Generation (CycloneDX)

**Results:** Zero critical vulnerabilities, 82/100 security score

**CI/CD Pipeline:**
- GitHub Actions automation
- Automated testing (85%+ coverage)
- Security gates (fails on CRITICAL)
- Automated deployment to staging

### ✅ Monitoring & Observability

- **Real-time metrics** via Prometheus
- **Visual dashboards** via Grafana
- **Experiment tracking** via MLflow
- **Alerting** on performance degradation

---

## 📁 Project Structure
```
sentiment-mlops/
├── README.md                       # This file
├── RUNBOOK.md                      # Complete execution guide
├── REVIEW.md                       # Self-assessment
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Docker Compose config
├── Dockerfile                      # Container definition
│
├── .github/workflows/
│   └── mlops-complete.yaml         # CI/CD pipeline
│
├── src/
│   ├── preprocessing/
│   │   └── preprocess.py           # Data preprocessing
│   ├── training/
│   │   ├── train.py                # Model training
│   │   └── model.py                # LSTM architecture
│   └── serving/
│       ├── enhanced_inference.py   # Flask API
│       └── static/
│           └── index.html          # Web UI
│
├── pipelines/
│   └── sentiment_pipeline_fixed.py # Kubeflow pipeline
│
├── deployment/
│   ├── kubernetes/
│   │   ├── deployment.yaml         # K8s deployment
│   │   ├── service.yaml            # K8s service
│   │   └── hpa.yaml                # Auto-scaling
│   └── katib/
│       └── sentiment-hpo-fixed.yaml # Katib experiment
│
├── monitoring/
│   ├── prometheus.yml              # Prometheus config
│   └── grafana/dashboards/         # Grafana dashboards
│
├── tests/
│   ├── test_model.py               # Model tests
│   ├── test_preprocessing.py       # Data pipeline tests
│   └── test_api.py                 # API tests
│
├── docs/
│   ├── ARCHITECTURE.md             # System design
│   ├── COST_ANALYSIS.md            # Infrastructure costs
│   ├── SECURITY_AUDIT.md           # Security assessment
│   ├── CICD_REQUIREMENTS.md        # CI/CD compliance
│   └── evidence/                   # Screenshots
│
├── models/                         # Trained models
│   ├── sentiment_model_best.pt     # Best model (80.6%)
│   └── metrics.json                # Performance metrics
│
└── scripts/
    ├── train.sh                    # Training script
    ├── deploy.sh                   # Deployment script
    └── security-scan.sh            # Local security checks
```

---

## 🔧 Usage

### Train Model
```bash
# Activate environment
source venv/bin/activate

# Train with default parameters
./scripts/train.sh

# Or with custom parameters
python src/training/train.py \
  --learning-rate 0.003 \
  --hidden-dim 384 \
  --epochs 5
```

### Run Katib HPO
```bash
# Start Kubernetes
minikube start --cpus=6 --memory=12288

# Load Docker image
docker build -t sentiment-analysis:latest .
minikube image load sentiment-analysis:latest

# Deploy Katib experiment
kubectl apply -f deployment/katib/sentiment-hpo-fixed.yaml

# Monitor
kubectl get experiments -n kubeflow -w
kubectl get trials -n kubeflow
```

### Deploy Kubeflow Pipeline
```bash
# Access Kubeflow UI
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80

# Open browser: http://localhost:8080
# Upload: sentiment_pipeline_fixed.yaml
# Create and run experiment
```

### Serve Model
```bash
# Docker Compose
docker-compose up -d

# Test API
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing movie!"}'

# Web UI
open http://localhost:8081
```

### Monitor
```bash
# Grafana dashboards
open http://localhost:3000  # admin/admin

# Prometheus metrics
open http://localhost:9090

# MLflow experiments
open http://localhost:5001
```

---

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Current Coverage:** 85%+

---

## 🔒 Security

### Scan Results

| Tool | Status | Critical | High | Medium |
|------|--------|----------|------|--------|
| **Semgrep** | ✅ Pass | 0 | 0 | 3 |
| **Gitleaks** | ✅ Pass | 0 | 0 | 0 |
| **Safety** | ✅ Pass | 0 | 0 | 5 |
| **Trivy** | ⚠️ Warning | 0 | 8 | 15 |

**Security Score:** 82/100 🟢

### Run Security Scans Locally
```bash
./scripts/security-scan.sh

# Or individual scans:
semgrep --config=auto src/
gitleaks detect --source .
safety check
trivy image sentiment-analysis:latest
```

---

## 💰 Cost Analysis

### Local Deployment
**Cost:** $0/month (runs on personal hardware)

### Cloud Deployment Estimates

| Platform | Monthly Cost | Use Case |
|----------|--------------|----------|
| **Development** | $25 | Single instance, basic monitoring |
| **Staging** | $75 | 2 instances, full monitoring |
| **AWS EKS Production** | $163 | HA, auto-scaling, monitoring |
| **GCP GKE Production** | $74 | HA, auto-scaling, monitoring |
| **GCP Optimized** | $45 | Spot instances, right-sizing |

**Full Analysis:** See `docs/COST_ANALYSIS.md`

---

## 📈 Performance Metrics

### Model Metrics
- Training time: ~15 minutes (CPU)
- Model size: 80MB
- Parameters: 2.6M
- Vocabulary: 46,159 words

### Inference Performance
- Latency (p50): 25ms
- Latency (p95): 45ms
- Latency (p99): 75ms
- Throughput: 100+ req/s

### Resource Usage
- Memory: 304MB (runtime)
- CPU: 15% average
- Startup time: 10s

---

## 🛠️ Development

### Setup Development Environment
```bash
# Clone and setup
git clone https://github.com/bojankostovski/sentiment-mlops.git
cd sentiment-mlops
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run linting
flake8 src/
black src/
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [RUNBOOK.md](RUNBOOK.md) | Complete setup and execution guide |
| [REVIEW.md](REVIEW.md) | Self-assessment and project status |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and design |
| [docs/COST_ANALYSIS.md](docs/COST_ANALYSIS.md) | Infrastructure cost breakdown |
| [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) | Security assessment |
| [docs/CICD_REQUIREMENTS.md](docs/CICD_REQUIREMENTS.md) | CI/CD compliance |

---

## 🎯 Project Goals Achieved

✅ **Dataset & Model**
- IMDB dataset (50k reviews)
- PyTorch LSTM (80.6% accuracy)
- Reproducible training pipeline

✅ **Kubeflow Pipeline**
- 6-component automated workflow
- Katib hyperparameter optimization
- Successfully executed end-to-end

✅ **Security & CI/CD**
- 5-layer security scanning
- Automated GitHub Actions pipeline
- Zero critical vulnerabilities

✅ **Multi-Cloud Portability**
- Kubernetes deployment
- Docker Compose deployment
- Cloud-ready architecture

✅ **Documentation**
- Comprehensive guides
- Architecture diagrams
- Evidence and screenshots

---

## 🏆 Key Achievements

### Technical Excellence
- **80.6% Model Accuracy** - Exceeds baseline expectations
- **Zero Critical Vulnerabilities** - Comprehensive security
- **85%+ Test Coverage** - High-quality codebase
- **Sub-second Inference** - Production-ready performance

### MLOps Maturity
- **Automated HPO** - Katib-based optimization
- **End-to-End Pipeline** - Kubeflow integration
- **Multi-Platform** - Kubernetes + Docker Compose
- **Full Observability** - Prometheus + Grafana + MLflow

### Real-World Skills
- **Infrastructure Troubleshooting** - MySQL, Argo, Kubernetes
- **Problem Solving** - Multiple infrastructure bugs resolved
- **Professional Documentation** - Enterprise-grade docs
- **DevSecOps** - Security-first approach

---

## 🐛 Known Limitations

### Current Limitations
1. **In-memory review storage** - Resets on restart (would use PostgreSQL in production)
2. **Manual retraining trigger** - Code exists, not scheduled (would use CronJob)
3. **Katib metrics collection** - Timing issues in local setup (works in production)

### Future Enhancements
1. **Model Architecture** - Upgrade to Transformer (BERT/RoBERTa) for +5-10% accuracy
2. **Distributed Training** - Multi-GPU support for faster training
3. **A/B Testing** - Canary deployments and feature flags
4. **Advanced Monitoring** - Distributed tracing (Jaeger), APM

See [REVIEW.md](REVIEW.md) for complete list.

---

## 🆘 Troubleshooting

### Common Issues

**Services won't start:**
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

**Kubeflow pods not running:**
```bash
kubectl get pods -n kubeflow
# Check individual pod logs for errors
```

**Model accuracy low:**
- Ensure full dataset downloaded
- Verify preprocessing completed
- Check hyperparameters match Katib results

**Full Troubleshooting Guide:** See [RUNBOOK.md](RUNBOOK.md#13-troubleshooting)

---

**Author:** Bojan Kostovski  
**Repository:** https://github.com/bojankostovski/sentiment-mlops  
**Issues:** GitHub Issues  
**Documentation:** `docs/` directory

---

## 📄 License

This project is created for educational purposes as part of MLOps Academy Final Project.

---

## 🙏 Acknowledgments

- **IMDB Dataset:** HuggingFace Datasets
- **Kubeflow:** Kubeflow community
- **MLOps Academy:** Course instructors and materials
- **Open Source:** PyTorch, Kubernetes, Prometheus, Grafana communities

---

## 📊 Project Stats

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/sentiment-mlops)
![GitHub repo size](https://img.shields.io/github/repo-size/yourusername/sentiment-mlops)
![Lines of code](https://img.shields.io/tokei/lines/github/yourusername/sentiment-mlops)

**Total Lines of Code:** ~5,000  
**Documentation:** 9 documents, 15+ screenshots  
**Test Coverage:** 85%+  
**Security Score:** 82/100  
**Time Investment:** ~40 hours

---
