#!/usr/bin/env python3
"""
Demo script for Linux Kernel Update Tracker
Demonstrates the full agentic workflow with sample data.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent / "agents"))

from analyzer import KernelDataAnalyzer
from writer import KernelBlogWriter


def create_sample_data():
    """Create sample commit data for demonstration."""
    print("=" * 70)
    print("DEMO: Creating sample commit data")
    print("=" * 70)

    date = datetime.now().strftime("%Y-%m-%d")

    # Sample XFS commits (realistic examples)
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

    The new algorithm uses a generation counter to detect stale snapshots
    and automatically retries if necessary. Testing shows this happens
    < 1% of the time under normal workloads.

    Signed-off-by: Darrick J. Wong <djwong@kernel.org>
    Reviewed-by: Chandan Babu R <chandanbabu@kernel.org>

 fs/xfs/scrub/repair.c      | 234 ++++++++++++++++++++++++++++++++-----
 fs/xfs/scrub/repair.h      |  45 ++++++++
 fs/xfs/libxfs/xfs_btree.c  |  87 ++++++++++++--
 fs/xfs/libxfs/xfs_btree.h  |   5 +
 4 files changed, 337 insertions(+), 34 deletions(-)
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

    This adds runtime checks before reflink operations and returns EFBIG
    if the operation would exceed limits. Also adds a new extent count
    format flag for filesystems that support 64-bit extent counts (planned
    for v6 format).

    This is a critical fix for users doing large VM image clones or
    database snapshot operations.

    Reported-by: Hugh Dickins <hughd@google.com>
    Fixes: 3efd2536f4e8 ("xfs: allow reflink of entire files")
    Cc: stable@vger.kernel.org
    Signed-off-by: Chandan Babu R <chandanbabu@kernel.org>

 fs/xfs/libxfs/xfs_reflink.c | 67 +++++++++++++++++++++++++++++++++++++
 fs/xfs/xfs_ioctl.c          | 12 +++++++
 2 files changed, 79 insertions(+)
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
    under high concurrency workloads (96+ threads). This is due to
    every transaction attempting to reserve log space atomically.

    This patch introduces per-CPU grant head caches that batch log
    reservations. Each CPU maintains a small cache (~64KB) of pre-
    reserved log space, reducing atomic operations by ~90%.

    Benchmarks show:
    - 96-thread dbench: 45% improvement in throughput
    - Metadata-heavy workloads: 30-40% improvement
    - Single-threaded: no regression

    The cache size is tunable via sysfs for workloads with different
    characteristics.

    Signed-off-by: Dave Chinner <dchinner@redhat.com>

 fs/xfs/xfs_log.c      | 312 ++++++++++++++++++++++++++++++++++++++----
 fs/xfs/xfs_log_priv.h |  23 ++++
 fs/xfs/xfs_sysfs.c    |  45 ++++++
 3 files changed, 357 insertions(+), 23 deletions(-)
"""
        }
    ]

    # Save sample data
    output_dir = Path("data/raw") / date / "xfs"
    output_dir.mkdir(parents=True, exist_ok=True)

    commits_file = output_dir / "commits.json"
    with open(commits_file, "w") as f:
        json.dump(xfs_commits, f, indent=2)

    print(f"✓ Created {len(xfs_commits)} sample XFS commits")
    print(f"✓ Saved to: {commits_file}")

    return date


def run_analysis(subsystem: str, date: str):
    """Run analysis agent on sample data."""
    print("\n" + "=" * 70)
    print("DEMO: Running Analysis Agent (using Claude API)")
    print("=" * 70)

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠️  ANTHROPIC_API_KEY not set!")
        print("Please set your API key:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    analyzer = KernelDataAnalyzer(model="claude-sonnet-4-6")  # Using Sonnet for demo
    analysis = analyzer.analyze_subsystem(subsystem, date)
    analyzer.save_analysis(analysis, subsystem, date)

    return analysis


def run_writer(subsystems: list, date: str):
    """Run writer agent to generate blog post."""
    print("\n" + "=" * 70)
    print("DEMO: Running Writer Agent (using Claude API)")
    print("=" * 70)

    writer = KernelBlogWriter(model="claude-sonnet-4-6")

    date_range = "May 1-5, 2026"
    blog_post = writer.generate_blog_post(
        subsystems=subsystems,
        date=date,
        date_range=date_range
    )

    writer.save_blog_post(blog_post, date)

    return blog_post


def display_results(blog_post: str):
    """Display final results."""
    print("\n" + "=" * 70)
    print("DEMO: Generated Blog Post Preview")
    print("=" * 70)
    print()

    # Show first 1500 characters
    preview = blog_post[:1500]
    if len(blog_post) > 1500:
        preview += "\n\n... (truncated for preview) ..."

    print(preview)
    print()
    print("=" * 70)
    print("Full blog post saved to: data/drafts/weekly-{date}.md".format(
        date=datetime.now().strftime("%Y-%m-%d")
    ))
    print("=" * 70)


def main():
    """Run complete demo."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Linux Kernel Update Tracker - AI Agent Demo".center(68) + "║")
    print("║" + "  Autonomous Multi-Agent System powered by Claude".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        # Step 1: Create sample data
        date = create_sample_data()

        # Step 2: Run analysis
        analysis = run_analysis("xfs", date)

        # Step 3: Generate blog post
        blog_post = run_writer(["xfs"], date)

        # Step 4: Display results
        display_results(blog_post)

        print("\n✅ Demo completed successfully!")
        print("\nWhat just happened:")
        print("  1. 📊 Sample kernel commit data was created")
        print("  2. 🤖 Analysis Agent (Claude) analyzed each commit for significance")
        print("  3. ✍️  Writer Agent (Claude) generated a technical blog post")
        print("  4. 💾 Output saved to data/drafts/")
        print("\nThis demonstrates:")
        print("  • Multi-agent orchestration")
        print("  • Prompt caching for cost efficiency")
        print("  • Specialized agents with different system prompts")
        print("  • End-to-end autonomous workflow")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
