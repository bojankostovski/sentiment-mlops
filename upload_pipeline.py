import kfp

# Connect to Kubeflow Pipelines
client = kfp.Client(host='http://localhost:8080')

# Upload pipeline
pipeline = client.pipeline_uploads.upload_pipeline(
    uploadfile='sentiment_pipeline_v1.yaml',
    name='Sentiment Analysis MLOps Pipeline',
    description='End-to-end pipeline: Preprocessing → Katib → Training → Deployment'
)

print(f"✅ Pipeline uploaded successfully!")
print(f"Pipeline ID: {pipeline.id}")
print(f"Pipeline Name: {pipeline.name}")
print(f"\n🌐 View in UI: http://localhost:8080/#/pipelines")
