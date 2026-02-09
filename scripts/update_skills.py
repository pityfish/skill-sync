#!/usr/bin/env python3
"""
Update all Git-based skills in the central repository.
Checks if directories are git repos and runs git pull.
Supports selective updates and interactive menu.
Includes parallel processing and detailed status.
"""

import os
import sys
import argparse
import subprocess
import concurrent.futures
from pathlib import Path

# Import central configuration
import config


def get_git_repo_status(repo_path: Path) -> str:
    """Check if a directory is a git repo."""
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        return "not_git"
    return "git"


def check_updates_available(repo_path: Path) -> tuple[bool, str]:
    """
    Check if updates are available for a repo.
    Returns (has_updates, detail_string)
    """
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
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..@{u}"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )

        behind_count = int(result.stdout.strip())

        if behind_count > 0:
            return True, f"⬇️  {behind_count} new commits"

        # Check if ahead
        result_ahead = subprocess.run(
            ["git", "rev-list", "--count", "@{u}..HEAD"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )
        ahead_count = int(result_ahead.stdout.strip())

        if ahead_count > 0:
            return False, f"⬆️  {ahead_count} commits ahead"

        return False, "✅ Up to date"

    except (subprocess.CalledProcessError, ValueError):
        # If no upstream, or not a repo
        return False, "❓ Git Error (No upstream?)"
    except subprocess.TimeoutExpired:
        return False, "⏱️  Timeout"


def update_git_repo(repo_path: Path) -> str:
    """Run git pull in the repo and return the status."""
    try:
        # Get HEAD before pull
        head_before = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        # Run git pull
        subprocess.run(
            ["git", "pull"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )

        # Get HEAD after pull
        head_after = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        if head_before == head_after:
            return "up_to_date"

        return "updated"

    except subprocess.CalledProcessError as e:
        return f"error: {e.stderr.strip() if e.stderr else str(e)}"


def get_all_git_skills():
    """Return a list of (skill_name, path) for all git-based skills."""
    skills = []
    if not config.SKILL_REPO.exists():
        return []

    for item in sorted(config.SKILL_REPO.iterdir()):
        if (
            item.is_dir()
            and not item.name.startswith(".")
            and get_git_repo_status(item) == "git"
        ):
            skills.append((item.name, item))
    return skills


def ask_skills_to_update(skills):
    """Interactive menu to select skills."""
    print("\n📦 Select skills to update:")

    updateable_skills = []
    other_skills = []

    print("   Checking for updates (parallel)...")

    # Run checks in parallel
    futures = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for name, path in skills:
            futures[name] = executor.submit(check_updates_available, path)

    for name, path in skills:
        has_update, status_msg = futures[name].result()
        if has_update:
            updateable_skills.append((name, path, status_msg))
        else:
            other_skills.append((name, path, status_msg))

    all_options = updateable_skills + other_skills

    if not all_options:
        print("   No git-based skills found.")
        return []

    # Display Menu
    print("\n   [Updateable]")
    if not updateable_skills:
        print("   (None)")

    for i, (name, path, msg) in enumerate(updateable_skills, 1):
        print(f"   {i}. {name:20} [{msg}]")

    print("\n   [Others]")
    offset = len(updateable_skills)
    for i, (name, path, msg) in enumerate(other_skills, 1):
        idx = offset + i
        print(f"   {idx}. {name:20} [{msg}]")

    print(f"\n   A. Update All (Default)")

    choice = input(f"\nEnter choice (e.g. '1,2' or 'A', default 'A'): ").strip()

    if not choice or choice.lower() == "a" or "all" in choice.lower():
        return [path for name, path, msg in all_options]

    selected_paths = []

    # Handle ranges and commas
    parts = choice.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                for i in range(start, end + 1):
                    if 1 <= i <= len(all_options):
                        name, path, msg = all_options[i - 1]
                        selected_paths.append(path)
            except ValueError:
                pass
        else:
            try:
                i = int(part)
                if 1 <= i <= len(all_options):
                    name, path, msg = all_options[i - 1]
                    selected_paths.append(path)
            except ValueError:
                pass

    return selected_paths


def main():
    parser = argparse.ArgumentParser(description="Update Git-based skills.")
    parser.add_argument("skills", nargs="*", help="Specific skill names to update")
    parser.add_argument(
        "--all", action="store_true", help="Update all skills without prompting"
    )
    args = parser.parse_args()

    skill_repo = config.SKILL_REPO
    if not skill_repo.exists():
        print(f"❌ Skill repository not found at {skill_repo}")
        return

    targets = []

    # 1. Update specific skills from args
    if args.skills:
        for name in args.skills:
            path = skill_repo / name
            if not path.exists():
                print(f"❌ Skill '{name}' not found.")
                continue
            if get_git_repo_status(path) != "git":
                print(f"⚠️  Skill '{name}' is not a proper git repository.")
                continue
            targets.append(path)

    # 2. Update all if --all flag
    elif args.all:
        targets = [path for name, path in get_all_git_skills()]

    # 3. Interactive mode if no args
    else:
        all_git_skills = get_all_git_skills()
        if not all_git_skills:
            print("📭 No git-based skills found to update.")
            return
        targets = ask_skills_to_update(all_git_skills)

    if not targets:
        print("No skills selected.")
        return

    print(f"\n🔄 Updating {len(targets)} skill(s)...\n")

    updated_count = 0

    for path in targets:
        skill_name = path.name
        result = update_git_repo(path)

        if result == "up_to_date":
            print(f"   ✅ {skill_name:25} [Up to date]")
        elif result == "updated":
            print(f"   ⬇️  {skill_name:25} [Updated successfully]")
            updated_count += 1
        else:
            print(f"   ❌ {skill_name:25} [Update failed: {result}]")

    print(f"\n✨ Update complete. {updated_count} skills updated.")


if __name__ == "__main__":
    main()
