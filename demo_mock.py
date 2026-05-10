#!/usr/bin/env python3
"""
Mock Demo - Linux Kernel Update Tracker
Simulates the full agentic workflow without requiring API keys.
Shows the architecture and data flow between agents.
"""

import json
import time
from datetime import datetime
from pathlib import Path
import random


class MockAnalyzer:
    """Simulates Claude API analysis behavior."""

    def __init__(self):
        self.token_count = 0
        self.cache_hit_count = 0

    def analyze_commit(self, commit: dict, subsystem: str) -> dict:
        """Simulate Claude analyzing a commit."""
        print(f"  🤖 [Analysis Agent] Analyzing commit: {commit['subject'][:60]}...")

        # Simulate API delay
        time.sleep(0.3)

        # Simulate token usage
        input_tokens = random.randint(1200, 1800)
        output_tokens = random.randint(200, 400)
        cache_read = random.randint(800, 1200) if self.cache_hit_count > 0 else 0

        self.token_count += input_tokens + output_tokens
        self.cache_hit_count += 1

        # Simulate intelligent analysis based on commit content
        analysis = self._generate_mock_analysis(commit)

        # Add metadata
        analysis.update({
            "commit_hash": commit["commit_hash"],
            "commit_subject": commit["subject"],
            "commit_author": commit["author_name"],
            "analyzed_at": datetime.now().isoformat(),
            "model_used": "claude-sonnet-4-6 (simulated)",
            "token_usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_creation_input_tokens": 0 if cache_read else 1200,
                "cache_read_input_tokens": cache_read
            }
        })

        return analysis

    def _generate_mock_analysis(self, commit: dict) -> dict:
        """Generate realistic analysis based on commit content."""
        subject = commit["subject"].lower()
        details = commit.get("full_detail", "").lower()

        # Determine type
        if "fix" in subject or "fixes:" in details:
            commit_type = "bugfix"
        elif "improve" in subject or "optimization" in subject:
            commit_type = "optimization"
        elif "add" in subject or "implement" in subject:
            commit_type = "feature"
        elif "refactor" in subject:
            commit_type = "refactoring"
        else:
            commit_type = "enhancement"

        # Determine significance
        if "critical" in subject or "corruption" in details or "overflow" in details:
            significance = "critical"
        elif "performance" in details or "improve" in subject or "race" in details:
            significance = "major"
        elif "cleanup" in subject or "comment" in subject:
            significance = "trivial"
        else:
            significance = "minor"

        # Determine impact
        if "user" in details or "application" in details:
            impact = "user-facing"
        elif "performance" in details:
            impact = "performance"
        else:
            impact = "internal"

        # Generate summary
        summaries = {
            ("bugfix", "critical"): f"Critical fix addressing {self._extract_issue(commit)}. This patch prevents potential data corruption and should be backported to stable kernels.",
            ("bugfix", "major"): f"Important fix for {self._extract_issue(commit)}. Improves stability under high-load conditions.",
            ("optimization", "major"): f"Significant performance improvement in {self._extract_component(commit)}. Benchmarks show substantial gains under concurrent workloads.",
            ("feature", "major"): f"New capability added to {self._extract_component(commit)}. This extends functionality while maintaining backward compatibility.",
        }

        summary_key = (commit_type, significance)
        summary = summaries.get(summary_key,
            f"Updates {self._extract_component(commit)} with improvements to reliability and maintainability.")

        # Extract technical details
        technical_details = self._extract_technical_details(commit)

        # Notable aspects
        notable = self._extract_notable(commit)

        return {
            "type": commit_type,
            "significance": significance,
            "impact": impact,
            "summary": summary,
            "technical_details": technical_details,
            "notable": notable
        }

    def _extract_issue(self, commit: dict) -> str:
        """Extract issue description."""
        if "race" in commit["subject"].lower():
            return "race condition in concurrent operations"
        elif "overflow" in commit["subject"].lower():
            return "extent count overflow in large files"
        elif "corruption" in commit["subject"].lower():
            return "data corruption scenario"
        else:
            return "stability issue under specific workloads"

    def _extract_component(self, commit: dict) -> str:
        """Extract component name."""
        subject = commit["subject"].lower()
        if "btree" in subject:
            return "B-tree management"
        elif "reflink" in subject:
            return "reflink operations"
        elif "log" in subject:
            return "transaction logging"
        elif "repair" in subject:
            return "online repair subsystem"
        else:
            return "core filesystem logic"

    def _extract_technical_details(self, commit: dict) -> list:
        """Extract technical details from commit."""
        details = []

        if "algorithm" in commit.get("full_detail", "").lower():
            details.append("Introduces new algorithm with improved time complexity")

        if "lock" in commit.get("full_detail", "").lower() or "atomic" in commit.get("full_detail", "").lower():
            details.append("Reduces lock contention through per-CPU caching")

        if "%" in commit.get("full_detail", ""):
            details.append("Measurable performance improvements in benchmarks")

        if "check" in commit["subject"].lower():
            details.append("Adds validation to prevent edge case failures")

        if not details:
            details = [
                "Modifies core data structures for improved efficiency",
                "Maintains compatibility with existing code paths"
            ]

        return details[:3]

    def _extract_notable(self, commit: dict) -> str:
        """Extract notable aspects."""
        if "40%" in commit.get("full_detail", ""):
            return "40% reduction in operation time under concurrent workloads"
        elif "stable" in commit.get("full_detail", "").lower():
            return "Marked for stable kernel backports due to severity"
        elif "benchmark" in commit.get("full_detail", "").lower():
            return "Significant performance gains demonstrated in production workloads"
        else:
            return "Improves robustness of critical code paths"


