# Quick Start Guide

Get started with the Linux Kernel Update Tracker in 5 minutes.

## Prerequisites

- **Python 3.10+** - Check with `python3 --version`
- **Git** - Check with `git --version`
- **Claude API Key** - Get from https://console.anthropic.com/
- **10GB+ disk space** - For git repositories

## Installation

```bash
# 1. Navigate to project directory
cd Claude_Agentic_Kernel_Publication

# 2. Run setup script
./scripts/setup.sh

# 3. Activate virtual environment
source venv/bin/activate

# 4. Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Test Run: XFS Subsystem

Let's do a complete test run for the XFS filesystem subsystem.

### Step 1: Collect Data (2-5 minutes)

```bash
python3 agents/collector.py --subsystem xfs --days 7
```

This will:
- Fetch XFS mailing list threads from lore.kernel.org
- Clone/update XFS git repository
- Extract commits from the last 7 days
- Save raw data to `data/raw/YYYY-MM-DD/xfs/`

**Expected output:**
```
============================================================
Collecting data for XFS
============================================================
Fetching mailing list updates from https://lore.kernel.org/linux-xfs/new.atom
Processing git repository: git://git.kernel.org/pub/scm/fs/xfs/xfs-linux.git
Found 15 commits for xfs
Saved 15 commits to data/raw/2026-05-06/xfs/commits.json
```

### Step 2: Analyze Data (5-10 minutes)

```bash
python3 agents/analyzer.py --subsystem xfs
```

This will:
- Load collected commits
- Analyze each commit using Claude API
- Extract significance, type, and summary
- Save analysis to `data/processed/YYYY-MM-DD/xfs/`

**Expected output:**
```
============================================================
Analyzing 15 commits for XFS
============================================================

[1/15] Analyzing: xfs: fix extent leak in xfs_reflink_cancel_cow_blocks...
  Type: bugfix | Significance: major

[2/15] Analyzing: xfs: improve btree scrub performance...
  Type: optimization | Significance: minor

...

============================================================
Analysis Summary for XFS
============================================================
Total commits analyzed: 15
Token usage:
  Input tokens: 45,230
  Output tokens: 8,150
  Cache read: 156,800
  Cache write: 18,500
Estimated cost: $0.87
```

### Step 3: Review Results

```bash
# View analysis results
cat data/processed/$(date +%Y-%m-%d)/xfs/analysis.json | jq '.analyses[] | {subject: .commit_subject, type, significance, summary}'
```

**Sample output:**
```json
{
  "subject": "xfs: fix extent leak in xfs_reflink_cancel_cow_blocks",
  "type": "bugfix",
  "significance": "major",
  "summary": "Fixes a critical memory leak where copy-on-write extent blocks were not properly released during reflink cancellation, potentially causing ENOSPC errors on filesystems with heavy reflink usage."
}
```

## Collect All Subsystems

Once you've verified it works for one subsystem, run for all:

```bash
# Collect data for all 16 subsystems
python3 agents/collector.py --all --days 7

# This will take 20-30 minutes depending on git clone speeds
```

## Understanding Costs

### Prompt Caching Benefits

The analyzer uses **prompt caching** to significantly reduce costs:

- **First run** (cache miss): $0.80-1.20 per subsystem
- **Subsequent runs** (cache hit): $0.15-0.30 per subsystem

### Weekly Cost Estimate

For 16 subsystems with ~10 commits each per week:

| Scenario | Cost per Run | Weekly Cost |
|----------|--------------|-------------|
| First run (no cache) | $12-18 | N/A |
| Weekly runs (cached) | $3-5 | $3-5 |
| Monthly (4 weeks) | - | $12-20 |

**Savings from caching: ~80-85%**

## What's Next?

### Phase 1 (Current)
- ✓ Data collection agent
- ✓ Analysis agent
- ⧗ Content generation agent (writer.py)
- ⧗ Publishing agent

### To Implement Next

1. **Writer Agent** - Generate blog posts
2. **Blog Template** - Standardized format
3. **Weekly Automation** - Cron job setup
4. **Publishing** - WordPress/Medium integration

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for complete roadmap.

## Troubleshooting

### "git clone failed"

**Problem:** Repository clone timeout or network error

**Solution:**
```bash
# Manually clone repositories first
mkdir -p data/repos
git clone git://git.kernel.org/pub/scm/fs/xfs/xfs-linux.git data/repos/xfs
```

### "ANTHROPIC_API_KEY not set"

**Problem:** API key environment variable missing

**Solution:**
```bash
export ANTHROPIC_API_KEY='your-api-key'

# Or add to ~/.bashrc or ~/.zshrc for persistence:
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### "No module named 'anthropic'"

**Problem:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Rate limit exceeded"

**Problem:** Too many API requests

**Solution:**
- Add delays between requests
- Use Claude Sonnet 4.6 instead of Opus 4.7 (lower rate limits)
- Upgrade your API tier at console.anthropic.com

## File Structure

After a successful run:

```
Claude_Agentic_Kernel_Publication/
├── data/
│   ├── raw/2026-05-06/
│   │   └── xfs/
│   │       ├── commits.json         # Raw git commits
│   │       └── mailing_list.json    # Mailing list threads
│   ├── processed/2026-05-06/
│   │   └── xfs/
│   │       └── analysis.json        # Claude analysis results
│   └── repos/
│       └── xfs/                     # Cloned git repository
├── agents/
│   ├── collector.py                 # Data collection
│   └── analyzer.py                  # Claude analysis
└── config/
    └── subsystems.json              # Subsystem definitions
```

## Advanced Usage

### Custom Date Range

```bash
# Collect last 14 days
python3 agents/collector.py --subsystem xfs --days 14

# Analyze specific date
python3 agents/analyzer.py --subsystem xfs --date 2026-04-29
```

### Use Different Claude Model

```bash
# Use Claude Sonnet 4.6 (faster, cheaper)
python3 agents/analyzer.py --subsystem xfs --model claude-sonnet-4-6

# Use Claude Haiku 4.5 (very cheap for testing)
python3 agents/analyzer.py --subsystem xfs --model claude-haiku-4-5
```

### Batch Processing

```bash
# Analyze multiple subsystems sequentially
for subsys in xfs ext4 btrfs nfs; do
    python3 agents/analyzer.py --subsystem $subsys
done
```

## Getting Help

- **Documentation:** See [README.md](README.md) and [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Claude API Docs:** https://docs.anthropic.com/
- **Kernel Mailing Lists:** https://lore.kernel.org/
- **Issues:** Create an issue with your error message and steps to reproduce

## Next Steps

1. **Run your first test** - Follow Step 1-3 above
2. **Review the analysis** - Check quality of Claude's summaries
3. **Tune prompts** - Edit `agents/analyzer.py` to improve output
4. **Build writer agent** - Next phase of the project

Happy tracking! 🐧
