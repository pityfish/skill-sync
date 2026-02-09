#!/usr/bin/env python3
"""
List all skills in central repo and their sync status across all detected platforms.
"""

import json
from pathlib import Path

# Import central configuration
import config


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
            return "✅", f"Synced"
        else:
            return "🔗", f"Linked → {target}"
    else:
        return "📁", "Local directory (not synced)"


def discover_all_skills(available_platforms: dict) -> set[str]:
    """Discover all skills from repo and all available platforms."""
    skills = set()

    # From central repo
    if config.SKILL_REPO.exists():
        for item in config.SKILL_REPO.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                skills.add(item.name)

    # From all available platforms
    for p_id, info in available_platforms.items():
        platform_path = info["path"]
        if platform_path.exists():
            for item in platform_path.iterdir():
                if (item.is_dir() or item.is_symlink()) and not item.name.startswith(
                    "."
                ):
                    skills.add(item.name)

    return skills


def list_all_skills():
    """List all skills with their sync status across all platforms."""
    available_platforms = config.get_available_platforms()
    metadata = config.load_metadata()
    all_skills = discover_all_skills(available_platforms)

    if not all_skills:
        print("📭 No skills found.")
        print(f"\nCentral Repo: {config.SKILL_REPO}")
        return

    # Count stats
    in_repo = 0
    synced_count = 0

    print(f"📚 All Skills ({len(all_skills)} total)\n")
    print("=" * 80)

    for skill_name in sorted(all_skills):
        repo_path = config.SKILL_REPO / skill_name
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

        for p_id, info in available_platforms.items():
            skill_path = info["path"] / skill_name
            icon, desc = check_path_status(skill_path, expected_source)

            print(f"   {info['name']:18} {icon} {desc}")

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
    print(f"\n📍 Available Platform Paths:")
    print(f"   Central Repo:  {config.SKILL_REPO}")
    for p_id, info in available_platforms.items():
        print(f"   {info['name']:15}: {info['path']}")


def main():
    list_all_skills()


if __name__ == "__main__":
    main()
