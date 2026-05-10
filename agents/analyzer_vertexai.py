#!/usr/bin/env python3
"""
Analysis Agent - Vertex AI Version
Analyzes collected kernel data using Claude via Vertex AI.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from anthropic import AnthropicVertex


class KernelDataAnalyzerVertexAI:
    """Analyzes kernel patches and commits using Claude via Vertex AI."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6@20250514",
        config_path: str = "config/subsystems.json",
        project_id: Optional[str] = None,
        region: str = "us-east5"
    ):
        """
        Initialize analyzer with Vertex AI.

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
        # Uses Application Default Credentials (ADC)
        self.client = AnthropicVertex(
            region=self.region,
            project_id=self.project_id
        )

        # Load subsystem configurations for context
        with open(config_path) as f:
            self.subsystems = json.load(f)

    def _get_subsystem_context(self, subsystem: str) -> str:
        """
        Get cached context about a subsystem.

        This will be used with prompt caching to avoid re-sending
        subsystem descriptions on every request.
        """
        config = self.subsystems.get(subsystem, {})

        context = f"""# {config.get('name', subsystem.upper())}

## Description
{config.get('description', 'Linux kernel subsystem')}

## Category
{config.get('category', 'N/A')}

## Key Maintainers
{', '.join(config.get('maintainers', []))}

## Common Keywords
{', '.join(config.get('keywords', []))}

## Priority
{config.get('priority', 'medium')}
"""
        return context

    def analyze_commit(
        self,
        commit: Dict,
        subsystem: str
    ) -> Dict:
        """
        Analyze a single git commit using Claude via Vertex AI.

        Args:
            commit: Commit metadata and content
            subsystem: Subsystem name for context

        Returns:
            Analysis results
        """
        subsystem_context = self._get_subsystem_context(subsystem)

        # Create analysis prompt
        analysis_prompt = f"""You are a Linux kernel expert analyzing changes to the {subsystem} subsystem.

Review the following commit and provide a structured analysis.

**Commit Information:**
- Hash: {commit.get('commit_hash', 'N/A')}
- Author: {commit.get('author_name', 'N/A')} <{commit.get('author_email', 'N/A')}>
- Date: {commit.get('date', 'N/A')}
- Subject: {commit.get('subject', 'N/A')}

**Commit Details:**
```
{commit.get('full_detail', 'No details available')[:8000]}
```

Analyze this commit and provide:

1. **Type**: bugfix | feature | refactoring | optimization | documentation | cleanup
2. **Significance**: critical | major | minor | trivial
3. **Impact**: user-facing | developer-facing | internal | performance
4. **Summary**: 2-3 sentence technical summary suitable for a blog post
5. **Technical Details**: Key technical changes (list format)
6. **Notable**: Any particularly interesting or significant aspects

