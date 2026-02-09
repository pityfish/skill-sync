#!/usr/bin/env python3
"""
Install a skill to ~/.skill_repo and sync to detected platforms via symlinks.
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Optional

# Import central configuration
import config


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


def install_to_repo(source_path: Path, skill_name: str, force: bool = False) -> Path:
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

    # Copy skill to Repo
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


def ask_sync_targets(available_platforms: dict) -> list[str]:
    """Ask user which platforms to sync to based on available ones."""
    if not available_platforms:
        print("\n⚠️  No supported platforms detected on this system.")
        return []

    print("\n🔗 Detected platforms. Select which to enable this skill:")

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

    target_paths = []
    for p_id in selected_ids:
        if p_id in available_platforms:
            target_paths.append(str(available_platforms[p_id]["path"] / skill_name))

    metadata[skill_name] = {
        "source": str(config.SKILL_REPO / skill_name),
        "targets": target_paths,
    }
    config.save_metadata(metadata)


def main():
    if len(sys.argv) < 2:
        print("Usage: install_skill.py <skill-path-or-file>")
        sys.exit(1)

    source_path = Path(sys.argv[1]).resolve()

    if not source_path.exists():
        print(f"❌ Error: Path does not exist: {source_path}")
        sys.exit(1)

    # Scan available platforms
    available_platforms = config.get_available_platforms()

    # Get skill name
    skill_name = get_skill_name(source_path)
    print(f"📦 Installing skill: {skill_name}")
    print(f"   Source: {source_path}")

    # Check for conflicts
    conflicts = check_conflicts(skill_name, available_platforms)
    force = False

    # Filter out self-conflicts if reinstalling from repo
    if source_path == config.SKILL_REPO / skill_name:
        conflicts.pop("repo", None)

    if conflicts:
        if not ask_user_overwrite(conflicts):
            print("\n❌ Installation cancelled.")
            sys.exit(0)
        force = True

    # Install to Central Repo
    print(f"\n📥 Installing to Central Repo (~/.skill_repo)...")
    repo_path = install_to_repo(source_path, skill_name, force)
    print(f"   ✅ Stored at: {repo_path}")

    # Ask user which platforms to sync
    sync_targets = ask_sync_targets(available_platforms)

    # Sync to platforms
    sync_to_platforms(repo_path, skill_name, sync_targets, available_platforms, force)

    # Update metadata
    update_sync_metadata(skill_name, sync_targets, available_platforms)

    print(f"\n✅ Skill '{skill_name}' setup complete!")


if __name__ == "__main__":
    main()
