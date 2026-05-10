#!/usr/bin/env python3
"""
Data Collection Agent
Fetches kernel updates from mailing lists and git repositories.
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

class KernelDataCollector:
    """Collects kernel development data from multiple sources."""

    def __init__(self, config_path: str = "config/subsystems.json"):
        """Initialize collector with subsystem configuration."""
        self.config_path = Path(config_path)
        self.subsystems = self._load_config()
        self.data_dir = Path("data/raw")

    def _load_config(self) -> Dict:
        """Load subsystem configuration."""
        with open(self.config_path) as f:
            return json.load(f)

    def collect_mailing_list_threads(
        self,
        subsystem: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Fetch mailing list threads from lore.kernel.org.

        Args:
            subsystem: Subsystem name (e.g., 'xfs', 'ext4')
            days: Number of days to look back

        Returns:
            List of email thread metadata
        """
        config = self.subsystems.get(subsystem)
        if not config:
            raise ValueError(f"Unknown subsystem: {subsystem}")

        lore_url = config.get("lore_url")
        if not lore_url:
            print(f"No lore URL configured for {subsystem}")
            return []

        # lore.kernel.org provides Atom feeds for recent activity
        # Format: https://lore.kernel.org/{list}/new.atom
        atom_url = f"{lore_url.rstrip('/')}/new.atom"

        try:
            print(f"Fetching mailing list updates from {atom_url}")
            response = requests.get(atom_url, timeout=30)
            response.raise_for_status()

            # For now, save raw atom feed
            # TODO: Parse XML and extract thread metadata
            return [{
                "source": "lore.kernel.org",
                "subsystem": subsystem,
                "feed_url": atom_url,
                "raw_content": response.text,
                "fetched_at": datetime.now().isoformat()
            }]

        except requests.RequestException as e:
            print(f"Error fetching mailing list: {e}")
            return []

    def collect_git_commits(
        self,
        subsystem: str,
        days: int = 7,
        clone_dir: str = "data/repos"
    ) -> List[Dict]:
        """
        Fetch git commits from kernel repositories.

        Args:
            subsystem: Subsystem name
            days: Number of days to look back
            clone_dir: Directory to clone repositories

        Returns:
            List of commit metadata
        """
        config = self.subsystems.get(subsystem)
        if not config:
            raise ValueError(f"Unknown subsystem: {subsystem}")

        git_repos = config.get("git_repos", [])
        if not git_repos:
            print(f"No git repositories configured for {subsystem}")
            return []

        commits = []
        repo_dir = Path(clone_dir) / subsystem

        for repo_url in git_repos:
            print(f"Processing git repository: {repo_url}")

            try:
                # Clone or update repository
                if repo_dir.exists():
                    print(f"Updating existing repository at {repo_dir}")
                    subprocess.run(
                        ["git", "-C", str(repo_dir), "fetch", "origin"],
                        check=True,
                        capture_output=True
                    )
                    subprocess.run(
                        ["git", "-C", str(repo_dir), "reset", "--hard", "origin/master"],
                        check=True,
                        capture_output=True
                    )
                else:
                    print(f"Cloning repository to {repo_dir}")
                    repo_dir.parent.mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["git", "clone", repo_url, str(repo_dir)],
                        check=True,
                        capture_output=True
                    )

                # Get commits from last N days
                since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                result = subprocess.run(
                    [
                        "git", "-C", str(repo_dir), "log",
                        f"--since={since_date}",
                        "--format=%H|%an|%ae|%ad|%s",
                        "--date=iso"
                    ],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Parse commit log
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue

                    parts = line.split("|")
                    if len(parts) >= 5:
                        commit_hash, author_name, author_email, date, subject = parts[:5]

                        # Get full commit details
                        commit_detail = subprocess.run(
                            ["git", "-C", str(repo_dir), "show", "--stat", commit_hash],
                            capture_output=True,
                            text=True,
                            check=True
                        )

                        commits.append({
                            "subsystem": subsystem,
                            "repository": repo_url,
                            "commit_hash": commit_hash,
                            "author_name": author_name,
                            "author_email": author_email,
                            "date": date,
                            "subject": subject,
                            "full_detail": commit_detail.stdout,
                            "fetched_at": datetime.now().isoformat()
                        })

                print(f"Found {len(commits)} commits for {subsystem}")

            except subprocess.CalledProcessError as e:
                print(f"Error processing git repository: {e}")
                continue

        return commits

    def save_data(self, subsystem: str, data: Dict, date: str = None):
        """
        Save collected data to disk.

        Args:
            subsystem: Subsystem name
            data: Data to save
            date: Date string (YYYY-MM-DD), defaults to today
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        output_dir = self.data_dir / date / subsystem
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save mailing list data
        if data.get("mailing_list"):
            ml_file = output_dir / "mailing_list.json"
            with open(ml_file, "w") as f:
                json.dump(data["mailing_list"], f, indent=2)
            print(f"Saved mailing list data to {ml_file}")

        # Save git commits
        if data.get("commits"):
            commits_file = output_dir / "commits.json"
            with open(commits_file, "w") as f:
                json.dump(data["commits"], f, indent=2)
            print(f"Saved {len(data['commits'])} commits to {commits_file}")

    def collect_subsystem(self, subsystem: str, days: int = 7) -> Dict:
        """
        Collect all data for a single subsystem.

        Args:
            subsystem: Subsystem name
            days: Number of days to look back

        Returns:
            Dictionary with collected data
        """
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
        """
        Collect data for all configured subsystems.

        Args:
            days: Number of days to look back
            subsystems: List of specific subsystems to collect, or None for all
        """
        target_subsystems = subsystems or list(self.subsystems.keys())

        print(f"Starting data collection for {len(target_subsystems)} subsystems")
        print(f"Looking back {days} days")

        for subsystem in target_subsystems:
            try:
                data = self.collect_subsystem(subsystem, days)
                self.save_data(subsystem, data)
            except Exception as e:
                print(f"Error collecting data for {subsystem}: {e}")
                continue

        print(f"\nData collection complete!")
        print(f"Data saved to: {self.data_dir}/{datetime.now().strftime('%Y-%m-%d')}/")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Collect kernel development data from mailing lists and git"
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

    collector = KernelDataCollector(config_path=args.config)

    if args.subsystem:
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
