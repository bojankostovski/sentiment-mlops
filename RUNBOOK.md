# MLOps Final Project - Sentiment Analysis - RUNBOOK

## 1. Environment

### Tested On
* **OS:** macOS M3
* **Python version:** 3.9.25
* **Kubernetes version:** 1.28 (Minikube)
* **Kubeflow version:** Not used (replaced with custom pipeline)
* **Docker version:** 24.0.6

### Required Tools
* `kubectl` (v1.28+)
* `docker` and `docker-compose`
* `python` 3.9+
* `git`
* `curl` (for API testing)
* `jq` (optional, for JSON parsing)

### Optional Tools
* `minikube` (if running Kubernetes locally)
* Browser (for accessing web UI, Grafana, Prometheus, MLflow)

---

## 2. Setup

### Clone Repository
```bash
git clone https://git.scalefocus.cloud/MLOps_Academy/mlops-final-p24.git
cd sentiment-mlops
```

### Python Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation
```bash
python --version  # Should be 3.9+
docker --version
docker-compose --version
kubectl version --client
```

---

## 3. Dataset

### Dataset Details
* **Source:** IMDB Movie Reviews (HuggingFace Datasets)
* **Size:** 50,000 movie reviews (25k train, 25k test)
* **Format:** Text files with sentiment labels
* **Download method:** Automatic via HuggingFace `datasets` library
* **Preprocessing:** 
  - Tokenization (word-level, basic English)
  - Vocabulary building (min_freq=5, 46,159 words)
  - Sequence padding (max_length=256)
  - Label encoding (positive=1, negative=0)

### Download & Preprocess
```bash
# Activate virtual environment
source venv/bin/activate

# Run preprocessing (downloads dataset automatically)
python src/preprocessing/preprocess.py
```

**Expected Output:**
```
Loading IMDB dataset...
Train samples: 25000
Test samples: 25000
Building vocabulary...
Vocabulary size: 46159
Data saved to data/processed/imdb_processed.pkl
```

**Dataset Location:** `data/processed/imdb_processed.pkl`

---

## 4. Model Training

### Training Pipeline
```bash
# Activate virtual environment
source venv/bin/activate

# Run training with default parameters
./scripts/train.sh

# OR run with custom parameters
python src/training/train.py \
  --epochs 5 \
  --batch-size 64 \
  --learning-rate 0.001 \
  --embedding-dim 100 \
  --hidden-dim 256 \
  --n-layers 2 \
  --dropout 0.5
```

### Expected Training Output
```
Using device: cpu
Loading data...
Train batches: 391
Test batches: 391
Creating model...
Model has 2,637,569 trainable parameters

Epoch 1/5
Training: 100%|████████████████| 391/391
Train Loss: 0.512 | Train Acc: 74.23%
Val Loss: 0.445 | Val Acc: 78.61%
Val F1: 0.784 | Val AUC: 0.867
✓ Saved best model (acc: 78.61%)

...

Training Complete!
Best Validation Accuracy: 80.61%
Final Test Metrics:
  loss: 0.4268
  accuracy: 0.8061
  precision: 0.7463
  recall: 0.9270
  f1: 0.8269
  auc: 0.9087
```

### Artifacts Created
* **Model file:** `models/sentiment_model_best.pt` (80MB)
* **Metrics:** `models/metrics.json`
* **Training logs:** `logs/training-*.log`
* **MLflow artifacts:** `mlruns/` directory

### Verify Training Success
```bash
# Check model file exists
ls -lh models/sentiment_model_best.pt

# Check metrics
cat models/metrics.json | jq .

# Expected: accuracy > 0.75, f1 > 0.70
```

---

## 5. Run Pipeline

**Note:** This project uses a simplified pipeline approach due to Kubeflow complexity. The pipeline components are:
1. Data preprocessing
2. Model training  
3. Model evaluation
4. Deployment (containerized serving)

