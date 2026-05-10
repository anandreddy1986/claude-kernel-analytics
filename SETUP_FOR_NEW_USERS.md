# Setup Guide for New Users

This guide will help you set up the Autonomous Agentic Kernel Publication System on your local machine.

## ⚠️ Important Security Notes

**Before you start:**
- **NEVER commit API keys or credentials** - The `.gitignore` is already configured to protect sensitive files
- **Your email password is NOT in this repo** - You'll need to configure it yourself
- **API keys are required** - You need either an Anthropic API key or Google Cloud (Vertex AI) credentials

## 📋 Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **10GB+ disk space** (for kernel git repositories)

4. **Claude API Access** - Choose one:
   - **Option A:** Anthropic API key from https://console.anthropic.com/
   - **Option B:** Google Cloud project with Vertex AI enabled

## 🚀 Quick Setup (5 minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/anandreddy1986/claude-kernel-analytics.git
cd claude-kernel-analytics
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 3: Configure API Access

**Option A: Using Anthropic Claude API (Recommended)**

```bash
# Set your API key (temporary - for this session only)
export ANTHROPIC_API_KEY='your-api-key-here'

# OR add to your shell profile for persistence:
echo 'export ANTHROPIC_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

**Option B: Using Google Vertex AI**

```bash
# Set up Google Cloud authentication
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Step 4: Initialize Project Structure

```bash
# Run setup script (creates directories)
./scripts/setup.sh

# Verify structure
ls -la data/ database/
```

### Step 5: Test Your Setup

```bash
# Quick test with XFS subsystem (7 days of data)
python3 agents/collector.py --subsystem xfs --days 7

# If successful, you'll see:
# ✓ Fetching mailing list updates
# ✓ Processing git repository
# ✓ Saved commits to data/raw/...
```

## 📧 Email Configuration (Optional)

If you want to use email features (monthly reports, presentations):

### Step 1: Copy Template

```bash
cp config/email_config.json.template config/email_config.json
```

### Step 2: Edit Configuration

Edit `config/email_config.json`:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@example.com",
  "recipient_email": "recipient@example.com"
}
```

### Step 3: Set Password (Environment Variable)

**NEVER put your password in config files!**

```bash
# For Gmail: Create an App Password at https://myaccount.google.com/apppasswords
export SMTP_PASSWORD='your-app-password'

# Or create .env_email file (this is git-ignored):
echo "SMTP_PASSWORD=your-app-password" > .env_email
```

## 🎯 First Test Run

Let's do a complete workflow test with one subsystem:

```bash
# 1. Collect data (2-5 minutes)
python3 agents/collector.py --subsystem xfs --days 7

# 2. Analyze with Claude (5-10 minutes)
python3 agents/analyzer.py --subsystem xfs

# 3. Check results
cat data/processed/$(date +%Y-%m-%d)/xfs/analysis.json
```

**Expected cost:** $0.80-1.20 for first run (creates cache), $0.15-0.30 for subsequent runs

## 📁 What Gets Created

After your first run:

```
claude-kernel-analytics/
├── venv/                          # Your virtual environment (git-ignored)
├── data/
│   ├── raw/YYYY-MM-DD/           # Raw collected data (git-ignored)
│   ├── processed/YYYY-MM-DD/     # Claude analysis results (git-ignored)
│   ├── drafts/                   # Generated blog posts (git-ignored)
│   └── repos/                    # Cloned kernel repos (git-ignored)
├── database/
│   └── kernel_tracker.db         # SQLite database (git-ignored)
└── .env_email                     # Your SMTP password (git-ignored)
```

**Note:** All sensitive and large files are automatically excluded by `.gitignore`

## 🔒 Files You Should NEVER Commit

The following are already in `.gitignore`, but be aware:

- `.env` or `.env_email` (passwords, secrets)
- `data/raw/`, `data/processed/` (can be large)
- `data/repos/` (kernel git repos are huge)
- `database/*.db` (can contain processed data)
- `config/email_config.json` (may contain your email)

## 📚 Documentation Reference

- **[README.md](README.md)** - Project overview and architecture
- **[QUICKSTART.md](QUICKSTART.md)** - Detailed usage examples
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Development roadmap
- **[SHARING_GUIDE.md](SHARING_GUIDE.md)** - Publishing and sharing results

## 🐛 Common Issues

### "No module named 'anthropic'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not set"
```bash
# Check if it's set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY='your-key'
```

### "git clone failed"
```bash
# Network issues? Clone manually
mkdir -p data/repos
git clone git://git.kernel.org/pub/scm/fs/xfs/xfs-linux.git data/repos/xfs
```

### "Rate limit exceeded"
- Wait a few minutes
- Use Claude Sonnet 4.6 instead: `--model claude-sonnet-4-6`
- Upgrade your API tier at console.anthropic.com

## 💡 Best Practices

1. **Start small** - Test with one subsystem first (XFS)
2. **Monitor costs** - Check your Anthropic dashboard regularly
3. **Use caching** - Run weekly for best cost efficiency (80% savings)
4. **Keep .env files private** - Never share or commit them
5. **Update regularly** - `git pull` to get latest improvements

## 🤝 Contributing

Found a bug or have a suggestion? Please open an issue on GitHub!

## 📞 Getting Help

1. Check [QUICKSTART.md](QUICKSTART.md) for detailed examples
2. Review error messages carefully - they usually indicate what's missing
3. Verify your API keys are set correctly
4. Check your API quota/limits at console.anthropic.com

## ✅ Verification Checklist

Before running the full system, verify:

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list`)
- [ ] API key set (`echo $ANTHROPIC_API_KEY`)
- [ ] Tested with one subsystem (`collector.py` + `analyzer.py`)
- [ ] Results appear in `data/processed/`

Once these are done, you're ready to run the full system!

---

**Need more help?** See [QUICKSTART.md](QUICKSTART.md) or open an issue on GitHub.
