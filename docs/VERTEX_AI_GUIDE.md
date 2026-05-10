# Vertex AI Setup Guide

## Overview

This project supports **Google Cloud Vertex AI** as an alternative to direct Anthropic API access. Vertex AI provides Claude models through Google Cloud Platform with enterprise features.

**Benefits:**
- ✅ No Anthropic API key needed
- ✅ GCP-integrated billing
- ✅ Enterprise security and compliance
- ✅ Same Claude models (Opus, Sonnet, Haiku)
- ✅ Prompt caching support

---

## Quick Start (3 Commands)

```bash
# 1. Set your GCP project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# 2. Authenticate
gcloud auth application-default login

# 3. Install dependencies (if not already done)
pip install 'anthropic[vertex]' requests python-dateutil gitpython
```

---

## Prerequisites

1. **Google Cloud Project** with Vertex AI enabled
2. **Python 3.10+**
3. **gcloud CLI** installed

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

### 3. Configure Environment

Add to your `.bashrc` or `.zshrc`:
```bash
# GCP Configuration
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-east5"  # or your preferred region

# Optional: Service account key (if using Option B)
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/kernel-tracker-key.json"
```

Reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

## Available Regions

Claude is available in these Vertex AI regions:
- `us-east5` (Columbus, Ohio) - **Recommended**
- `europe-west1` (Belgium)
- `asia-northeast1` (Tokyo)

Check current availability:
```bash
gcloud ai models list --region=us-east5 | grep claude
```

---

## Available Models

| Model | Model ID | Best For |
|-------|----------|----------|
| **Claude Sonnet 4.6** | `claude-sonnet-4-6@20250514` | Analysis and writing (recommended) |
| **Claude Opus 4.7** | `claude-opus-4-7@20250514` | Complex analysis requiring maximum accuracy |
| **Claude Haiku 4.5** | `claude-haiku-4-5@20251001` | Simple data collection or filtering |

---

## Running the Agents

### Analysis Agent (Vertex AI version)

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

### Writer Agent (Vertex AI version)

```bash
# Generate blog post
python3 agents/writer_vertexai.py \
    --subsystems xfs ext4 btrfs \
    --date 2026-05-07 \
    --date-range "May 1-7, 2026"
```

---

## Code Differences

### Anthropic API vs Vertex AI

**Original (Direct Anthropic API):**
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Vertex AI:**
```python
from anthropic import AnthropicVertex

client = AnthropicVertex(
    region="us-east5",
    project_id=os.environ["GOOGLE_CLOUD_PROJECT"]
)

response = client.messages.create(
    model="claude-sonnet-4-6@20250514",  # Note: versioned model ID
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### File Structure

```
agents/
├── analyzer.py              # Original (Anthropic API)
├── analyzer_vertexai.py     # ← Use this for Vertex AI
├── writer.py                # Original (Anthropic API)
└── writer_vertexai.py       # ← Use this for Vertex AI
```

---

## Testing Your Setup

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
    --member="user:$(gcloud config get-value account)" \
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

## Anthropic API vs Vertex AI Comparison

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

## Enterprise Benefits

1. **Centralized Billing**: All AI costs in GCP billing
2. **Security**: Service accounts, VPC, audit logs
3. **Compliance**: HIPAA, SOC 2, ISO 27001
4. **Integration**: Works with other GCP services
5. **Support**: Google Cloud enterprise support

---

## Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Claude on Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude)
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)
