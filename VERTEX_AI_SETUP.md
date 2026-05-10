# Vertex AI Setup Guide

## Overview

This project supports **Google Cloud Vertex AI** as an alternative to direct Anthropic API access. Vertex AI provides Claude models through Google Cloud Platform with:

- ✅ **No Anthropic API key needed**
- ✅ **GCP-integrated billing**
- ✅ **Enterprise security and compliance**
- ✅ **Same Claude models** (Opus, Sonnet, Haiku)
- ✅ **Prompt caching support**

---

## Prerequisites

1. **Google Cloud Project** with Vertex AI enabled
2. **Authentication** via Application Default Credentials (ADC)
3. **Python 3.10+**
4. **anthropic[vertex]** Python package

---

## Setup Steps

### 1. Enable Vertex AI API

```bash
# Set your GCP project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verify it's enabled
gcloud services list --enabled | grep aiplatform
```

### 2. Set Up Authentication

**Option A: Local Development (gcloud CLI)**
```bash
# Authenticate with your Google account
gcloud auth application-default login

# Set project
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Verify authentication
gcloud auth application-default print-access-token
```

**Option B: Service Account (Production)**
```bash
# Create service account
gcloud iam service-accounts create kernel-tracker \
    --display-name="Kernel Update Tracker Bot"

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:kernel-tracker@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/kernel-tracker-key.json \
    --iam-account=kernel-tracker@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/kernel-tracker-key.json"
```

### 3. Install Dependencies

```bash
# Install Anthropic SDK with Vertex AI support
pip install 'anthropic[vertex]' requests python-dateutil gitpython

# Or from requirements file
pip install -r requirements.txt
```

Update `requirements.txt` to include Vertex AI:
```txt
anthropic[vertex]>=0.34.0
google-cloud-aiplatform>=1.38.0
requests>=2.31.0
python-dateutil>=2.9.0
gitpython>=3.1.43
```

### 4. Configure Environment

Add to your `.bashrc` or `.zshrc`:
```bash
# GCP Configuration
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-east5"  # or your preferred region

# Optional: Service account key
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/kernel-tracker-key.json"
```

Reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

## Available Regions for Claude on Vertex AI

Claude is available in these regions:
- `us-east5` (Columbus, Ohio) - **Recommended**
- `europe-west1` (Belgium)
- `asia-northeast1` (Tokyo)

Check current availability:
```bash
gcloud ai models list --region=us-east5 | grep claude
```

---

## Available Models

### Claude Sonnet 4.6 (Recommended for this project)
```
Model ID: claude-sonnet-4-6@20250514
Use case: Analysis and writing (good balance of cost/performance)
```

### Claude Opus 4.7 (Higher accuracy)
```
Model ID: claude-opus-4-7@20250514
Use case: Complex analysis requiring maximum accuracy
```

### Claude Haiku 4.5 (Fastest/cheapest)
```
Model ID: claude-haiku-4-5@20251001
Use case: Simple data collection or filtering
```

---

## Running the Agents with Vertex AI

### Analysis Agent

```bash
# Using environment variables
python3 agents/analyzer_vertexai.py \
    --subsystem xfs \
    --date 2026-05-07

# Or specify project/region explicitly
python3 agents/analyzer_vertexai.py \
    --subsystem xfs \
    --project-id your-project-id \
    --region us-east5 \
    --model claude-sonnet-4-6@20250514
```

### Writer Agent

```bash
# Generate blog post
python3 agents/writer_vertexai.py \
    --subsystems xfs ext4 btrfs \
    --date 2026-05-07 \
    --date-range "May 1-7, 2026"

# With explicit configuration
python3 agents/writer_vertexai.py \
    --subsystems xfs \
    --project-id your-project-id \
    --region us-east5 \
    --model claude-sonnet-4-6@20250514
```

---

## Testing Your Setup

### Quick Test Script

