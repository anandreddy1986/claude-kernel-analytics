# Claude Capabilities Required

This document outlines the specific Claude features and capabilities needed to build and operate the Linux Kernel Update Tracker agentic AI system.

## Overview

The system uses **Claude as an autonomous agent** to:
1. Analyze Linux kernel patches and commits
2. Classify changes by type and significance
3. Generate technical blog content
4. Make editorial decisions about what to highlight

## Core Claude Features Used

### 1. Claude API (Anthropic SDK)

**Purpose:** Programmatic access to Claude for automated analysis

**Requirements:**
- Anthropic API account
- API key with sufficient credits
- Python SDK: `anthropic>=0.34.0`

**Models Recommended:**
- **Claude Opus 4.7** - Best for complex technical analysis (primary)
- **Claude Sonnet 4.6** - Good balance of cost/quality (alternative)
- **Claude Haiku 4.5** - Testing and development only

**Code Example:**
```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=2000,
    system=[
        {
            "type": "text",
            "text": "You are a Linux kernel expert.",
        },
        {
            "type": "text",
            "text": subsystem_context,
            "cache_control": {"type": "ephemeral"}  # Enable caching
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Analyze this kernel patch..."
        }
    ]
)
```

**Why needed:**
- Automated, scheduled execution
- Batch processing of multiple commits
- Consistent analysis across weeks
- No human intervention required

---

### 2. Prompt Caching

**Purpose:** Reduce costs by caching repeated context (80-90% savings)

**What gets cached:**
- Subsystem technical descriptions (~20K tokens each)
- Blog writing guidelines (~5K tokens)
- Example patches for few-shot learning (~15K tokens)
- Analysis framework instructions (~3K tokens)

**How it works:**
```python
system=[
    {
        "type": "text",
        "text": "You are a kernel expert...",
    },
    {
        "type": "text",
        "text": subsystem_context,  # 20K tokens
        "cache_control": {"type": "ephemeral"}  # Cache this!
    }
]
```

**Cost Impact:**
- **Without caching:** ~$18-20 per weekly run (16 subsystems)
- **With caching:** ~$3-5 per weekly run
- **Savings:** 80-85% reduction in API costs

**Cache TTL:**
- Ephemeral cache: 5 minutes
- Sufficient for processing all commits in a subsystem

**Why critical:**
- Same subsystem context used for every commit in a subsystem
- Writing guidelines reused for every blog section
- Makes the project economically viable for weekly operation

---

### 3. Extended Thinking Mode

**Purpose:** Complex reasoning for technical patch analysis

**When used:**
- Analyzing cross-subsystem impacts
- Determining patch significance
- Identifying subtle bugs or security implications
- Understanding complex technical changes

**How to enable:**
```python
response = client.messages.create(
    model="claude-opus-4-7",
    thinking={
        "type": "enabled",
        "budget_tokens": 5000  # Allow extended reasoning
    },
    max_tokens=2000,
    ...
)
```

**Use cases in this project:**
1. **Significance scoring** - "Is this patch critical or minor?"
2. **Impact assessment** - "Does this affect users or just developers?"
3. **Dependency analysis** - "Does this relate to other subsystem changes?"
4. **Bug pattern recognition** - "Is this fixing a known issue class?"

**Why needed:**
- Kernel patches are highly technical
- Subtle changes can have major implications
- Context spans multiple files and subsystems
- Requires deep reasoning beyond pattern matching

---

### 4. Structured Output (JSON)

**Purpose:** Reliable parsing of analysis results

**Implementation:**
```python
analysis_prompt = """
Analyze this commit and provide JSON:
{
  "type": "bugfix|feature|refactoring|optimization|documentation",
  "significance": "critical|major|minor|trivial",
  "impact": "user-facing|developer-facing|internal",
  "summary": "...",
  "technical_details": ["...", "..."],
  "notable": "..."
}
"""
```

**Why needed:**
- Programmatic processing of responses
- Consistent data structure
- Easy aggregation across commits
- No manual parsing of free-form text