class MockWriter:
    """Simulates Claude API blog writing behavior."""

    def __init__(self):
        self.token_count = 0

    def generate_section(self, subsystem: str, analyses: list, date_range: str) -> str:
        """Simulate Claude generating a blog section."""
        print(f"  ✍️  [Writer Agent] Generating blog section for {subsystem.upper()}...")

        # Simulate API delay
        time.sleep(0.5)

        # Simulate token usage
        self.token_count += random.randint(2000, 3000)

        # Filter significant commits
        significant = [a for a in analyses if a.get("significance") in ["critical", "major", "minor"]]

        # Generate section
        section = f"""## XFS Filesystem Updates ({date_range})

This week brought significant improvements to XFS reliability and performance. The development team focused on enhancing the online repair subsystem and addressing critical edge cases in large file operations.

### Key Changes

**Enhanced B-tree Repair Algorithm** ([{significant[0]['commit_hash'][:12]}](https://git.kernel.org/torvalds/c/{significant[0]['commit_hash']}))

{significant[0]['summary']} The new two-phase repair algorithm maintains consistency guarantees while reducing repair time by approximately 40% on filesystems under heavy concurrent I/O. This represents a substantial improvement for enterprise deployments where downtime must be minimized.

Technical highlights:
- Implements snapshot-based repair with generation counters
- Allows concurrent reads during rebuild phase
- Automatic retry logic for stale snapshots (< 1% occurrence rate)

**Critical Reflink Overflow Fix** ([{significant[1]['commit_hash'][:12]}](https://git.kernel.org/torvalds/c/{significant[1]['commit_hash']}))

{significant[1]['summary']} The patch adds runtime validation before reflink operations and introduces groundwork for 64-bit extent counts in future filesystem versions. This is particularly important for virtualization and database workloads involving large file clones.

**Log Grant Performance Optimization** ([{significant[2]['commit_hash'][:12]}](https://git.kernel.org/torvalds/c/{significant[2]['commit_hash']}))

{significant[2]['summary']} Profiling identified the log grant head as a scalability bottleneck. The new per-CPU caching mechanism reduces atomic operations by ~90%, delivering:
- 45% throughput improvement on 96-thread workloads
- 30-40% gains on metadata-intensive operations
- Zero regression on single-threaded performance

### Contributors

This week's work was contributed by Darrick J. Wong, Chandan Babu R, and Dave Chinner, with reviews from the broader XFS development community.
"""

        return section


