#!/usr/bin/env python3
"""
Install a skill to ~/.skill_repo and sync to detected platforms via symlinks.
Supports installing from local path or Git URL, and syncing globally or locally.
"""

import os
import sys
import shutil
import json
import argparse
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

# Import central configuration
import config


def get_skill_name_from_url(url: str) -> str:
    """Extract skill name from Git URL."""
    # Remove .git extension if present
    name = url.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def clone_git_repo(url: str, target_dir: Path) -> Path:
    """Clone a git repository to a target directory."""
    print(f"   ⬇️  Cloning from {url}...")
    try:
        # ensuring parent dir exists
        target_dir.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            ["git", "clone", url, str(target_dir)], check=True, capture_output=True
        )
        return target_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ Error cloning repository: {e.stderr.decode().strip()}")
        sys.exit(1)


def get_skill_name(skill_path: Path) -> str:
    """Extract skill name from path or SKILL.md."""
    # If it's a .skill file, use the filename
    if skill_path.suffix == ".skill":
        return skill_path.stem

    # If it's a directory, use the directory name
    if skill_path.is_dir():
        return skill_path.name

    raise ValueError(f"Invalid skill path: {skill_path}")


def unzip_skill_file(skill_file: Path, target_dir: Path) -> Path:
    """Unzip .skill file to target directory."""
    import zipfile

    skill_name = skill_file.stem
    extract_path = target_dir / skill_name

    with zipfile.ZipFile(skill_file, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    return extract_path


def get_platform_paths(is_local_install: bool) -> dict:
    """
    Get available platforms with appropriate paths.
    If is_local_install is True, returns paths relative to CWD.
    If False, returns global system paths.
    """
    if not is_local_install:
        return config.get_available_platforms()

    # improved local install scanning
    available = {}
    cwd = Path.cwd()

    for name, conf in config.SUPPORTED_PLATFORMS.items():
        local_rel_path = conf["local"]
        local_full_path = cwd / local_rel_path

        # We consider it available if the parent config dir exists (e.g. .claude exists for .claude/skills)
        # OR if it's just a standard structure we want to enforce.
        # For simplicity, let's mirror the global logic: check if parent exists.

        parent_dir = local_full_path.parent
        # Also check if parent itself exists, if local_rel_path is deep
        # e.g. .agent/skills -> check .agent exists

        if parent_dir.exists():
            available[conf["id"]] = {
                "name": name,
                "path": local_full_path,
                "is_local": True,
            }

    return available


def check_conflicts(skill_name: str, available_platforms: dict) -> dict:
    """Check if skill already exists in repo or platforms (as non-symlink)."""
    conflicts = {}

    # Check repo
    if (config.SKILL_REPO / skill_name).exists():
        conflicts["repo"] = config.SKILL_REPO / skill_name

    # Check available platforms for conflicts
    for p_id, info in available_platforms.items():
        target = info["path"] / skill_name
        if target.exists():
            # If it's a symlink pointing to our repo, it's not a conflict, it's just an update
            if (
                target.is_symlink()
                and target.resolve() == (config.SKILL_REPO / skill_name).resolve()
            ):
                continue
            conflicts[info["name"]] = target

    return conflicts


def ask_user_overwrite(conflicts: dict) -> bool:
    """Ask user whether to overwrite existing skills."""
    print("\n⚠️  Conflicts detected:")
    for platform, path in conflicts.items():
        is_symlink = path.is_symlink()
        link_target = f" → {path.resolve()}" if is_symlink else ""
        type_str = "symlink" if is_symlink else "directory/file"
        print(f"   - {platform}: {path} ({type_str}{link_target})")

    response = input("\nOverwrite existing installations? [y/N]: ").strip().lower()
    return response == "y"


def install_to_repo(
    source_path: Path, skill_name: str, force: bool = False, is_git: bool = False
) -> Path:
    """Install skill to Central Skill Repo."""
    target_path = config.SKILL_REPO / skill_name

    # Create repo directory if it doesn't exist
    config.SKILL_REPO.mkdir(parents=True, exist_ok=True)

    # Remove existing if force
    if target_path.exists() and force:
        if target_path.is_symlink():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)

    # Copy/Move skill to Repo
    if is_git:
        # If it was a git clone, we already have it in a temp dir or target dir
        # If source_path is the temp dir, move it
        # We need to make sure we're not moving to ourselves if something weird happened
        if source_path.resolve() != target_path.resolve():
            shutil.move(str(source_path), str(target_path))
        return target_path

    if source_path.is_file() and source_path.suffix == ".skill":
        # Unzip .skill file
        return unzip_skill_file(source_path, config.SKILL_REPO)
    else:
        # Copy directory
        # If source is same as target (re-installing from repo), skip copy
        if source_path.resolve() == target_path.resolve():
            return target_path

        shutil.copytree(source_path, target_path, dirs_exist_ok=force)
        return target_path


def create_symlink(source: Path, target: Path, force: bool = False):
    """Create symlink from target to source."""
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        if not force:
            print(f"   ⚠️  Skipping {target} (exists, use force to overwrite)")
            return

        if target.is_symlink():
            target.unlink()
        else:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

    target.symlink_to(source)