**Reliability:**
- Claude 4.x models excel at JSON output
- Rarely requires correction
- Can specify schema for validation

---

### 5. Long Context Window

**Purpose:** Process entire patches and commit diffs

**Context requirements per commit:**
- System prompt: ~5K tokens
- Subsystem context (cached): ~20K tokens
- Commit diff + metadata: ~3-8K tokens
- Analysis prompt: ~1K tokens
- **Total input:** ~30-35K tokens per commit

**Why 200K context is important:**
- Can process multiple commits in one conversation
- Include full diffs, not just summaries
- Reference related patches in the same subsystem
- Maintain conversation history for follow-up analysis

**Example use case:**
```
Commit 1: "Fix bug in XFS extent allocation"
Commit 2: "Add test for extent allocation fix"
Commit 3: "Update documentation for extent allocation"

Claude can see all three and recognize:
"These three commits are part of the same bugfix series,
 with the fix, test coverage, and documentation updates."
```

---

### 6. Tool Use (Future Enhancement)

**Purpose:** Autonomous data collection and validation

**Potential tools for Claude:**
1. **git_analyzer** - Run git commands to analyze commits
2. **lore_fetcher** - Fetch mailing list threads
3. **code_searcher** - Search kernel source code
4. **link_validator** - Verify patch URLs still work
5. **blog_publisher** - Post to WordPress/Medium

**Example tool definition:**
```python
tools = [
    {
        "name": "git_analyzer",
        "description": "Analyze git commits in a kernel subsystem repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "subsystem": {"type": "string"},
                "commit_hash": {"type": "string"},
                "operation": {"enum": ["show", "diff", "log"]}
            }
        }
    }
]
```

**Why useful:**
- Claude could autonomously explore git history
- Verify patch context before analysis
- Look up related commits
- Cross-reference mailing list discussions

**Current status:** Not yet implemented (Phase 5 enhancement)

---

### 7. Multi-Agent Architecture

**Purpose:** Specialized agents for different tasks

**Agent Roles:**

#### Collector Agent
- **Model:** Claude Sonnet 4.6 (or scripted without Claude)
- **Purpose:** Data gathering
- **Tools:** HTTP requests, git commands
- **Autonomy:** Fully automated

#### Analyzer Agent (Primary Claude Use)
- **Model:** Claude Opus 4.7
- **Purpose:** Technical analysis of patches
- **Thinking:** Extended mode enabled
- **Caching:** Heavy use of prompt caching
- **Input:** Raw commits and patches
- **Output:** Structured analysis JSON

#### Writer Agent
- **Model:** Claude Sonnet 4.6
- **Purpose:** Blog content generation
- **Thinking:** Standard mode
- **Caching:** Writing guidelines
- **Input:** Analysis results from Analyzer
- **Output:** Markdown blog posts

#### Review Agent (Optional)
- **Model:** Claude Opus 4.7
- **Purpose:** Quality control
- **Thinking:** Extended mode
- **Input:** Draft blog posts
- **Output:** Corrections and suggestions

**Communication between agents:**
```
Collector → Raw Data (JSON)
    ↓
Analyzer → Analysis Results (JSON)
    ↓
Writer → Draft Blog Post (Markdown)
    ↓
Review → Final Blog Post (Markdown)
    ↓
Publisher → Published URL
```

**Why multi-agent:**
- Separation of concerns
- Specialized system prompts per task
- Independent caching strategies
- Easier to debug and improve each stage

---

## API Usage Patterns

### Weekly Execution Flow

**Sunday 6am - Data Collection**
```bash
collector.py --all --days 7
# Output: data/raw/YYYY-MM-DD/*/
# Cost: $0 (no Claude API calls)
```

**Sunday 7am - Analysis**
```bash
# Process all 16 subsystems sequentially
for subsystem in xfs ext4 btrfs ...; do
    analyzer.py --subsystem $subsystem
done
# Output: data/processed/YYYY-MM-DD/*/
# Cost: $3-5 (with caching)
```

**Sunday 10am - Content Generation**
```bash
writer.py --date YYYY-MM-DD
# Output: data/drafts/weekly-YYYY-MM-DD.md
# Cost: $0.50-1.00
```