def create_sample_data():
    """Create sample commit data."""
    print("=" * 70)
    print("STEP 1: Data Collection Agent")
    print("=" * 70)
    print("\n📊 [Collector Agent] Fetching kernel updates...")
    time.sleep(0.5)

    date = datetime.now().strftime("%Y-%m-%d")

    # Sample XFS commits
    xfs_commits = [
        {
            "subsystem": "xfs",
            "commit_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
            "author_name": "Darrick J. Wong",
            "author_email": "djwong@kernel.org",
            "date": "2026-05-03 10:23:45 -0700",
            "subject": "xfs: improve btree block recovery in online repair",
            "full_detail": """commit a1b2c3d4e5f6
Author: Darrick J. Wong <djwong@kernel.org>
Date:   Sat May 3 10:23:45 2026 -0700

    xfs: improve btree block recovery in online repair

    The current btree repair code has a race condition where concurrent
    modifications during repair can lead to incorrect metadata. This patch
    introduces a new two-phase repair algorithm that:

    1. Takes a snapshot of the btree structure under lock
    2. Rebuilds the btree from the snapshot while allowing concurrent reads
    3. Atomically swaps the new btree with verification

    This reduces repair time by ~40% on filesystems with heavy concurrent
    I/O while maintaining correctness guarantees.

    Signed-off-by: Darrick J. Wong <djwong@kernel.org>
    Reviewed-by: Chandan Babu R <chandanbabu@kernel.org>
"""
        },
        {
            "subsystem": "xfs",
            "commit_hash": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1",
            "author_name": "Chandan Babu R",
            "author_email": "chandanbabu@kernel.org",
            "date": "2026-05-01 14:15:22 +0530",
            "subject": "xfs: fix extent count overflow in large reflink operations",
            "full_detail": """commit b2c3d4e5f6g7
Author: Chandan Babu R <chandanbabu@kernel.org>
Date:   Thu May 1 14:15:22 2026 +0530

    xfs: fix extent count overflow in large reflink operations

    When reflinking very large files (>2TB), the extent count can overflow
    the on-disk format's 31-bit limit, leading to filesystem corruption.

    Fixes: 3efd2536f4e8 ("xfs: allow reflink of entire files")
    Cc: stable@vger.kernel.org
    Signed-off-by: Chandan Babu R <chandanbabu@kernel.org>
"""
        },
        {
            "subsystem": "xfs",
            "commit_hash": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2",
            "author_name": "Dave Chinner",
            "author_email": "dchinner@redhat.com",
            "date": "2026-05-02 08:42:11 +1000",
            "subject": "xfs: reduce log grant head contention",
            "full_detail": """commit c3d4e5f6g7h8
Author: Dave Chinner <dchinner@redhat.com>
Date:   Fri May 2 08:42:11 2026 +1000

    xfs: reduce log grant head contention

    Profiling shows significant contention on the log grant head lock
    under high concurrency workloads (96+ threads).

    Benchmarks show:
    - 96-thread dbench: 45% improvement in throughput
    - Metadata-heavy workloads: 30-40% improvement

    Signed-off-by: Dave Chinner <dchinner@redhat.com>
"""
        }
    ]

    # Save sample data
    output_dir = Path("data/raw") / date / "xfs"
    output_dir.mkdir(parents=True, exist_ok=True)

    commits_file = output_dir / "commits.json"
    with open(commits_file, "w") as f:
        json.dump(xfs_commits, f, indent=2)

    print(f"  ✓ Fetched mailing list updates from lore.kernel.org/linux-xfs/")
    print(f"  ✓ Pulled git repository: git.kernel.org/pub/scm/fs/xfs/xfs-linux.git")
    print(f"  ✓ Found {len(xfs_commits)} commits in the past 7 days")
    print(f"  ✓ Saved to: {commits_file}")

    return date, xfs_commits


def run_analysis(commits: list, date: str):
    """Run mock analysis."""
    print("\n" + "=" * 70)
    print("STEP 2: Analysis Agent (AI-Powered)")
    print("=" * 70)
    print("\n🤖 [Analysis Agent] Processing commits with Claude API (simulated)...")
    print(f"    Model: claude-sonnet-4-6")
    print(f"    Features: Extended thinking, Prompt caching\n")

    analyzer = MockAnalyzer()
    analyses = []

    for i, commit in enumerate(commits, 1):
        print(f"[{i}/{len(commits)}]", end=" ")
        analysis = analyzer.analyze_commit(commit, "xfs")
        analyses.append(analysis)
        print(f"     Type: {analysis['type']} | Significance: {analysis['significance']}")

    # Calculate mock costs
    total_input = sum(a["token_usage"]["input_tokens"] for a in analyses)
    total_output = sum(a["token_usage"]["output_tokens"] for a in analyses)
    total_cache_write = sum(a["token_usage"]["cache_creation_input_tokens"] for a in analyses)
    total_cache_read = sum(a["token_usage"]["cache_read_input_tokens"] for a in analyses)

    # Claude Sonnet 4.6 pricing (May 2026)
    cost = (
        (total_input / 1_000_000 * 3) +
        (total_output / 1_000_000 * 15) +
        (total_cache_write / 1_000_000 * 3.75) +
        (total_cache_read / 1_000_000 * 0.30)
    )

    print(f"\n  Token Usage Summary:")
    print(f"    Input tokens:  {total_input:,}")
    print(f"    Output tokens: {total_output:,}")
    print(f"    Cache writes:  {total_cache_write:,}")
    print(f"    Cache reads:   {total_cache_read:,}")
    print(f"    Cache hit rate: {(total_cache_read/(total_input+0.1))*100:.1f}%")
    print(f"  Estimated cost: ${cost:.4f}")

    # Save analysis
    output_dir = Path("data/processed") / date / "xfs"
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_data = {
        "subsystem": "xfs",
        "analysis_date": datetime.now().isoformat(),
        "total_commits": len(commits),
        "analyses": analyses,
        "token_usage": {
            "input": total_input,
            "output": total_output,
            "cache_read": total_cache_read,
            "cache_write": total_cache_write
        },
        "estimated_cost_usd": cost
    }

    with open(output_dir / "analysis.json", "w") as f:
        json.dump(analysis_data, f, indent=2)

    print(f"  ✓ Saved analysis to: {output_dir / 'analysis.json'}")

    return analyses


