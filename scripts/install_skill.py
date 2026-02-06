#!/usr/bin/env python3
"""
Install a skill to ~/.skill_repo and sync to Gemini, Claude Code, and Antigravity via symlinks.
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Optional


# Central Skill Repository
SKILL_REPO = Path.home() / ".skill_repo"

# Platform skill directories
GEMINI_SKILLS = Path.home() / ".gemini" / "skills"
CLAUDE_SKILLS = Path.home() / ".claude" / "skills"
ANTIGRAVITY_SKILLS = Path.home() / ".gemini" / "antigravity" / "skills"

# Metadata file to track synced skills
SYNC_METADATA = SKILL_REPO / ".skill_sync_metadata.json"


def load_metadata():
    """Load sync metadata from file."""
    if SYNC_METADATA.exists():
        with open(SYNC_METADATA, 'r') as f:
            return json.load(f)
    return {}


def save_metadata(metadata):
    """Save sync metadata to file."""
    SYNC_METADATA.parent.mkdir(parents=True, exist_ok=True)
    with open(SYNC_METADATA, 'w') as f:
        json.dump(metadata, f, indent=2)


def get_skill_name(skill_path: Path) -> str:
    """Extract skill name from path or SKILL.md."""
    # If it's a .skill file, use the filename
    if skill_path.suffix == '.skill':
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

    with zipfile.ZipFile(skill_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    return extract_path


def check_conflicts(skill_name: str) -> dict:
    """Check if skill already exists in repo or platforms (as non-symlink)."""
    conflicts = {}

    # Check repo
    if (SKILL_REPO / skill_name).exists():
        conflicts['repo'] = SKILL_REPO / skill_name

    # Check platforms for non-symlink conflicts or existing installations
    for name, path in [('gemini', GEMINI_SKILLS), ('claude', CLAUDE_SKILLS), ('antigravity', ANTIGRAVITY_SKILLS)]:
        target = path / skill_name
        if target.exists():
            # If it's a symlink pointing to our repo, it's not a conflict, it's just an update
            if target.is_symlink() and target.resolve() == (SKILL_REPO / skill_name).resolve():
                continue
            conflicts[name] = target

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
    return response == 'y'


def install_to_repo(source_path: Path, skill_name: str, force: bool = False) -> Path:
    """Install skill to Central Skill Repo."""
    target_path = SKILL_REPO / skill_name

    # Create repo directory if it doesn't exist
    SKILL_REPO.mkdir(parents=True, exist_ok=True)

    # Remove existing if force
    if target_path.exists() and force:
        if target_path.is_symlink():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)

    # Copy skill to Repo
    if source_path.is_file() and source_path.suffix == '.skill':
        # Unzip .skill file
        return unzip_skill_file(source_path, SKILL_REPO)
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


def ask_sync_targets() -> list[str]:
    """Ask user which platforms to sync to."""
    print("\n🔗 Select platforms to enable this skill:")
    print("   1. Gemini (~/.gemini/skills)")
    print("   2. Claude Code (~/.claude/skills)")
    print("   3. Google Antigravity (~/.gemini/antigravity/skills)")
    print("   4. All (default)")

    choice = input("\nEnter choice (e.g. '1,2' or '4'): ").strip()

    if not choice:
        choice = '4'

    targets = []

    # Handle 'all' cases
    if '4' in choice or 'all' in choice.lower():
        return ['gemini', 'claude', 'antigravity']

    if '1' in choice: targets.append('gemini')
    if '2' in choice: targets.append('claude')
    if '3' in choice: targets.append('antigravity')

    return targets


def sync_to_platforms(repo_skill_path: Path, skill_name: str, targets: list[str], force: bool = False):
    """Create symlinks in selected platforms."""
    print(f"\n📎 Creating symlinks from {repo_skill_path}...")

    if not targets:
        print("   No platforms selected.")
        return

    if 'gemini' in targets:
        target = GEMINI_SKILLS / skill_name
        create_symlink(repo_skill_path, target, force)
        print(f"   ✅ Gemini: {target}")

    if 'claude' in targets:
        target = CLAUDE_SKILLS / skill_name
        create_symlink(repo_skill_path, target, force)
        print(f"   ✅ Claude Code: {target}")

    if 'antigravity' in targets:
        target = ANTIGRAVITY_SKILLS / skill_name
        create_symlink(repo_skill_path, target, force)
        print(f"   ✅ Antigravity: {target}")


def update_sync_metadata(skill_name: str, synced_targets: list[str]):
    """Update metadata file with sync information."""
    metadata = load_metadata()

    target_paths = []
    if 'gemini' in synced_targets:
        target_paths.append(str(GEMINI_SKILLS / skill_name))
    if 'claude' in synced_targets:
        target_paths.append(str(CLAUDE_SKILLS / skill_name))
    if 'antigravity' in synced_targets:
        target_paths.append(str(ANTIGRAVITY_SKILLS / skill_name))

    metadata[skill_name] = {
        'source': str(SKILL_REPO / skill_name),
        'targets': target_paths
    }
    save_metadata(metadata)


def main():
    if len(sys.argv) < 2:
        print("Usage: install_skill.py <skill-path-or-file>")
        sys.exit(1)

    source_path = Path(sys.argv[1]).resolve()

    if not source_path.exists():
        print(f"❌ Error: Path does not exist: {source_path}")
        sys.exit(1)

    # Get skill name
    skill_name = get_skill_name(source_path)
    print(f"📦 Installing skill: {skill_name}")
    print(f"   Source: {source_path}")

    # Check for conflicts
    conflicts = check_conflicts(skill_name)
    force = False

    # Filter out self-conflicts if reinstalling from repo
    if source_path == SKILL_REPO / skill_name:
        conflicts.pop('repo', None)

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
    sync_targets = ask_sync_targets()

    # Sync to platforms
    sync_to_platforms(repo_path, skill_name, sync_targets, force)

    # Update metadata
    update_sync_metadata(skill_name, sync_targets)

    print(f"\n✅ Skill '{skill_name}' setup complete!")


if __name__ == "__main__":
    main()