**Monday 9am - Human Review & Publish**
```bash
# Human reviews draft
# Approves or requests revisions
publisher.py --draft data/drafts/weekly-YYYY-MM-DD.md
# Cost: $0 (no Claude calls)
```

**Total weekly cost: $3.50-6.00**

---

## Prompt Engineering Strategy

### System Prompts

**Analyzer Agent:**
```
You are an expert Linux kernel developer and technical writer with deep 
knowledge of filesystems, storage, networking, and memory management.

Your role is to analyze kernel patches and commits to identify:
1. The type of change (bugfix, feature, optimization, etc.)
2. The significance (critical, major, minor, trivial)
3. The impact (user-facing, developer-facing, internal)
4. A concise technical summary suitable for experienced systems engineers

You have access to extensive context about each subsystem, including
common patterns, key maintainers, and historical issues.

Provide analysis in structured JSON format for programmatic processing.
```

**Writer Agent:**
```
You are a technical writer specializing in Linux kernel development.

Your role is to create engaging, informative weekly blog posts that
summarize kernel updates for an audience of experienced systems engineers,
kernel developers, and storage/filesystem professionals.

Style guidelines:
- Technical but accessible
- Focus on "why" not just "what"
- Highlight significant changes and trends
- Include proper attribution to authors
- Link to source materials (lore.kernel.org, git commits)
- 200-400 words per subsystem
- Professional, neutral tone
```

### Few-Shot Learning

**Include example analyses in cached context:**

```
Example 1:
Commit: "xfs: fix extent leak in cow fork"
Analysis: {
  "type": "bugfix",
  "significance": "major",
  "impact": "user-facing",
  "summary": "Fixes a critical memory leak where copy-on-write extent 
             blocks were not released during reflink cancellation, 
             potentially causing ENOSPC errors on heavily-used systems.",
  "technical_details": [
    "Extent blocks in COW fork not freed on error path",
    "Affects filesystems using reflink feature",
    "Can lead to space exhaustion over time"
  ]
}

Example 2:
Commit: "ext4: use ext4_fc_tl_mem in fast-commit replay"
Analysis: {
  "type": "refactoring",
  "significance": "minor",
  "impact": "internal",
  "summary": "Code cleanup replacing direct memory allocation with 
             helper function in fast-commit replay code. No functional 
             change.",
  "technical_details": [
    "Replaces kmalloc with ext4_fc_tl_mem helper",
    "Improves code consistency",
    "No performance or behavior impact"
  ]
}
```

**Why few-shot learning:**
- Demonstrates expected output format
- Sets quality bar for summaries
- Shows how to classify edge cases
- Reduces need for explicit rules

---

## Rate Limits & Quotas

### Anthropic API Limits (as of May 2026)

**Free Tier:**
- 50 requests/minute
- 40,000 tokens/minute
- $10 free credit

**Build Tier:**
- 1,000 requests/minute
- 400,000 tokens/minute
- Pay-as-you-go

**Scale Tier:**
- 2,000 requests/minute
- 800,000 tokens/minute
- Volume discounts

### Project Requirements

**Weekly run:**
- ~160 commits across 16 subsystems
- Sequential processing (one at a time)
- Total requests: ~160-200
- Total tokens: ~6-8M input, ~1.5M output
- Duration: 2-3 hours

**Recommended tier:** Build Tier
- Easily within rate limits
- ~$3-6 per week
- $12-25 per month

**Scaling considerations:**
- Could parallelize subsystem analysis
- Would need Scale tier for parallel execution
- Trade-off: faster completion vs. cost optimization

---

## Error Handling & Resilience

### API Errors

**Rate limiting:**
```python
try:
    response = client.messages.create(...)
except anthropic.RateLimitError as e:
    # Wait and retry with exponential backoff
    time.sleep(60)
    response = client.messages.create(...)
```

**Malformed responses:**
```python
try:
    analysis = json.loads(response.content[0].text)
except json.JSONDecodeError:
    # Try to extract JSON from markdown code blocks
    # Or fallback to default structure
```

