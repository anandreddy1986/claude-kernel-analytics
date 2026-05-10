#!/usr/bin/env python3
"""
Content Generation Agent - Vertex AI Version
Generates blog posts from analyzed kernel data using Claude via Vertex AI.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from anthropic import AnthropicVertex


class KernelBlogWriterVertexAI:
    """Generates blog posts from kernel analysis data using Claude via Vertex AI."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6@20250514",
        config_path: str = "config/subsystems.json",
        project_id: Optional[str] = None,
        region: str = "us-east5"
    ):
        """
        Initialize blog writer with Vertex AI.

        Args:
            model: Claude model ID on Vertex AI
            config_path: Path to subsystems configuration
            project_id: GCP project ID (or set GOOGLE_CLOUD_PROJECT env var)
            region: GCP region (default: us-east5)
        """
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError(
                "GCP project ID required. Set GOOGLE_CLOUD_PROJECT environment variable "
                "or pass project_id parameter"
            )

        self.region = region
        self.model = model

        # Initialize Vertex AI client
        self.client = AnthropicVertex(
            region=self.region,
            project_id=self.project_id
        )

        # Load subsystem configurations
        with open(config_path) as f:
            self.subsystems = json.load(f)

    def _get_writing_guidelines(self) -> str:
        """Get cached writing guidelines for blog posts."""
        return """# Technical Writing Guidelines

## Style
- Write for experienced systems engineers and kernel developers
- Be technical but accessible
- Focus on the "why" and impact, not just the "what"
- Use active voice and clear, concise language
- Include specific technical details (function names, data structures, algorithms)

## Structure for Subsystem Sections
1. Opening paragraph: High-level summary of the week's activity
2. Key changes: 3-5 most important updates with:
   - Concise description
   - Technical details
   - Impact/motivation
   - Link to patch/commit
3. Contributors: Acknowledge key developers
4. Length: 200-400 words per subsystem

## Tone
- Professional and informative
- Neutral (avoid hype or dramatic language)
- Respectful of contributors' work
- Educational where appropriate
"""

    def generate_subsystem_section(
        self,
        subsystem: str,
        analysis: Dict,
        date_range: str = "past week"
    ) -> str:
        """
        Generate a blog post section for a single subsystem.

        Args:
            subsystem: Subsystem name
            analysis: Analysis results from analyzer agent
            date_range: Time period covered (e.g., "April 29 - May 5, 2026")

        Returns:
            Markdown formatted blog section
        """
        subsystem_config = self.subsystems.get(subsystem, {})
        subsystem_name = subsystem_config.get("name", subsystem.upper())

        # Filter out significant commits
        analyses = analysis.get("analyses", [])
        significant_commits = [
            a for a in analyses
            if a.get("significance") in ["critical", "major", "minor"]
            and not a.get("error")
        ]

        if not significant_commits:
            print(f"No significant commits for {subsystem}, skipping blog section")
            return ""

        # Prepare data for Claude
        commits_summary = []
        for a in significant_commits[:10]:  # Limit to top 10
            commits_summary.append({
                "subject": a.get("commit_subject", ""),
                "author": a.get("commit_author", ""),
                "type": a.get("type", ""),
                "significance": a.get("significance", ""),
                "impact": a.get("impact", ""),
                "summary": a.get("summary", ""),
                "technical_details": a.get("technical_details", []),
                "notable": a.get("notable", ""),
                "commit_hash": a.get("commit_hash", "")[:12]
            })

        prompt = f"""Generate a blog post section for the **{subsystem_name}** subsystem covering {date_range}.

**Commits to cover ({len(commits_summary)} total):**

{json.dumps(commits_summary, indent=2)}

**Subsystem context:**
- Category: {subsystem_config.get('category', 'N/A')}
- Maintainers: {', '.join(subsystem_config.get('maintainers', []))}
- Description: {subsystem_config.get('description', '')}

Generate a well-structured blog section that:
1. Starts with a compelling overview paragraph
2. Highlights 3-5 most significant changes with technical details
3. Includes commit hash references in format [hash](https://git.kernel.org/torvalds/c/HASH)
4. Acknowledges contributors
5. Is 250-400 words
6. Uses markdown formatting with ## for the section title

Focus on impact and technical substance. Make it informative for kernel developers.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=[
                    {
                        "type": "text",
                        "text": "You are an expert technical writer specializing in Linux kernel development."
                    },
                    {
                        "type": "text",
                        "text": self._get_writing_guidelines(),
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            section = response.content[0].text
            return section.strip()

        except Exception as e:
            print(f"Error generating blog section for {subsystem}: {e}")
            return f"## {subsystem_name}\n\n*Error generating content*"

    def generate_blog_post(
        self,
        subsystems: List[str],
        date: str = None,
        date_range: str = None
    ) -> str:
        """
        Generate complete weekly blog post.

        Args:
            subsystems: List of subsystems to include
            date: Date of analysis data (YYYY-MM-DD)
            date_range: Human-readable date range for title

        Returns:
            Complete blog post in markdown
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if date_range is None:
            date_range = f"Week of {date}"

        print(f"\n{'='*60}")
        print(f"Generating Blog Post for {date_range}")
        print(f"Using Claude via Vertex AI")
        print(f"Project: {self.project_id}, Region: {self.region}")
        print(f"{'='*60}")

        # Generate header
        blog_post = f"""# Linux Kernel Weekly Update: {date_range}

*Automated weekly digest of Linux kernel subsystem development*

---

"""

        sections = []

        # Generate section for each subsystem
        for subsystem in subsystems:
            print(f"\nGenerating section for {subsystem.upper()}...")

            # Load analysis data
            analysis_file = Path("data/processed") / date / subsystem / "analysis.json"

            if not analysis_file.exists():
                print(f"  No analysis data found for {subsystem}, skipping")
                continue

            with open(analysis_file) as f:
                analysis = json.load(f)

            section = self.generate_subsystem_section(subsystem, analysis, date_range)

            if section:
                sections.append(section)
                print(f"  ✓ Generated {len(section)} characters")

        # Combine all sections
        blog_post += "\n\n".join(sections)

        # Add footer
        blog_post += f"""

---

## About This Report

This weekly summary is automatically generated by an AI agent system powered by Claude via Google Cloud Vertex AI, tracking kernel development across filesystems, networking, storage, and core kernel subsystems.

**Data Sources:**
- Linux Kernel Mailing Lists (lore.kernel.org)
- Kernel.org Git Repositories

**AI Infrastructure:**
- Google Cloud Vertex AI
- Claude {self.model}
- Multi-agent orchestration
- Prompt caching for efficiency

*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}*
"""

        return blog_post

    def save_blog_post(
        self,
        content: str,
        date: str = None,
        filename: str = None
    ):
        """Save blog post to file."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if filename is None:
            filename = f"weekly-{date}.md"

        output_dir = Path("data/drafts")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / filename
        with open(output_file, "w") as f:
            f.write(content)

        print(f"\n{'='*60}")
        print(f"Blog post saved to: {output_file}")
        print(f"{'='*60}")
        print(f"Length: {len(content)} characters")
        print(f"Words: ~{len(content.split())} words")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate blog posts from kernel analysis data using Vertex AI"
    )
    parser.add_argument(
        "--subsystems",
        nargs="+",
        required=True,
        help="Subsystems to include (e.g., xfs ext4 btrfs)"
    )
    parser.add_argument(
        "--date",
        help="Date of analysis data (YYYY-MM-DD), defaults to today"
    )
    parser.add_argument(
        "--date-range",
        help="Human-readable date range for title (e.g., 'April 29 - May 5, 2026')"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6@20250514",
        help="Claude model ID on Vertex AI"
    )
    parser.add_argument(
        "--project-id",
        help="GCP project ID (or set GOOGLE_CLOUD_PROJECT env var)"
    )
    parser.add_argument(
        "--region",
        default="us-east5",
        help="GCP region (default: us-east5)"
    )
    parser.add_argument(
        "--output",
        help="Output filename (default: weekly-YYYY-MM-DD.md)"
    )

    args = parser.parse_args()

    writer = KernelBlogWriterVertexAI(
        model=args.model,
        project_id=args.project_id,
        region=args.region
    )

    blog_post = writer.generate_blog_post(
        subsystems=args.subsystems,
        date=args.date,
        date_range=args.date_range
    )

    writer.save_blog_post(
        content=blog_post,
        date=args.date,
        filename=args.output
    )


if __name__ == "__main__":
    main()