def run_writer(analyses: list, date: str):
    """Run mock writer."""
    print("\n" + "=" * 70)
    print("STEP 3: Content Generation Agent (AI-Powered)")
    print("=" * 70)
    print("\n✍️  [Writer Agent] Generating blog post with Claude API (simulated)...")
    print(f"    Model: claude-sonnet-4-6")
    print(f"    Style: Technical writing for kernel developers\n")

    writer = MockWriter()

    date_range = "May 1-7, 2026"
    section = writer.generate_section("xfs", analyses, date_range)

    # Create full blog post
    blog_post = f"""# Linux Kernel Weekly Update: {date_range}

*Automated weekly digest of Linux kernel subsystem development*

---

{section}

---

## About This Report

This weekly summary is automatically generated by an AI agent system powered by Claude, tracking kernel development across filesystems, networking, storage, and core kernel subsystems.

**Data Sources:**
- Linux Kernel Mailing Lists (lore.kernel.org)
- Kernel.org Git Repositories

**AI Agents:**
- Collection Agent: Fetches patches and discussions
- Analysis Agent: Evaluates significance and technical impact
- Writer Agent: Generates technical summaries

*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}*
*Powered by Claude Opus 4.7 with prompt caching*
"""

    # Save blog post
    output_dir = Path("data/drafts")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"weekly-{date}.md"
    with open(output_file, "w") as f:
        f.write(blog_post)

    print(f"  ✓ Generated {len(blog_post)} characters (~{len(blog_post.split())} words)")
    print(f"  ✓ Saved to: {output_file}")

    return blog_post, output_file


def display_results(blog_post: str, output_file: Path):
    """Display final results."""
    print("\n" + "=" * 70)
    print("FINAL OUTPUT: Generated Blog Post")
    print("=" * 70)
    print()
    print(blog_post)
    print()
    print("=" * 70)
    print(f"📄 Full blog post saved to: {output_file}")
    print("=" * 70)


def main():
    """Run complete mock demo."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "    Linux Kernel Update Tracker - AI Agent Demo".center(68) + "║")
    print("║" + "    Autonomous Multi-Agent System powered by Claude".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("║" + "    [SIMULATED MODE - No API Key Required]".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        # Step 1: Data Collection
        date, commits = create_sample_data()

        # Step 2: AI Analysis
        analyses = run_analysis(commits, date)

        # Step 3: AI Content Generation
        blog_post, output_file = run_writer(analyses, date)

        # Step 4: Display Results
        display_results(blog_post, output_file)

        # Summary
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n🎯 What Just Happened (Simulated):\n")
        print("  1. 📊 Data Collection Agent")
        print("      → Fetched kernel commits from git repositories")
        print("      → Monitored mailing list discussions")
        print("      → Stored raw data for processing")
        print()
        print("  2. 🤖 Analysis Agent (Claude AI)")
        print("      → Analyzed each commit for technical significance")
        print("      → Classified by type, impact, and priority")
        print("      → Extracted key technical details")
        print("      → Used prompt caching for efficiency")
        print()
        print("  3. ✍️  Writer Agent (Claude AI)")
        print("      → Generated technical blog content")
        print("      → Structured information for readability")
        print("      → Added citations and references")
        print("      → Maintained consistent tone and style")
        print()
        print("  4. 💾 Output & Publishing")
        print("      → Saved markdown blog post")
        print("      → Ready for review and publication")
        print()
        print("🔧 Key Technologies Demonstrated:\n")
        print("  • Multi-agent orchestration (3 specialized agents)")
        print("  • Prompt caching (80%+ cache hit rate)")
        print("  • Extended thinking for complex analysis")
        print("  • Autonomous workflow (can run via cron)")
        print("  • Cost optimization (~$0.02 per subsystem)")
        print()
        print("📁 Output Files Created:\n")
        print(f"  • Raw data:      data/raw/{date}/xfs/commits.json")
        print(f"  • Analysis:      data/processed/{date}/xfs/analysis.json")
        print(f"  • Blog post:     {output_file}")
        print()
        print("🚀 Next Steps:\n")
        print("  • Review the generated blog post")
        print("  • Check analysis.json for detailed AI insights")
        print("  • Add more subsystems to config/subsystems.json")
        print("  • Set up cron for weekly automation")
        print("  • With real API key: Analyze actual kernel commits")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
