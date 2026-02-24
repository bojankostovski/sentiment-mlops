# System Architecture

## Overview

This project implements a complete MLOps pipeline for sentiment analysis using PyTorch, Kubeflow, and Kubernetes.

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  IMDB Dataset (50k reviews)                                 │
│  ├─ Training: 25k samples                                   │
│  └─ Testing: 25k samples                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  PREPROCESSING                              │
├─────────────────────────────────────────────────────────────┤
│  • Tokenization (basic_english)                             │
│  • Vocabulary Building (~25k tokens)                        │
│  • Sequence Padding (max_length=256)                        │
│  • Train/Test Split                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  Bidirectional LSTM                                         │
│  ├─ Embedding: 100d                                         │
│  ├─ Hidden: 256d                                            │
│  ├─ Layers: 2                                               │
│  ├─ Dropout: 0.5                                            │
│  └─ Parameters: ~2.6M                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  TRAINING PIPELINE                          │
├─────────────────────────────────────────────────────────────┤
│  Kubeflow Pipeline Components:                              │
│  1. preprocess_data()                                       │
│  2. train_model()                                           │
│  3. evaluate_model()                                        │
│  4. deploy_model()                                          │
│                                                             │
│  MLflow Tracking:                                           │
│  • Hyperparameters                                          │
│  • Metrics (accuracy, F1, loss)                             │
│  • Model artifacts                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT LAYER                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Platform 1: Kubernetes (Minikube)                          │
│  ├─ Deployment: 2 replicas                                  │
│  ├─ HPA: 1-5 pods                                           │
│  ├─ Service: LoadBalancer                                   │
│  └─ Storage: PVC (2Gi)                                      │
│                                                             │
│  Platform 2: Docker Compose                                 │
│  ├─ Model Server                                            │
│  ├─ MLflow                                                  │
│  ├─ Prometheus                                              │
│  └─ Grafana                                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  SERVING LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  Flask REST API                                             │
│  Endpoints:                                                 │
│  • POST /predict - Get sentiment prediction                │
│  • GET  /health  - Health check                            │
│  • GET  /metrics - Prometheus metrics                      │
│                                                             │
│  Response Format:                                           │
│  {                                                          │
│    "sentiment": "positive",                                 │
│    "confidence": 0.95,                                      │
│    "probability": 0.95                                      │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  MONITORING LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  Prometheus Metrics:                                        │
│  • model_predictions_total                                  │
│  • model_prediction_duration_seconds                        │
│  • model_positive_predictions_total                         │
│  • model_negative_predictions_total                         │
│                                                             │
│  Grafana Dashboards:                                        │
│  • Prediction rate over time                               │
│  • Latency percentiles (p50, p95, p99)                     │
│  • Sentiment distribution                                  │
│  • Error rates                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  GitHub Actions Workflow:                                   │
│  1. Security Scan (Semgrep, Gitleaks)                       │
│  2. Code Quality (flake8, black)                            │
│  3. Unit Tests (pytest)                                     │
│  4. Build Image (Docker)                                    │
│  5. Container Scan (Trivy, Grype)                           │
│  6. SBOM Generation (CycloneDX)                             │
│  7. Deploy Staging (Docker Compose)                         │
│  8. Deploy Production (Kubernetes)                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Model Architecture

**SentimentLSTM**
- Embedding Layer: Maps vocabulary to dense vectors
- Bidirectional LSTM: Processes sequence in both directions
- Dropout: Prevents overfitting
- Fully Connected: Maps to sentiment prediction

**Performance:**
- Accuracy: ~89%
- F1 Score: ~0.88
- Inference Time: <50ms per prediction

### 2. Data Pipeline
```
Raw Text → Tokenization → Numericalization → Padding → Batch → Model
```

**Preprocessing Steps:**
1. Lowercase conversion
2. Basic English tokenization
3. Vocabulary building (min_freq=5)
4. Sequence padding to max_length=256
5. Batch collation with dynamic padding

### 3. Deployment Strategies

#### Kubernetes Deployment
- **Replicas**: 2 (high availability)
- **Auto-scaling**: HPA based on CPU/Memory
- **Storage**: Persistent volume for models
- **Security**: Non-root user, read-only filesystem
- **Health Checks**: Liveness & readiness probes

#### Docker Compose Deployment
- **Services**: Model, MLflow, Prometheus, Grafana
- **Networking**: Bridge network for inter-service communication
- **Volumes**: Persistent storage for data and models
- **Monitoring**: Built-in observability stack

### 4. Monitoring Stack

**Metrics Collection:**
- Prometheus scrapes `/metrics` endpoint every 15s
- Metrics include: prediction count, latency, sentiment distribution

**Visualization:**
- Grafana dashboards for real-time monitoring
- Alerts configured for high error rates

### 5. Security Measures

**Code Security:**
- SAST with Semgrep
- Secret detection with Gitleaks
- Dependency scanning with Safety

**Container Security:**
- Vulnerability scanning with Trivy & Grype
- SBOM generation for supply chain transparency
- Non-root containers
- Minimal base images

**Runtime Security:**
- Network policies
- Resource quotas
- Security contexts
- Read-only filesystems where possible

## Multi-Platform Portability

The solution demonstrates portability through:

1. **Containerization**: Same Docker image runs on both platforms
2. **Configuration**: Environment variables for platform-specific settings
3. **Orchestration**: Kubernetes for production, Docker Compose for development
4. **Monitoring**: Consistent metrics across platforms

## Technology Stack

| Layer | Technology |
|-------|------------|
| ML Framework | PyTorch 2.0 |
| NLP | TorchText |
| Experiment Tracking | MLflow |
| Orchestration | Kubeflow Pipelines |
| Container Runtime | Docker |
| Deployment (Prod) | Kubernetes |
| Deployment (Dev) | Docker Compose |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions |
| Security | Semgrep, Trivy, Gitleaks |

## Scalability Considerations

1. **Horizontal Scaling**: HPA can scale from 1 to 5 pods
2. **Load Balancing**: Kubernetes service distributes traffic
3. **Caching**: Can add Redis for frequent predictions
4. **Batch Processing**: Support for batch inference
5. **Model Versioning**: MLflow tracks multiple versions

## Future Enhancements

1. A/B testing for model versions
2. Automated retraining on data drift
3. Multi-model deployment
4. GPU support for faster inference
5. Real-time streaming predictions
6. Feature store integration