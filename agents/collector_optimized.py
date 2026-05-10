#!/usr/bin/env python3
"""
Data Collection Agent - Optimized Version
Uses a SINGLE shared Linux kernel repository instead of cloning per subsystem.

Key improvements:
- Clones Linux kernel ONCE (saves ~12 GB)
- Queries different filesystem paths from shared repo
- Much faster subsequent runs
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests
from typing import List, Dict, Optional
import subprocess


class OptimizedKernelCollector:
    """Collects kernel data using a shared repository."""

    def __init__(self, config_path: str = "config/subsystems.json"):
        """Initialize collector with subsystem configuration."""
        self.config_path = Path(config_path)
        self.subsystems = self._load_config()
        self.data_dir = Path("data/raw")

        # Single shared repository for all subsystems
        self.shared_repo_dir = Path("data/repos/linux")
        self.shared_repo_url = "git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"

    def _load_config(self) -> Dict:
        """Load subsystem configuration."""
        with open(self.config_path) as f:
            return json.load(f)

    def _ensure_shared_repo(self):
        """
        Ensure shared Linux kernel repository exists.
        Clone once, reuse for all subsystems.
        """
        if self.shared_repo_dir.exists():
            print(f"✓ Shared repository exists: {self.shared_repo_dir}")
            print(f"  Updating repository...")
            try:
                subprocess.run(
                    ["git", "-C", str(self.shared_repo_dir), "fetch", "origin"],
                    check=True,
                    capture_output=True,
                    timeout=300
                )
                subprocess.run(
                    ["git", "-C", str(self.shared_repo_dir), "reset", "--hard", "origin/master"],
                    check=True,
                    capture_output=True
                )
                print(f"✓ Repository updated")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Update timed out, using existing repo")
            except Exception as e:
                print(f"⚠️  Update failed: {e}, using existing repo")
        else:
            print(f"Cloning shared Linux kernel repository...")
            print(f"  This will take 5-10 minutes and use ~6 GB")
            print(f"  URL: {self.shared_repo_url}")
            print(f"  Destination: {self.shared_repo_dir}")

            self.shared_repo_dir.parent.mkdir(parents=True, exist_ok=True)

            try:
                # Clone with progress
                subprocess.run(
                    ["git", "clone", "--progress", self.shared_repo_url, str(self.shared_repo_dir)],
                    check=True,
                    timeout=600  # 10 minute timeout
                )
                print(f"✓ Repository cloned successfully")
            except subprocess.TimeoutExpired:
                print(f"❌ Clone timed out after 10 minutes")
                raise
            except Exception as e:
                print(f"❌ Clone failed: {e}")
                raise

    def collect_mailing_list_threads(
        self,
        subsystem: str,
        days: int = 7
    ) -> List[Dict]:
        """Fetch mailing list threads from lore.kernel.org."""
        config = self.subsystems.get(subsystem)
        if not config:
            raise ValueError(f"Unknown subsystem: {subsystem}")

        lore_url = config.get("lore_url")
        if not lore_url:
            print(f"No lore URL configured for {subsystem}")
            return []

        atom_url = f"{lore_url.rstrip('/')}/new.atom"

        try:
            print(f"Fetching mailing list updates from {atom_url}")
            response = requests.get(atom_url, timeout=30)
            response.raise_for_status()

            return [{
                "source": "lore.kernel.org",
                "subsystem": subsystem,
                "feed_url": atom_url,
                "raw_content": response.text,
                "fetched_at": datetime.now().isoformat()
            }]

        except requests.RequestException as e:
            print(f"⚠️  Mailing list fetch failed: {e}")
            return []

    def collect_git_commits(
        self,
        subsystem: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Fetch git commits from shared repository.

        Args:
            subsystem: Subsystem name
            days: Number of days to look back

        Returns:
            List of commit metadata
        """
        config = self.subsystems.get(subsystem)
        if not config:
            raise ValueError(f"Unknown subsystem: {subsystem}")

        # Determine filesystem path in kernel tree
        subsystem_paths = {
            # Filesystems
            "xfs": "fs/xfs/",
            "ext4": "fs/ext4/",
            "btrfs": "fs/btrfs/",
            "overlayfs": "fs/overlayfs/",
            "fuse": "fs/fuse/",
            "nfs": "fs/nfs/",
            "nfsd": "fs/nfsd/",
            "cifs": "fs/smb/client/",
            "smb": "fs/smb/",
            # Core subsystems
            "vfs": "fs/",  # Virtual File System layer
            "block": "block/",  # Block I/O layer
            "nvme": "drivers/nvme/",  # NVMe storage
            "md": "drivers/md/",  # Software RAID
            "scsi": "drivers/scsi/",  # SCSI subsystem
            # Storage management
            "dm": "drivers/md/",  # Device Mapper (same tree as md)
            # Distributed filesystems
            "ceph": "fs/ceph/",  # CephFS client
            # Clustered filesystems
            "gfs2": "fs/gfs2/",  # GFS2 clustered filesystem
        }

        fs_path = subsystem_paths.get(subsystem, f"fs/{subsystem}/")

        print(f"Collecting commits from: {fs_path}")
        print(f"Looking back: {days} days")

        commits = []

        try:
            # Get commits from last N days
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            # Get commit hashes
            result = subprocess.run(
                [
                    "git", "-C", str(self.shared_repo_dir), "log",
                    f"--since={since_date}",
                    "--format=%H|%an|%ae|%ad|%s",
                    "--date=iso",
                    "--", fs_path
                ],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse commits
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|", 4)
                if len(parts) >= 5:
                    commit_hash, author_name, author_email, date, subject = parts

                    # Get full commit details
                    commit_detail = subprocess.run(
                        ["git", "-C", str(self.shared_repo_dir), "show", "--stat", commit_hash],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=30
                    )

                    commits.append({
                        "subsystem": subsystem,
                        "repository": self.shared_repo_url,
                        "filesystem_path": fs_path,
                        "commit_hash": commit_hash,
                        "author_name": author_name,
                        "author_email": author_email,
                        "date": date,
                        "subject": subject,
                        "full_detail": commit_detail.stdout,
                        "fetched_at": datetime.now().isoformat()
                    })

            print(f"✓ Found {len(commits)} commits for {subsystem}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error processing git repository: {e}")

        return commits

    def save_data(self, subsystem: str, data: Dict, date: str = None):
        """Save collected data to disk."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        output_dir = self.data_dir / date / subsystem
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save mailing list data
        if data.get("mailing_list"):
            ml_file = output_dir / "mailing_list.json"
            with open(ml_file, "w") as f:
                json.dump(data["mailing_list"], f, indent=2)
            print(f"✓ Saved mailing list data to {ml_file}")

        # Save git commits
        if data.get("commits"):
            commits_file = output_dir / "commits.json"
            with open(commits_file, "w") as f:
                json.dump(data["commits"], f, indent=2)
            print(f"✓ Saved {len(data['commits'])} commits to {commits_file}")

    def collect_subsystem(self, subsystem: str, days: int = 7) -> Dict:
        """Collect all data for a single subsystem."""
        print(f"\n{'='*60}")
        print(f"Collecting data for {subsystem.upper()}")
        print(f"{'='*60}")

        data = {
            "subsystem": subsystem,
            "collection_date": datetime.now().isoformat(),
            "days_back": days,
            "mailing_list": self.collect_mailing_list_threads(subsystem, days),
            "commits": self.collect_git_commits(subsystem, days)
        }

        return data

    def collect_all(self, days: int = 7, subsystems: Optional[List[str]] = None):
        """Collect data for all configured subsystems."""
        # Ensure shared repository exists ONCE
        print("=" * 60)
        print("STEP 1: Ensure shared Linux kernel repository")
        print("=" * 60)
        self._ensure_shared_repo()

        target_subsystems = subsystems or list(self.subsystems.keys())

        print(f"\n{'='*60}")
        print(f"STEP 2: Collect data for {len(target_subsystems)} subsystems")
        print(f"{'='*60}")
        print(f"Looking back {days} days")

        for subsystem in target_subsystems:
            try:
                data = self.collect_subsystem(subsystem, days)
                self.save_data(subsystem, data)
            except Exception as e:
                print(f"❌ Error collecting data for {subsystem}: {e}")
                continue

        print(f"\n{'='*60}")
        print(f"✅ Data collection complete!")
        print(f"{'='*60}")
        print(f"Data saved to: {self.data_dir}/{datetime.now().strftime('%Y-%m-%d')}/")
        print(f"Shared repository: {self.shared_repo_dir}")
        print(f"Disk usage saved: ~12 GB (single repo vs. 3 separate clones)")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Collect kernel development data (optimized with shared repo)"
    )
    parser.add_argument(
        "--subsystem",
        help="Specific subsystem to collect (e.g., xfs, ext4)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    parser.add_argument(
        "--config",
        default="config/subsystems.json",
        help="Path to subsystems configuration file"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Collect data for all configured subsystems"
    )

    args = parser.parse_args()

    collector = OptimizedKernelCollector(config_path=args.config)

    if args.subsystem:
        # Ensure repo exists first
        collector._ensure_shared_repo()
        data = collector.collect_subsystem(args.subsystem, args.days)
        collector.save_data(args.subsystem, data)
    elif args.all:
        collector.collect_all(days=args.days)
    else:
        print("Error: Must specify --subsystem or --all")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