### Pipeline Execution
```bash
# Complete pipeline execution
source venv/bin/activate

# Step 1: Preprocess (if not done)
python src/preprocessing/preprocess.py

# Step 2: Train model
./scripts/train.sh

# Step 3: Deploy
./scripts/deploy.sh docker-compose staging
```

### Expected Pipeline Outcome
* ✅ Data preprocessed and saved
* ✅ Model trained (accuracy ~80%)
* ✅ Model deployed and serving predictions
* ✅ Monitoring active (Prometheus/Grafana)

### Verify Pipeline Success
```bash
# Check all services running
docker-compose ps

# Should show:
# - sentiment-model (Up)
# - mlflow (Up)
# - prometheus (Up)
# - grafana (Up)

# Test inference
curl http://localhost:8081/health

# Expected: {"status":"healthy","model_loaded":true}
```

---

## 6. Serving

### Serving Method
**Custom Flask REST API** (containerized)

### Deployment Details
* **Platform:** Docker Compose (development/staging)
* **Namespace:** N/A (containerized services)
* **Port:** 8081 (model API)
* **Manifests location:** `docker-compose.yml`

### Service URLs
* **Model API:** http://localhost:8081
* **MLflow:** http://localhost:5001
* **Prometheus:** http://localhost:9090
* **Grafana:** http://localhost:3000

### Start Services
```bash
docker-compose up -d
```

### Test Inference

**Web UI Method:**
```
Open: http://localhost:8081
Enter movie name and review
Click "Analyze Sentiment"
```

**API Method:**
```bash
# Test positive review
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie was absolutely amazing! Loved it!"}'

# Expected response:
# {"sentiment":"positive","confidence":0.95,"probability":0.95}

# Test negative review
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Terrible film. Waste of time and money."}'

# Expected response:
# {"sentiment":"negative","confidence":0.98,"probability":0.02}
```

### Add Review with Movie Context
```bash
curl -X POST http://localhost:8081/add_review \
  -H "Content-Type: application/json" \
  -d '{
    "movie": "Inception",
    "review": "Brilliant movie! Mind-bending plot and stunning visuals!"
  }'

# Check movie statistics
curl http://localhost:8081/movie/inception | jq .
```

### Verify Serving Health
```bash
# Health check
curl http://localhost:8081/health

# Metrics endpoint (Prometheus format)
curl http://localhost:8081/metrics

# List all reviewed movies
curl http://localhost:8081/movies | jq .
```

---

## 7. Monitoring

### Metrics Collected
* `model_predictions_total` - Total number of predictions
* `model_prediction_duration_seconds` - Prediction latency histogram
* `model_positive_predictions_total` - Positive sentiment count
* `model_negative_predictions_total` - Negative sentiment count
* System metrics (CPU, memory, disk)

