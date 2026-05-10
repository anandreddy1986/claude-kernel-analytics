# Vertex AI Quick Start

**For users with existing Google Cloud / Vertex AI access**

## TL;DR - 3 Commands to Get Started

```bash
# 1. Set your GCP project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# 2. Authenticate (if not already done)
gcloud auth application-default login

# 3. Install dependencies
pip install 'anthropic[vertex]' requests python-dateutil gitpython
```

---

## Run the Demo (with Vertex AI)

```bash
# Create sample data
python3 -c "from demo_mock import create_sample_data; create_sample_data()"

# Run analysis with Vertex AI
python3 agents/analyzer_vertexai.py --subsystem xfs

# Generate blog post
python3 agents/writer_vertexai.py --subsystems xfs
```

---

## Key Differences for Vertex AI

### Code Changes Needed

**Original (Direct Anthropic API):**
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
```

**Vertex AI:**
```python
from anthropic import AnthropicVertex

client = AnthropicVertex(
    region="us-east5",
    project_id=os.environ["GOOGLE_CLOUD_PROJECT"]
)
```

### Environment Variables

| Anthropic API | Vertex AI |
|---------------|-----------|
| `ANTHROPIC_API_KEY` | `GOOGLE_CLOUD_PROJECT` |
| - | `GOOGLE_APPLICATION_CREDENTIALS` (optional) |

### Model Names

| Anthropic API | Vertex AI |
|---------------|-----------|
| `claude-sonnet-4-6` | `claude-sonnet-4-6@20250514` |
| `claude-opus-4-7` | `claude-opus-4-7@20250514` |
| `claude-haiku-4-5` | `claude-haiku-4-5@20251001` |

---

## File Structure

```
agents/
├── analyzer.py              # Original (Anthropic API)
├── analyzer_vertexai.py     # ← Use this for Vertex AI
├── writer.py                # Original (Anthropic API)
└── writer_vertexai.py       # ← Use this for Vertex AI
```

---

## Quick Test

```python
#!/usr/bin/env python3
from anthropic import AnthropicVertex
import os

client = AnthropicVertex(
    region="us-east5",
    project_id=os.environ["GOOGLE_CLOUD_PROJECT"]
)

response = client.messages.create(
    model="claude-sonnet-4-6@20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.content[0].text)
```

---

## Common Issues

### "Could not determine credentials"
```bash
gcloud auth application-default login
```

### "Project not set"
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### "Permission denied"
```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="user:$(gcloud config get-value account)" \
    --role="roles/aiplatform.user"
```

---

## Full Documentation

See [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md) for complete setup instructions.
