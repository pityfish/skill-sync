#!/usr/bin/env python3
"""
List all skills in central repo and their sync status across all detected platforms.
Includes Git update status check (Parallelized).
"""

import json
import subprocess
import concurrent.futures
from pathlib import Path

# Import central configuration
import config


def check_git_remote_status(repo_path: Path) -> tuple[str, str]:
    """
    Check if a git repo has updates available.
    Returns: (status_code, status_message)
    status_code: 'up_to_date', 'update_available', 'diverged', 'error', 'not_git'
    """
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        return "not_git", ""

    try:
        # Fetch remote updates (quietly)
        subprocess.run(
            ["git", "fetch"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            timeout=10,
        )

        # Check raw commits behind using rev-list
        # HEAD..@{u} means commits in upstream but not in HEAD
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..@{u}"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )

        behind_count = int(result.stdout.strip())

        if behind_count > 0:
            return "update_available", f" ⬇️  {behind_count} commits behind"

        # Also check if we are ahead (unpushed changes)
        result_ahead = subprocess.run(
            ["git", "rev-list", "--count", "@{u}..HEAD"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )
        ahead_count = int(result_ahead.stdout.strip())

        if ahead_count > 0:
            return "up_to_date", f" ⬆️  {ahead_count} commits ahead"

        return "up_to_date", " ✅ Up to date"

    except subprocess.CalledProcessError:
        # Fallback or strict error
        # Maybe no upstream configured?
        return "error", " ❓ Git Error (No upstream?)"
    except subprocess.TimeoutExpired:
        return "error", " ⏱️  Timeout"
    except Exception:
        return "error", " ❓ Error"


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
    all_skills = sorted(list(discover_all_skills(available_platforms)))

    if not all_skills:
        print("📭 No skills found.")
        print(f"\nCentral Repo: {config.SKILL_REPO}")
        return

    # Prepare parallel git verification
    # We only check git status for folders in the repo
    git_check_futures = {}
    repo_skills = []

    print(f"📚 All Skills ({len(all_skills)} total)\n")
    print("=" * 80)

    # Start git checks in background
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for skill_name in all_skills:
            repo_path = config.SKILL_REPO / skill_name
            if repo_path.exists():
                git_check_futures[skill_name] = executor.submit(
                    check_git_remote_status, repo_path
                )

    # Count stats
    in_repo = 0
    synced_count = 0
    updates_available = 0

    for skill_name in all_skills:
        repo_path = config.SKILL_REPO / skill_name
        repo_exists = repo_path.exists()
        update_status_str = ""

        if repo_exists:
            in_repo += 1
            # Retrieve git status from future
            if skill_name in git_check_futures:
                status_code, status_msg = git_check_futures[skill_name].result()
                if status_code == "update_available":
                    updates_available += 1
                update_status_str = status_msg

        print(f"\n📦 {skill_name}{update_status_str}")

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
    if updates_available > 0:
        print(
            f"   Updates available: {updates_available} (Run 'python3 scripts/update_skills.py')"
        )

    # Show paths
    print(f"\n📍 Available Platform Paths:")
    print(f"   Central Repo:  {config.SKILL_REPO}")
    for p_id, info in available_platforms.items():
        print(f"   {info['name']:15}: {info['path']}")


def main():
    list_all_skills()


if __name__ == "__main__":
    main()