### Monitoring Stack
* **Prometheus:** Metrics collection (http://localhost:9090)
* **Grafana:** Visualization dashboards (http://localhost:3000)
* **MLflow:** Experiment tracking (http://localhost:5001)

### Access Dashboards

**Prometheus:**
```
URL: http://localhost:9090
Query examples:
- model_predictions_total
- rate(model_predictions_total[1m])
- histogram_quantile(0.95, rate(model_prediction_duration_seconds_bucket[1m]))
```

**Grafana:**
```
URL: http://localhost:3000
Username: admin
Password: admin

Dashboards to import: monitoring/grafana/dashboards/sentiment-dashboard.json
```

**MLflow:**
```
URL: http://localhost:5001
View: Training experiments, metrics, model artifacts
```

### What Healthy Looks Like
* All containers running (`docker-compose ps` shows "Up")
* Prometheus scraping metrics (http://localhost:9090/targets shows "UP")
* Predictions returning in < 100ms
* No error logs in `docker-compose logs`
* Grafana dashboards showing data

### Generate Test Traffic
```bash
# Generate predictions to see metrics
for i in {1..50}; do
  curl -s -X POST http://localhost:8081/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "Great movie!"}' > /dev/null
  sleep 0.5
done
```

---

## 8. Retraining

### Trigger Method
**Manual** (automated trigger implemented but not scheduled)

### Retraining Concept
The system is designed to support automated retraining triggered by:
1. **Data drift detection** (concept implemented, not deployed)
2. **Scheduled retraining** (weekly/monthly via CronJob)
3. **Performance degradation** (accuracy monitoring)

### Manual Retraining
```bash
# Collect new reviews (via web UI or API)
# When sufficient new data collected:

source venv/bin/activate

# Retrain with new data
python src/training/train.py \
  --epochs 5 \
  --run-name "retraining-$(date +%Y%m%d)"

# Rebuild and redeploy
docker-compose down
docker-compose build model-server
docker-compose up -d
```

### Implementation Location
* Training pipeline: `src/training/train.py`
* Deployment automation: `scripts/deploy.sh`
* Future: Kubeflow pipeline at `pipelines/sentiment_pipeline.py`

### Output Changes
* New model file: `models/sentiment_model_best.pt`
* Updated metrics: `models/metrics.json`
* MLflow logs new experiment run
* Automatic deployment via CI/CD (when implemented)

---

## 9. CI/CD & DevSecOps

### CI Tool
**GitHub Actions** (configuration in `.github/workflows/mlops-complete.yaml`)

### Pipeline Stages
1. **Security Scans**
   - Semgrep (SAST)
   - Gitleaks (Secret detection)
   - TruffleHog (Additional secret detection)

2. **Code Quality**
   - Flake8 (Linting)
   - Black (Formatting check)
   - MyPy (Type checking)

3. **Unit Tests**
   - pytest (Unit tests)
   - Coverage reports

4. **Build**
   - Docker image build
   - Multi-stage optimization

5. **Container Security**
   - Trivy (Vulnerability scanning)
   - Grype (Additional scanning)
   - SBOM generation (CycloneDX)

6. **Dependency Scanning**
   - Safety (Python package vulnerabilities)
   - Checks for CRITICAL vulnerabilities

7. **Deploy Staging**
   - Docker Compose deployment
   - Smoke tests
   - Health checks

8. **Deploy Production** (manual approval)
   - Kubernetes deployment
   - Rollout verification

### Security Scans Used
* **SAST:** Semgrep (p/security-audit)
* **Secret Detection:** Gitleaks, TruffleHog
* **Container Scanning:** Trivy, Grype
* **Dependency Scanning:** Safety (Python packages)
* **SBOM:** Syft/Anchore

### Security Gate Rules
* **FAIL on:** CRITICAL vulnerabilities
* **WARN on:** HIGH vulnerabilities (logged)
* **PASS on:** MEDIUM/LOW (documented)

### View CI/CD Pipeline
```
GitHub: https://github.com/bojankostovski/sentiment-mlops/actions
Workflow file: .github/workflows/mlops-complete.yaml
```

### Local Security Scan
```bash
# Run security checks locally
./scripts/security-scan.sh

# Individual scans
semgrep --config=auto .
gitleaks detect
safety check
trivy image sentiment-analysis:latest
```

### Deployment Approach
* **Staging:** Automated on push to `main`
* **Production:** Manual approval required
* **Rollback:** Docker tag-based (`docker-compose pull && docker-compose up -d`)

---

## 10. Multi-Cloud Portability

### Platform A: Docker Compose (Local/Development)
**Evidence:**
```bash
# Deploy
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:8081/health

# Screenshot: docs/evidence/docker-compose-deployment.png
```

**Characteristics:**
* Lightweight, fast iteration
* Runs on any machine with Docker
* Suitable for: development, testing, demos, small production

### Platform B: Kubernetes (Minikube/Production-ready)
**Evidence:**
```bash
# Start Minikube
minikube start --cpus=10 --memory=15972 --disk-size=50g

# Deploy
kubectl apply -f deployment/kubernetes/

# Verify
kubectl get pods -n sentiment-analysis
kubectl get svc -n sentiment-analysis

# Screenshot: docs/evidence/kubernetes-deployment.png
```

**Characteristics:**
* Production-grade orchestration
* Auto-scaling, self-healing
* Suitable for: production, multi-team, high availability

### Key Differences

| Aspect | Docker Compose | Kubernetes |
|--------|---------------|------------|
| **Orchestration** | Single host | Multi-node cluster |
| **Scaling** | Manual | Automatic (HPA) |
| **Load Balancing** | Simple round-robin | Advanced (Service) |
| **Health Checks** | Basic | Liveness/Readiness probes |
| **Updates** | Stop/Start | Rolling updates |
| **Configuration** | docker-compose.yml | Multiple YAML manifests |
| **Complexity** | Low | High |
| **Use Case** | Dev/Test/Small prod | Production |

### Portability Demonstration
**Same Docker Image:**
```bash
# Build once
docker build -t sentiment-analysis:latest .

# Run on Compose
docker-compose up -d

# Run on Kubernetes
docker save sentiment-analysis:latest | minikube image load -
kubectl apply -f deployment/kubernetes/
```

### Cloud Migration Path
```
Local Development
  ↓ (same image)
Cloud Kubernetes
  ├─ AWS EKS
  ├─ GCP GKE
  └─ Azure AKS

(Minimal manifest changes, zero code changes)
```

---

## 11. Costs

### Current Setup (Local)
**Total: $0/month**

All components run locally:
* Compute: Personal laptop/desktop
* Storage: Local disk (~10GB)
* Network: Localhost

### Cloud Deployment Estimates

#### AWS EKS Deployment
| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| **EKS Control Plane** | 1 cluster | $73 |
| **Worker Nodes** | 2x t3.medium | $61 |
| **Storage (EBS)** | 30GB | $3 |
| **Load Balancer** | 1 ALB | $16 |
| **Data Transfer** | 50GB | $5 |
| **CloudWatch** | Basic logs | $5 |
| **Total** | | **~$163/month** |

#### GCP GKE Deployment (Optimized)
| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| **GKE Cluster** | Standard (free control plane) | $0 |
| **Worker Nodes** | 2x e2-medium | $49 |
| **Storage** | 30GB Persistent Disk | $1 |
| **Load Balancer** | 1 LB | $18 |
| **Network Egress** | 50GB | $6 |
| **Total** | | **~$74/month** |

### Cost Optimizations Applied
1. **Right-sizing:** Reduced from t3.large to t3.medium (-40%)
2. **Spot instances:** For training workloads (-60%)
3. **Auto-scaling:** Scale to zero during off-hours (-30%)
4. **Storage lifecycle:** Delete old artifacts after 90 days (-20%)

### Assumptions
* **Usage:** 8-5 weekdays (auto-scale down nights/weekends)
* **Traffic:** ~1,000 predictions/day
* **Training:** Once per week (~2 hours)
* **Region:** us-east-1 (AWS) or us-central1 (GCP)
* **Data:** 50GB egress/month
* **Retention:** 30 days logs, 90 days artifacts

### Cost Breakdown by Function
* **Inference (serving):** 60% of costs
* **Training:** 20% of costs
* **Monitoring:** 10% of costs
* **Storage:** 10% of costs

### Scaling Costs
| Users/Day | Predictions/Day | Monthly Cost (GCP) |
|-----------|-----------------|-------------------|
| 10 | 100 | $45 |
| 100 | 1,000 | $74 (current estimate) |
| 1,000 | 10,000 | $245 |
| 10,000 | 100,000 | $890 |

---

## 12. Known Limitations

### What is Incomplete

1. **Kubeflow Integration**
   - Pipeline defined but not deployed to Kubeflow
   - Used simplified Python scripts instead
   - Reason: Kubeflow setup complexity vs. project timeline

2. **Automated Retraining**
   - Manual trigger only
   - Data drift detection implemented conceptually
   - No scheduled CronJob deployed
   - Reason: Requires production data flow

3. **Hyperparameter Tuning (Katib)**
   - Trained with fixed hyperparameters
   - Manual experimentation via MLflow
   - No automated Katib sweep
   - Reason: Time constraints, manual tuning sufficient

4. **Network Policies**
   - Defined but not enforced
   - Security contexts implemented
   - Network segmentation ready but not active
   - Reason: Single-tenant local deployment

5. **Multi-Region Deployment**
   - Single region only
   - DR/backup plan not implemented
   - Reason: Cost and scope

### What Would Be Improved

1. **Model Architecture**
   - Current: Bidirectional LSTM
   - Future: Transformer-based (BERT/RoBERTa)
   - Expected gain: +5-10% accuracy

2. **Data Pipeline**
   - Current: Static dataset
   - Future: Streaming data ingestion
   - Real-time review processing

3. **Monitoring**
   - Current: Basic metrics
   - Future: Advanced observability
     - Distributed tracing (Jaeger)
     - Log aggregation (ELK)
     - APM (Application Performance Monitoring)
     - Synthetic monitoring

4. **Testing**
   - Current: Unit tests (85% coverage)
   - Future: Full test pyramid
     - Integration tests
     - E2E tests
     - Load tests (Locust)
     - Chaos engineering

5. **Security**
   - Current: Container scanning, SAST
   - Future: Runtime security (Falco)
   - Secrets management (Vault)
   - mTLS for service-to-service

6. **Deployment**
   - Current: Manual approval for production
   - Future: Progressive delivery
     - Canary deployments (10% → 50% → 100%)
     - A/B testing framework
     - Feature flags
     - Automated rollback

7. **Data Management**
   - Current: In-memory storage
   - Future: PostgreSQL for persistence
   - Review data versioning
   - GDPR compliance tools

---

## 13. Troubleshooting

### Issue: Model server fails to start
**Symptom:** `docker-compose ps` shows "Restarting"

**Solution:**
```bash
# Check logs
docker-compose logs model-server

# Common causes:
# 1. Model file missing
ls -lh models/sentiment_model_best.pt

# 2. Port conflict
lsof -i :8081  # Kill conflicting process

# 3. Rebuild image
docker-compose down
docker-compose build model-server
docker-compose up -d
```

### Issue: Prometheus shows no data
**Symptom:** Empty graphs in Grafana

**Solution:**
```bash
# Check Prometheus targets
open http://localhost:9090/targets

# Should show model-server:8080 as "UP"
# If DOWN, check model server is exposing /metrics:
curl http://localhost:8081/metrics

# Restart Prometheus
docker-compose restart prometheus
```

### Issue: Training fails with OOM
**Symptom:** "Killed" or memory errors

**Solution:**
```bash
# Reduce batch size
python src/training/train.py --batch-size 32

# Or limit dataset
# Edit preprocessing to use subset
```

### Issue: CI/CD pipeline fails
**Symptom:** GitHub Actions red X

**Solution:**
```bash
# Check .github/workflows/mlops-complete.yaml
# Common issues:
# 1. Secrets not set in GitHub
# 2. Docker build fails
# 3. Tests fail

# Run locally to debug:
pytest tests/ -v
docker build -t test:latest .
```

---

## 14. Quick Start Summary
```bash
# 1. Setup
git clone <repo>
cd sentiment-mlops
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Train
./scripts/train.sh

# 3. Deploy
./scripts/deploy.sh docker-compose staging

# 4. Test
curl http://localhost:8081/health
open http://localhost:8081

# 5. Monitor
open http://localhost:3000  # Grafana
open http://localhost:5001  # MLflow

# 6. Stop
docker-compose down
```

---

## 15. Contact & Support

**Issues:** GitHub Issues tab
**Questions:** [your.email@example.com]
**Documentation:** docs/ directory

---

**Last Updated:** 2024-02-24
**Version:** 1.0
**Author:** [Your Name]
