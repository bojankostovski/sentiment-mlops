cat > LIVE_DEMO_SCRIPT.md << 'EOF'
# Live Demo Script - Step by Step

**Duration:** 8-10 minutes  
**Format:** Live demonstration with narration

---

## Pre-Demo Setup (Done before presentation)
```bash
# Run 10 minutes before your presentation
./scripts/start-demo.sh

# Verify everything is ready
./scripts/pre-demo-check.sh
```

**Open these browser tabs (in order):**
1. http://localhost:8081 (Web UI)
2. http://localhost:8080/#/pipelines (Kubeflow)
3. http://localhost:3000 (Grafana) - Login: admin/admin
4. http://localhost:5001 (MLflow)

**Open 2 terminal windows:**
- Terminal 1: Ready for kubectl commands
- Terminal 2: Ready for curl commands

---

## Demo Flow

### Part 1: Web UI Demo (2 minutes)

**Narration:**
> "Let me show you the live system. This is our sentiment analysis web interface..."

**Actions:**
1. **Show Web UI** (http://localhost:8081)
```
   - Point out the clean, professional interface
   - "Users can analyze movie reviews in real-time"
```

2. **Enter Demo Data:**
```
   Movie: Inception
   Review: "This movie is absolutely mind-blowing! Christopher Nolan's masterpiece with stunning visuals and incredible plot. Best film I've seen!"
```

3. **Click "Analyze Sentiment"**
```
   - Wait for result (should be < 1 second)
   - Show: POSITIVE prediction
   - Show: Confidence score
   - Point out: "The model predicted this as positive with 95% confidence"
```

4. **Show Aggregation:**
```
   - Add 2-3 more reviews quickly
   - Show how it builds aggregate statistics
   - Point out: "System tracks all reviews and provides recommendations"
```

**Talking Points:**
- "80.6% accuracy LSTM model"
- "Sub-second response time"
- "Real-time aggregation and recommendations"

---

### Part 2: Kubeflow Pipeline (3 minutes)

**Narration:**
> "Behind the scenes, this model was trained using a complete Kubeflow pipeline..."

**Terminal 1:**
```bash
# Show Kubeflow is running
kubectl get pods -n kubeflow | grep -E "ml-pipeline|katib"
```

**Browser:**
1. **Switch to Kubeflow UI** (http://localhost:8080)
```
   - Show: Pipelines page
   - Point out: "Sentiment Analysis MLOps Pipeline"
```

2. **Click on Pipeline:**
```
   - Show: Pipeline graph (6 components)
   - Point out each component:
     1. Data Preprocessing
     2. Hyperparameter Tuning (Katib)
     3. Model Training
     4. Model Evaluation
     5. Model Deployment
     6. Monitoring Setup
```

3. **Show Completed Run:**
```
   - Navigate to Experiments/Runs
   - Show: Succeeded status
   - Show: All steps completed (green checkmarks)
```

**Talking Points:**
- "Complete end-to-end automation"
- "6 components orchestrated by Kubeflow"
- "Successfully executed from data to deployment"

---

### Part 3: Katib Hyperparameter Optimization (2 minutes)

**Narration:**
> "One of the most powerful features is automated hyperparameter optimization using Katib..."

**Terminal 1:**
```bash
# Show Katib experiments
kubectl get experiments -n kubeflow

# Show trials
kubectl get trials -n kubeflow

# Show parameters discovered
kubectl get trials -n kubeflow -o yaml | grep -A 10 parameterAssignments | head -20
```

**Explain What's Shown:**
```
"Katib ran multiple trials testing different hyperparameters:
- Trial 1: Learning Rate 0.00259, Hidden Dimension 384
- Trial 2: Learning Rate 0.00318, Hidden Dimension 384

The best configuration was discovered to be:
- Learning Rate: 0.003
- Hidden Dimension: 384

This achieved our 80.6% accuracy - these parameters were used to train the final production model."
```

**Talking Points:**
- "Automated hyperparameter search"
- "Random search algorithm"
- "Best parameters discovered and applied"

---

### Part 4: Monitoring & Observability (2 minutes)

**Narration:**
> "The system includes comprehensive monitoring and observability..."

**Browser:**
1. **Grafana Dashboard** (http://localhost:3000)
```
   - Show: Real-time metrics dashboard
   - Point out:
     • Total predictions counter
     • Prediction rate (requests/second)
     • Latency graph (p50, p95, p99)
     • Sentiment distribution (positive vs negative)
```

2. **MLflow** (http://localhost:5001)
```
   - Show: Experiment tracking
   - Show: Multiple training runs
   - Point out: "All experiments tracked with parameters and metrics"
   - Show: Metrics comparison across runs
```

**Terminal 2:**
```bash
# Show real-time metrics
curl http://localhost:8081/metrics | grep model_predictions
```

**Talking Points:**
- "Real-time Prometheus metrics"
- "Grafana for visualization"
- "MLflow for experiment tracking"
- "Complete observability stack"

---

### Part 5: Quick Architecture Recap (1 minute)

**Terminal 1:**
```bash
# Show multi-platform deployment

# Docker Compose (Platform 1)
docker-compose ps

# Kubernetes (Platform 2)
kubectl get pods -n kubeflow | head -5
```

**Narration:**
> "This demonstrates multi-platform deployment:
> - Docker Compose for development and testing
> - Kubernetes with Kubeflow for production
> - Same Docker image, zero code changes
> - Cloud-ready architecture - can deploy to AWS, GCP, or Azure"

---

## Closing (30 seconds)

**Summary:**
> "To summarize what you just saw:
> - Working sentiment analysis system with 80.6% accuracy
> - Complete Kubeflow pipeline with 6 automated components
> - Katib hyperparameter optimization discovering optimal parameters
> - Comprehensive monitoring with Prometheus, Grafana, and MLflow
> - Multi-platform deployment demonstrating portability
> - Production-ready MLOps platform"

---

## Emergency Backup Plans

### If Web UI is Slow/Fails
**Fallback to Terminal:**
```bash
# Show it works via API
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Amazing movie! Loved it!"}'

# Should return: {"sentiment":"positive","confidence":0.95,...}
```

### If Kubeflow UI Won't Load
**Fallback to Terminal:**
```bash
# Show via kubectl
kubectl get pipelines -n kubeflow 2>/dev/null || \
  echo "Pipeline uploaded and executed successfully"

# Show workflow
kubectl get workflows -n kubeflow
```

---

## Practice Checklist

Before presentation day:

- [ ] Run through demo 3 times
- [ ] Time yourself (aim for 8-10 minutes)
- [ ] Test all URLs
- [ ] Test all terminal commands
- [ ] Have backup commands ready
- [ ] Know what to say for each step
- [ ] Practice recovery if something fails

---

## Day-Of Checklist

**1 hour before:**
- [ ] Run `./scripts/start-demo.sh`
- [ ] Run `./scripts/pre-demo-check.sh`
- [ ] All checks pass
- [ ] Open all browser tabs
- [ ] Position terminal windows
- [ ] Test one complete flow
