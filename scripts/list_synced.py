#!/usr/bin/env python3
"""
List all skills in central repo and their sync status across all platforms.
"""

import json
from pathlib import Path


# Central Skill Repository
SKILL_REPO = Path.home() / ".skill_repo"

# Platform skill directories
GEMINI_SKILLS = Path.home() / ".gemini" / "skills"
CLAUDE_SKILLS = Path.home() / ".claude" / "skills"
ANTIGRAVITY_SKILLS = Path.home() / ".gemini" / "antigravity" / "skills"

# Metadata file
SYNC_METADATA = SKILL_REPO / ".skill_sync_metadata.json"

# Platform mapping
PLATFORMS = {
    'gemini': GEMINI_SKILLS,
    'claude': CLAUDE_SKILLS,
    'antigravity': ANTIGRAVITY_SKILLS
}


def load_metadata():
    """Load sync metadata from file."""
    if SYNC_METADATA.exists():
        with open(SYNC_METADATA, 'r') as f:
            return json.load(f)
    return {}


def check_path_status(path: Path, expected_source: Path = None) -> tuple[str, str]:
    """
    Check path status.
    Returns (status_icon, description).
    """
    if not path.exists() and not path.is_symlink():
        return "❌", "Not installed"

    if path.is_symlink():
        target = path.resolve()
        if not target.exists():
            return "⚠️ ", "Broken symlink"

        if expected_source and target == expected_source:
            return "✅", f"Synced → {target}"
        else:
            return "🔗", f"Linked → {target}"
    else:
        return "📁", "Local directory (not synced)"


def discover_all_skills() -> set[str]:
    """Discover all skills from repo and all platforms."""
    skills = set()

    # From central repo
    if SKILL_REPO.exists():
        for item in SKILL_REPO.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                skills.add(item.name)

    # From all platforms
    for platform_path in PLATFORMS.values():
        if platform_path.exists():
            for item in platform_path.iterdir():
                if (item.is_dir() or item.is_symlink()) and not item.name.startswith('.'):
                    skills.add(item.name)

    return skills


def list_all_skills():
    """List all skills with their sync status across all platforms."""
    metadata = load_metadata()
    all_skills = discover_all_skills()

    if not all_skills:
        print("📭 No skills found.")
        print(f"\nCentral Repo: {SKILL_REPO}")
        print(f"Metadata: {SYNC_METADATA}")
        return

    # Count stats
    in_repo = 0
    synced_count = 0

    print(f"📚 All Skills ({len(all_skills)} total)\n")
    print("=" * 80)

    for skill_name in sorted(all_skills):
        repo_path = SKILL_REPO / skill_name
        repo_exists = repo_path.exists()

        if repo_exists:
            in_repo += 1

        print(f"\n📦 {skill_name}")

        # Central Repo status
        if repo_exists:
            print(f"   Repo:         ✅ {repo_path}")
        else:
            print(f"   Repo:         ❌ Not in central repo")

        # Platform statuses
        expected_source = repo_path if repo_exists else None
        platforms_synced = 0

        for platform_name, platform_path in PLATFORMS.items():
            skill_path = platform_path / skill_name
            icon, desc = check_path_status(skill_path, expected_source)

            display_name = {
                'gemini': 'Gemini',
                'claude': 'Claude',
                'antigravity': 'Antigravity'
            }[platform_name]

            print(f"   {display_name:12} {icon} {desc}")

            if icon == "✅":
                platforms_synced += 1

        if platforms_synced > 0:
            synced_count += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"\n📊 Summary:")
    print(f"   Total skills:     {len(all_skills)}")
    print(f"   In central repo:  {in_repo}")
    print(f"   Synced to 1+ platforms: {synced_count}")

    # Show paths
    print(f"\n📍 Paths:")
    print(f"   Central Repo:  {SKILL_REPO}")
    print(f"   Gemini:        {GEMINI_SKILLS}")
    print(f"   Claude Code:   {CLAUDE_SKILLS}")
    print(f"   Antigravity:   {ANTIGRAVITY_SKILLS}")
    print(f"   Metadata:      {SYNC_METADATA}")


def main():
    list_all_skills()


if __name__ == "__main__":
    main()
