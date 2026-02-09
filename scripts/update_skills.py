#!/usr/bin/env python3
"""
Update all Git-based skills in the central repository.
Checks if directories are git repos and runs git pull.
Supports selective updates and interactive menu.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Import central configuration
import config


def get_git_repo_status(repo_path: Path) -> str:
    """Check if a directory is a git repo."""
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        return "not_git"
    return "git"


def check_updates_available(repo_path: Path) -> bool:
    """Check if updates are available for a repo."""
    try:
        subprocess.run(
            ["git", "fetch"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            timeout=10,
        )
        status = subprocess.run(
            ["git", "status", "-uno"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )
        return "Your branch is behind" in status.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def update_git_repo(repo_path: Path) -> str:
    """Run git pull in the repo and return the status."""
    try:
        # Run git pull
        result = subprocess.run(
            ["git", "pull"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )

        output = result.stdout.strip()

        if "Already up to date" in output or "Already up-to-date" in output:
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

    # Check updates first to be helpful
    updateable_skills = []
    other_skills = []

    print("   Checking for updates...")
    for name, path in skills:
        if check_updates_available(path):
            updateable_skills.append((name, path))
        else:
            other_skills.append((name, path))

    all_options = updateable_skills + other_skills

    if not all_options:
        print("   No git-based skills found.")
        return []

    for i, (name, path) in enumerate(all_options, 1):
        status = " (Update Available)" if i <= len(updateable_skills) else ""
        print(f"   {i}. {name}{status}")

    all_idx = len(all_options) + 1
    print(f"   {all_idx}. All skills")

    choice = input(f"\nEnter choice (e.g. '1,2' or '{all_idx}'): ").strip()

    if not choice:
        return []

    if str(all_idx) in choice or "all" in choice.lower():
        return [path for name, path in all_options]

    selected_paths = []
    for i, (name, path) in enumerate(all_options, 1):
        if str(i) in choice.split(","):
            selected_paths.append(path)

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
