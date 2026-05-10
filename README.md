# Linux Kernel Update Tracker

An autonomous agentic AI system powered by Claude that monitors Linux kernel development and generates weekly blog posts.

## 🔒 Security Notice

**For new users:** This project requires API keys. See **[SETUP_FOR_NEW_USERS.md](SETUP_FOR_NEW_USERS.md)** for complete setup instructions.

**Important:**
- Never commit API keys or credentials to version control
- The `.gitignore` is configured to protect sensitive files (`.env*`, credentials, etc.)
- Set `ANTHROPIC_API_KEY` as an environment variable, not in code

## What This Does

Automatically tracks 15+ Linux kernel subsystems (filesystems, networking, memory management, storage) across mailing lists and git repositories, analyzes changes using Claude's extended thinking capabilities, and generates comprehensive weekly blog posts summarizing the most important updates.

## Quick Start

### Prerequisites
- Python 3.10+
- Claude API key (Opus 4.7 or Sonnet 4.6 recommended)
- Git
- 10GB+ disk space

### Installation
```bash
# Clone the repository
cd Claude_Agentic_Kernel_Publication

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (will create requirements.txt)
pip install anthropic requests python-dateutil gitpython

# Set up environment
export ANTHROPIC_API_KEY="your-api-key-here"

# Initialize the project
./scripts/setup.sh
```

### First Run (Manual Test)
```bash
# Test data collection for XFS subsystem
python agents/collector.py --subsystem xfs --days 7

# Analyze collected data
python agents/analyzer.py --input data/raw/$(date +%Y-%m-%d)/

# Generate blog post
python agents/writer.py --input data/processed/$(date +%Y-%m-%d)/

# Review output
cat data/drafts/weekly-$(date +%Y-%m-%d).md
```

### Weekly Automation
```bash
# Add to crontab (runs every Sunday at 6 AM)
0 6 * * 0 /path/to/scripts/weekly_run.sh
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Weekly Trigger (Cron)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 1. Data Collection Agent                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ • Fetch mailing list threads (lore.kernel.org)       │   │
│  │ • Pull git repository updates (kernel.org)           │   │
│  │ • Store raw patches and discussions                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                2. Analysis & Filtering Agent                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ • Parse patches and commit messages                  │   │
│  │ • Classify by subsystem and significance             │   │
│  │ • Extract key technical details (Claude API)         │   │
│  │ • Cross-reference mailing list + git                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                3. Content Generation Agent                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ • Summarize changes per subsystem                    │   │
│  │ • Generate technical blog content (Claude API)       │   │
│  │ • Add citations and references                       │   │
│  │ • Format as markdown                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 4. Review & Publishing Agent                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ • Human review queue                                 │   │
│  │ • Publish to blog platform                           │   │
│  │ • Archive and track metrics                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Subsystems Tracked

### Filesystems
- **XFS** - High-performance filesystem
- **EXT4** - Linux default filesystem
- **Btrfs** - Copy-on-write filesystem
- **OverlayFS** - Union filesystem
- **FUSE/virtiofs** - Userspace filesystems

### Network Filesystems
- **NFS** - Network File System (client/server)
- **SMB/CIFS** - Windows file sharing
- **CephFS** - Distributed filesystem
- **NFS-Ganesha** - Userspace NFS server
- **Samba** - Userspace SMB server

### Storage & Block
- **Device Mapper/LVM** - Logical volume management
- **Block Layer** - I/O scheduling
- **MD/RAID** - Software RAID
- **NVMe** - Modern storage protocol

### Core Kernel
- **Networking** - TCP/IP stack
- **Memory Management** - MM subsystem
- **Process Scheduling** - Scheduler and signals
- **Security** - LSM, SELinux

## Claude Capabilities Used

### 1. Multi-Agent Orchestration
Each agent is a separate Claude conversation with specialized system prompts:
- **Collector:** Git and mailing list expertise
- **Analyzer:** Linux kernel technical knowledge
- **Writer:** Technical writing and summarization

### 2. Prompt Caching
Significant cost savings by caching:
- Subsystem technical descriptions (~20K tokens each)
- Blog writing guidelines (~5K tokens)
- Example patches for few-shot learning (~15K tokens)
- **Expected savings:** 80-90% on repeat weekly runs

### 3. Extended Thinking
Used in analysis agent for:
- Complex patch impact assessment
- Cross-subsystem dependency analysis
- Significance scoring

### 4. Tool Use
- HTTP requests to lore.kernel.org
- Git CLI commands
- Database queries
- Blog platform APIs

## Cost Estimates

### Per Weekly Blog Post
- **With prompt caching:** $3-5
- **Without caching:** $15-20

### Monthly (4 blog posts)
- **With prompt caching:** $12-20
- **Without caching:** $60-80

*Based on Claude Opus 4.7 pricing as of May 2026*

## Configuration

### Subsystem Definitions
Edit `config/subsystems.json`:
```json
{
  "xfs": {
    "name": "XFS Filesystem",
    "mailing_lists": ["linux-xfs@vger.kernel.org"],
    "git_repos": ["git://git.kernel.org/pub/scm/fs/xfs/xfs-linux.git"],
    "maintainers": ["Darrick J. Wong", "Chandan Babu R"],
    "priority": "high",
    "keywords": ["xfs", "extent", "btree", "log", "inode"]
  }
}
```

### Prompt Templates
Edit `config/prompts.json`:
```json
{
  "analysis": {
    "system": "You are a Linux kernel expert...",
    "user_template": "Analyze this patch for {subsystem}..."
  },
  "writing": {
    "system": "You are a technical writer...",
    "user_template": "Generate a blog section for {subsystem}..."
  }
}
```

## Development Roadmap

- [x] Project planning and architecture
- [ ] Phase 1: Data collection infrastructure
- [ ] Phase 2: Analysis pipeline with Claude
- [ ] Phase 3: Content generation
- [ ] Phase 4: Automation and publishing
- [ ] Phase 5: Refinement and optimization

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed timeline.

## Example Output

### Sample Blog Post Section
```markdown
## XFS Updates (April 29 - May 5, 2026)

This week saw significant progress in XFS metadata validation and repair 
capabilities. Darrick J. Wong submitted a 12-patch series improving the 
robustness of online filesystem repair, particularly for handling corrupted 
extent B+trees. The series introduces new scrub phases that can detect and 
repair cross-referenced metadata inconsistencies without taking the filesystem 
offline.

Key changes:
- **Online repair improvements** ([patch](https://lore.kernel.org/...)): New 
  inode scanning algorithm reduces repair time by ~40% on large filesystems
- **Metadata validation** ([patch](https://lore.kernel.org/...)): Additional 
  checks for extent overlap detection
- **Performance fix** ([patch](https://lore.kernel.org/...)): Resolved 
  contention in log grant heads under high concurrency

Contributors: Darrick J. Wong, Chandan Babu R, Dave Chinner
```

## Contributing

This is a personal project, but suggestions for improvements are welcome via issues.

## License

MIT License - See LICENSE file

## Resources

- [Linux Kernel Mailing Lists](https://lore.kernel.org/)
- [Kernel.org Git Repositories](https://git.kernel.org/)
- [Claude API Documentation](https://docs.anthropic.com/)
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)