Save as `test_vertexai.py`:
```python
#!/usr/bin/env python3
from anthropic import AnthropicVertex
import os

# Configuration
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
region = "us-east5"

print(f"Testing Vertex AI connection...")
print(f"Project: {project_id}")
print(f"Region: {region}")

# Create client
client = AnthropicVertex(region=region, project_id=project_id)

# Simple test
response = client.messages.create(
    model="claude-sonnet-4-6@20250514",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Say 'Hello from Vertex AI!'"}
    ]
)

print(f"\n✅ Success! Response:")
print(response.content[0].text)
```

Run it:
```bash
python3 test_vertexai.py
```

Expected output:
```
Testing Vertex AI connection...
Project: your-project-id
Region: us-east5

✅ Success! Response:
Hello from Vertex AI!
```

---

## Pricing

Vertex AI pricing for Claude (as of May 2026):

### Claude Sonnet 4.6
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens
- Cache write: $3.75 per million tokens
- Cache read: $0.30 per million tokens

### Estimated Costs for This Project
- **Per subsystem (weekly)**: $0.03 - $0.05
- **15 subsystems**: $0.45 - $0.75 per week
- **Monthly**: $2 - $3
- **Yearly**: $24 - $36

**Note**: Vertex AI pricing may include additional GCP charges (minimal for API calls).

---

## Troubleshooting

### Error: "Could not automatically determine credentials"
```bash
# Solution: Authenticate with gcloud
gcloud auth application-default login
```

### Error: "Permission denied"
```bash
# Solution: Grant Vertex AI User role
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="user:your-email@example.com" \
    --role="roles/aiplatform.user"
```

### Error: "API not enabled"
```bash
# Solution: Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### Error: "Model not found in region"
```bash
# Solution: Use a supported region
# Change to us-east5, europe-west1, or asia-northeast1
export GOOGLE_CLOUD_REGION="us-east5"
```

### Check Current Configuration
```bash
# View project
gcloud config get-value project

# View active account
gcloud auth list

# Test API access
gcloud ai models list --region=us-east5
```

---

## Differences from Direct Anthropic API

| Feature | Anthropic API | Vertex AI |
|---------|---------------|-----------|
| **Authentication** | ANTHROPIC_API_KEY | Google ADC |
| **SDK Import** | `from anthropic import Anthropic` | `from anthropic import AnthropicVertex` |
| **Client Init** | `Anthropic(api_key=key)` | `AnthropicVertex(region, project_id)` |
| **Model IDs** | `claude-sonnet-4-6` | `claude-sonnet-4-6@20250514` |
| **Billing** | Anthropic account | GCP billing |
| **Features** | All features | All features (same) |
| **Prompt Caching** | ✅ Supported | ✅ Supported |
| **Region** | Global | Regional (us-east5, etc.) |

---

## Production Deployment

### Cron Job Setup

Create `/etc/cron.d/kernel-tracker`:
```cron
# Run every Sunday at 6 AM
0 6 * * 0 /opt/kernel-tracker/run.sh

# run.sh should:
# 1. Set GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS
# 2. Run collector.py
# 3. Run analyzer_vertexai.py
# 4. Run writer_vertexai.py
```

### GCP Compute Engine / Cloud Run

If running on GCP:
```bash
# Service account is automatically configured
# No need for GOOGLE_APPLICATION_CREDENTIALS

# Just set project
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)

# Run agents
python3 agents/analyzer_vertexai.py --subsystem xfs
```

---

## Benefits of Vertex AI for Enterprise

1. **Centralized Billing**: All AI costs in GCP billing
2. **Security**: Service accounts, VPC, audit logs
3. **Compliance**: HIPAA, SOC 2, ISO 27001
4. **Integration**: Works with other GCP services
5. **Multi-Cloud**: Part of broader AI strategy
6. **Support**: Google Cloud enterprise support

---

## Next Steps

1. ✅ Set up GCP project and authentication
2. ✅ Test connection with `test_vertexai.py`
3. ✅ Run demo with sample data
4. ⬜ Configure for production with service account
5. ⬜ Set up monitoring and alerting
6. ⬜ Schedule weekly cron job

---

## Support

- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **Claude on Vertex AI**: https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude
- **Anthropic SDK**: https://github.com/anthropics/anthropic-sdk-python
- **Project Issues**: https://github.com/your-repo/issues

---

*Last updated: 2026-05-07*