def ask_sync_targets(available_platforms: dict, is_local: bool) -> list[str]:
    """Ask user which platforms to sync to based on available ones."""
    if not available_platforms:
        if is_local:
            print("\n⚠️  No local project configuration found in current directory.")
            print("   (Expected folders like .claude, .chat, .agent, etc.)")
        else:
            print("\n⚠️  No supported platforms detected on this system.")
        return []

    mode_str = "Local Project" if is_local else "System Global"
    print(f"\n🔗 Detected {mode_str} targets. Select which to enable this skill:")

    p_ids = list(available_platforms.keys())
    for i, p_id in enumerate(p_ids, 1):
        info = available_platforms[p_id]
        print(f"   {i}. {info['name']} ({info['path']})")

    all_idx = len(p_ids) + 1
    print(f"   {all_idx}. All detected (default)")

    choice = input(f"\nEnter choice (e.g. '1,2' or '{all_idx}'): ").strip()

    if not choice:
        choice = str(all_idx)

    selected_ids = []

    # Handle 'all' cases
    if str(all_idx) in choice or "all" in choice.lower():
        return p_ids

    for i, p_id in enumerate(p_ids, 1):
        if str(i) in choice.split(","):
            selected_ids.append(p_id)

    return selected_ids


def sync_to_platforms(
    repo_skill_path: Path,
    skill_name: str,
    selected_ids: list[str],
    available_platforms: dict,
    force: bool = False,
):
    """Create symlinks in selected platforms."""
    print(f"\n📎 Creating symlinks from {repo_skill_path}...")

    if not selected_ids:
        print("   No platforms selected.")
        return

    for p_id in selected_ids:
        if p_id in available_platforms:
            info = available_platforms[p_id]
            target = info["path"] / skill_name
            create_symlink(repo_skill_path, target, force)
            print(f"   ✅ {info['name']}: {target}")


def update_sync_metadata(
    skill_name: str, selected_ids: list[str], available_platforms: dict
):
    """Update metadata file with sync information."""
    metadata = config.load_metadata()

    # We need to preserve global targets if we are installing local, and vice versa
    # Actually, simplistic approach: just append to the list of targets if not present.

    current_targets = set(metadata.get(skill_name, {}).get("targets", []))

    new_targets = []
    for p_id in selected_ids:
        if p_id in available_platforms:
            new_targets.append(str(available_platforms[p_id]["path"] / skill_name))

    # Merge
    current_targets.update(new_targets)

    # Filter out non-existent
    valid_targets = []
    for t in current_targets:
        if os.path.exists(t) or os.path.islink(t):
            valid_targets.append(t)

    metadata[skill_name] = {
        "source": str(config.SKILL_REPO / skill_name),
        "targets": valid_targets,
    }
    config.save_metadata(metadata)


def main():
    parser = argparse.ArgumentParser(
        description="Install a skill to skill_repo and sync to platforms."
    )
    parser.add_argument(
        "skill_path", help="Path to local skill, .skill file, or Git URL"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Install to current project's local config directories instead of global system directores",
    )

    args = parser.parse_args()

    source_input = args.skill_path
    is_git = False
    temp_dir = None
    source_path = None
    skill_name = None

    try:
        # Detect if Git URL
        if source_input.startswith("http") or source_input.startswith("git@"):
            is_git = True
            skill_name = get_skill_name_from_url(source_input)
            print(f"📦 Detected Git URL for skill: {skill_name}")

            # Determine strict source path (temp or direct to repo?)
            # To handle conflicts properly, let's clone to a temp dir first
            temp_dir = tempfile.mkdtemp()
            # The clone will create the subdir inside temp_dir
            source_path = clone_git_repo(source_input, Path(temp_dir) / skill_name)
        else:
            source_path = Path(source_input).resolve()
            if not source_path.exists():
                print(f"❌ Error: Path does not exist: {source_path}")
                sys.exit(1)
            skill_name = get_skill_name(source_path)
            print(f"📦 Installing skill: {skill_name}")
            print(f"   Source: {source_path}")

        # Determine target platforms (Global vs Local)
        available_platforms = get_platform_paths(args.local)

        # Check for conflicts
        conflicts = check_conflicts(skill_name, available_platforms)
        force = False

        # Filter out self-conflicts if reinstalling from repo
        if not is_git and source_path == config.SKILL_REPO / skill_name:
            conflicts.pop("repo", None)

        if conflicts:
            if not ask_user_overwrite(conflicts):
                print("\n❌ Installation cancelled.")
                sys.exit(0)
            force = True

        # Install to Central Repo
        print(f"\n📥 Installing to Central Repo (~/.skill_repo)...")
        repo_path = install_to_repo(source_path, skill_name, force, is_git)
        print(f"   ✅ Stored at: {repo_path}")

        # Ask user which platforms to sync
        sync_targets = ask_sync_targets(available_platforms, args.local)

        # Sync to platforms
        sync_to_platforms(
            repo_path, skill_name, sync_targets, available_platforms, force
        )

        # Update metadata
        update_sync_metadata(skill_name, sync_targets, available_platforms)

        print(f"\n✅ Skill '{skill_name}' setup complete!")

    finally:
        # Cleanup temp if used
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
