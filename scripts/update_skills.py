#!/usr/bin/env python3
"""
Update all Git-based skills in the central repository.
Checks if directories are git repos and runs git pull.
"""

import os
import sys
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


def list_and_update_skills():
    """List all skills in repo and update git-based ones."""
    skill_repo = config.SKILL_REPO

    if not skill_repo.exists():
        print(f"❌ Skill repository not found at {skill_repo}")
        return

    print(f"🔄 Checking for updates in {skill_repo}...\n")

    skills_found = 0
    updated_count = 0
    error_count = 0
    up_to_date_count = 0
    skipped_count = 0

    # Iterate through all directories in skill_repo
    try:
        items = sorted(
            [
                x
                for x in skill_repo.iterdir()
                if x.is_dir() and not x.name.startswith(".")
            ]
        )
    except FileNotFoundError:
        print("❌ Skill repository directory accessed but not found.")
        return

    for item in items:
        skills_found += 1
        skill_name = item.name

        status = get_git_repo_status(item)

        if status == "not_git":
            print(f"   📁 {skill_name:25} [Skipped - Not a git repo]")
            skipped_count += 1
            continue

        # Try update
        result = update_git_repo(item)

        if result == "up_to_date":
            print(f"   ✅ {skill_name:25} [Up to date]")
            up_to_date_count += 1
        elif result == "updated":
            print(f"   ⬇️  {skill_name:25} [Updated successfully]")
            updated_count += 1
        else:
            # Error case
            print(f"   ❌ {skill_name:25} [Update failed]")
            # Print error detail purely
            print(f"      Server message: {result}")
            error_count += 1

    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   Total skills scanned: {skills_found}")
    print(f"   Updated:              {updated_count}")
    print(f"   Up to date:           {up_to_date_count}")
    print(f"   Errors:               {error_count}")
    print(f"   Skipped (non-git):    {skipped_count}")

    if updated_count > 0:
        print(
            "\n✨ Some skills were updated. Platform symlinks typically point to these"
        )
        print(
            "   directories, so no re-sync should be needed unless files were added/removed."
        )


def main():
    list_and_update_skills()


if __name__ == "__main__":
    main()