Respond in JSON format:
{{
  "type": "...",
  "significance": "...",
  "impact": "...",
  "summary": "...",
  "technical_details": ["...", "..."],
  "notable": "..."
}}
"""

        try:
            # Use Claude API with prompt caching via Vertex AI
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=[
                    {
                        "type": "text",
                        "text": "You are an expert Linux kernel developer and technical writer.",
                    },
                    {
                        "type": "text",
                        "text": subsystem_context,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
            )

            # Extract JSON response
            response_text = response.content[0].text

            # Try to parse JSON from response
            # Claude might wrap it in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)

            # Add metadata
            analysis["commit_hash"] = commit.get("commit_hash")
            analysis["commit_subject"] = commit.get("subject")
            analysis["commit_author"] = commit.get("author_name")
            analysis["analyzed_at"] = datetime.now().isoformat()
            analysis["model_used"] = self.model
            analysis["vertex_ai"] = {
                "project_id": self.project_id,
                "region": self.region
            }

            # Add usage statistics
            if hasattr(response, 'usage'):
                analysis["token_usage"] = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cache_creation_input_tokens": getattr(
                        response.usage, 'cache_creation_input_tokens', 0
                    ),
                    "cache_read_input_tokens": getattr(
                        response.usage, 'cache_read_input_tokens', 0
                    )
                }

            return analysis

        except Exception as e:
            print(f"Error analyzing commit {commit.get('commit_hash')}: {e}")
            return {
                "error": str(e),
                "commit_hash": commit.get("commit_hash"),
                "analyzed_at": datetime.now().isoformat()
            }

    def analyze_subsystem(
        self,
        subsystem: str,
        date: str = None
    ) -> Dict:
        """
        Analyze all commits for a subsystem.

        Args:
            subsystem: Subsystem name
            date: Date string (YYYY-MM-DD), defaults to today

        Returns:
            Analysis results for all commits
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Load collected data
        data_dir = Path("data/raw") / date / subsystem
        commits_file = data_dir / "commits.json"

        if not commits_file.exists():
            print(f"No commit data found for {subsystem} on {date}")
            return {}

        with open(commits_file) as f:
            commits = json.load(f)

        print(f"\n{'='*60}")
        print(f"Analyzing {len(commits)} commits for {subsystem.upper()}")
        print(f"Using Claude via Vertex AI")
        print(f"Project: {self.project_id}, Region: {self.region}")
        print(f"{'='*60}")

        analyses = []
        total_tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}

        for i, commit in enumerate(commits, 1):
            print(f"\n[{i}/{len(commits)}] Analyzing: {commit.get('subject', 'N/A')[:60]}...")

            analysis = self.analyze_commit(commit, subsystem)
            analyses.append(analysis)

            # Aggregate token usage
            if "token_usage" in analysis:
                usage = analysis["token_usage"]
                total_tokens["input"] += usage.get("input_tokens", 0)
                total_tokens["output"] += usage.get("output_tokens", 0)
                total_tokens["cache_read"] += usage.get("cache_read_input_tokens", 0)
                total_tokens["cache_write"] += usage.get("cache_creation_input_tokens", 0)

            # Print summary
            if "type" in analysis:
                print(f"  Type: {analysis['type']} | Significance: {analysis['significance']}")

        # Calculate costs (Vertex AI pricing may differ from direct API)
        # Using approximate Sonnet 4.6 pricing
        cost_estimate = (
            (total_tokens["input"] / 1_000_000 * 3) +
            (total_tokens["output"] / 1_000_000 * 15) +
            (total_tokens["cache_write"] / 1_000_000 * 3.75) +
            (total_tokens["cache_read"] / 1_000_000 * 0.30)
        )

        summary = {
            "subsystem": subsystem,
            "analysis_date": datetime.now().isoformat(),
            "total_commits": len(commits),
            "analyses": analyses,
            "token_usage": total_tokens,
            "estimated_cost_usd": round(cost_estimate, 4),
            "vertex_ai": {
                "project_id": self.project_id,
                "region": self.region,
                "model": self.model
            }
        }

        print(f"\n{'='*60}")
        print(f"Analysis Summary for {subsystem.upper()}")
        print(f"{'='*60}")
        print(f"Total commits analyzed: {len(commits)}")
        print(f"Token usage:")
        print(f"  Input tokens: {total_tokens['input']:,}")
        print(f"  Output tokens: {total_tokens['output']:,}")
        print(f"  Cache read: {total_tokens['cache_read']:,}")
        print(f"  Cache write: {total_tokens['cache_write']:,}")
        print(f"Estimated cost: ${cost_estimate:.4f}")

        return summary

    def save_analysis(
        self,
        analysis: Dict,
        subsystem: str,
        date: str = None
    ):
        """Save analysis results."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        output_dir = Path("data/processed") / date / subsystem
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "analysis.json"
        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=2)

        print(f"\nSaved analysis to {output_file}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze kernel commits using Claude via Vertex AI"
    )
    parser.add_argument(
        "--subsystem",
        required=True,
        help="Subsystem to analyze (e.g., xfs, ext4)"
    )
    parser.add_argument(
        "--date",
        help="Date of data to analyze (YYYY-MM-DD), defaults to today"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6@20250514",
        help="Claude model ID on Vertex AI (default: claude-sonnet-4-6@20250514)"
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
        "--config",
        default="config/subsystems.json",
        help="Path to subsystems configuration"
    )

    args = parser.parse_args()

    analyzer = KernelDataAnalyzerVertexAI(
        model=args.model,
        config_path=args.config,
        project_id=args.project_id,
        region=args.region
    )

    analysis = analyzer.analyze_subsystem(args.subsystem, args.date)
    analyzer.save_analysis(analysis, args.subsystem, args.date)


if __name__ == "__main__":
    main()