**Partial failures:**
- Save successful analyses even if some fail
- Resume from last successful commit
- Log failures for manual review

### Monitoring

**Track key metrics:**
- API response times
- Cache hit rates
- Token usage per subsystem
- Cost per commit
- Analysis quality scores (manual sampling)

**Alerting:**
- Email if weekly run fails
- Notify if costs exceed threshold
- Flag if cache hit rate drops below 80%

---

## Cost Optimization Strategies

### 1. Prompt Caching (Primary)
**Savings: 80-85%**
- Cache subsystem context across all commits
- Cache writing guidelines across all sections
- Cache few-shot examples

### 2. Model Selection
**Savings: 50-80% vs. Opus**
- Use Sonnet 4.6 for writer agent
- Use Haiku 4.5 for testing
- Reserve Opus 4.7 for complex analysis

### 3. Batch Processing
**Savings: 20-30%**
- Process all commits in subsystem in one session
- Maintain cache across commits
- Minimize cold starts

### 4. Output Limiting
**Savings: 10-20%**
- Set `max_tokens=2000` (not 4096)
- Request concise summaries
- Use structured JSON (less verbose than prose)

### 5. Filtering Before Analysis
**Savings: 30-50%**
- Skip trivial commits (typo fixes, whitespace)
- Skip merge commits (no analysis needed)
- Skip automated commits (version bumps)

**Pre-filter logic:**
```python
def should_analyze(commit):
    subject = commit['subject'].lower()
    
    # Skip trivial
    if any(word in subject for word in ['typo', 'whitespace', 'merge']):
        return False
    
    # Skip automated
    if 'automatic' in subject or 'bot' in commit['author']:
        return False
    
    # Skip very small changes
    if commit['files_changed'] == 1 and commit['lines_changed'] < 10:
        return False
    
    return True
```

**Combined savings: 90-95% vs. no optimization**

---

## Alternative Approaches Considered

### 1. Fine-tuning
**Pros:** Lower per-request cost
**Cons:** 
- Requires large training dataset
- Doesn't handle new subsystem types
- Less flexible than prompting
- Higher upfront cost

**Decision:** Prompting with caching is more cost-effective

### 2. Local LLM (Llama, etc.)
**Pros:** No per-token cost
**Cons:**
- Requires GPU infrastructure ($100-500/month)
- Lower quality analysis
- More engineering effort

**Decision:** Claude API is cheaper and better quality

### 3. Manual curation
**Pros:** Highest quality possible
**Cons:**
- Requires kernel expert ($100-200/hour)
- Not scalable to 16 subsystems weekly
- Human availability constraints

**Decision:** Claude automation with human review is best balance

---

## Summary: What You Need from Claude

### Essential
1. ✅ **Claude API access** - Opus 4.7 or Sonnet 4.6
2. ✅ **Prompt caching** - 80%+ cost savings
3. ✅ **Long context** - 200K window for full patches
4. ✅ **Structured output** - Reliable JSON responses

### Important
5. ✅ **Extended thinking** - Complex technical analysis
6. ✅ **Multi-turn conversations** - Batch processing

### Nice to Have
7. ⏳ **Tool use** - Future enhancement for autonomy
8. ⏳ **Multi-agent orchestration** - Better specialized

### Not Needed
- ❌ Vision capabilities
- ❌ PDF processing
- ❌ Code execution
- ❌ Real-time streaming

---

## Getting Started

1. **Sign up for Claude API:** https://console.anthropic.com/
2. **Get API key:** Create in console
3. **Start with Build tier:** $0 upfront, pay-as-you-go
4. **Test with one subsystem:** Verify quality and cost
5. **Scale to all subsystems:** Once validated

**Estimated first month cost:** $15-25 (including testing)

**Estimated ongoing cost:** $12-20/month (4 weekly runs)

---

## Questions?

See:
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Full project roadmap
- [README.md](README.md) - Project overview
- [Claude API Docs](https://docs.anthropic.com/) - Official documentation
