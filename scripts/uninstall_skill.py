#!/usr/bin/env python3
"""
Uninstall a skill from central repo and/or selected platforms.
"""

import sys
import json
import shutil
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
    'repo': SKILL_REPO,
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


def save_metadata(metadata):
    """Save sync metadata to file."""
    SYNC_METADATA.parent.mkdir(parents=True, exist_ok=True)
    with open(SYNC_METADATA, 'w') as f:
        json.dump(metadata, f, indent=2)


def remove_path(path: Path) -> bool:
    """Remove file or directory (including symlinks)."""
    if not path.exists() and not path.is_symlink():
        return False

    if path.is_symlink() or path.is_file():
        path.unlink()
        return True
    elif path.is_dir():
        shutil.rmtree(path)
        return True

    return False


def get_skill_locations(skill_name: str) -> dict:
    """Get all locations where skill exists."""
    locations = {}

    for name, base_path in PLATFORMS.items():
        path = base_path / skill_name
        if path.exists() or path.is_symlink():
            is_symlink = path.is_symlink()
            locations[name] = {
                'path': path,
                'is_symlink': is_symlink,
                'target': path.resolve() if is_symlink else None
            }

    return locations


def ask_uninstall_targets(locations: dict) -> list[str]:
    """Ask user which locations to uninstall from."""
    print("\n🗑️  Select locations to remove:")

    options = []
    idx = 1

    # Always show repo first if exists
    if 'repo' in locations:
        info = locations['repo']
        type_str = "symlink" if info['is_symlink'] else "directory"
        print(f"   {idx}. Central Repo (~/.skill_repo) [{type_str}]")
        options.append(('repo', idx))
        idx += 1

    # Then show platforms
    for name in ['gemini', 'claude', 'antigravity']:
        if name in locations:
            info = locations[name]
            type_str = "symlink" if info['is_symlink'] else "directory"
            display_name = {
                'gemini': 'Gemini (~/.gemini/skills)',
                'claude': 'Claude Code (~/.claude/skills)',
                'antigravity': 'Antigravity (~/.gemini/antigravity/skills)'
            }[name]
            print(f"   {idx}. {display_name} [{type_str}]")
            options.append((name, idx))
            idx += 1

    print(f"   {idx}. All locations")

    choice = input(f"\nEnter choice (e.g. '1,2' or '{idx}' for all): ").strip()

    if not choice:
        return []

    targets = []

    # Handle 'all' case
    if str(idx) in choice or 'all' in choice.lower():
        return [name for name, _ in options]

    # Parse individual choices
    for name, opt_idx in options:
        if str(opt_idx) in choice:
            targets.append(name)

    return targets


def uninstall_skill(skill_name: str, targets: list[str]):
    """Uninstall skill from specified locations."""
    metadata = load_metadata()

    print(f"\n🗑️  Removing '{skill_name}'...\n")

    removed_any = False

    for target in targets:
        path = PLATFORMS[target] / skill_name

        display_name = {
            'repo': 'Central Repo',
            'gemini': 'Gemini',
            'claude': 'Claude Code',
            'antigravity': 'Antigravity'
        }[target]

        if remove_path(path):
            print(f"   ✅ Removed from {display_name}: {path}")
            removed_any = True
        else:
            print(f"   ⚠️  Not found in {display_name}: {path}")

    # Update metadata
    if skill_name in metadata:
        # If repo is removed, delete entire entry
        if 'repo' in targets:
            del metadata[skill_name]
            print(f"\n   ✅ Removed from sync metadata")
        else:
            # Otherwise, just update targets list
            remaining_targets = []
            for t in metadata[skill_name].get('targets', []):
                t_path = Path(t)
                if t_path.exists():
                    remaining_targets.append(t)
            metadata[skill_name]['targets'] = remaining_targets
            print(f"\n   ✅ Updated sync metadata")

        save_metadata(metadata)

    if removed_any:
        print(f"\n✅ Uninstall complete!")
    else:
        print(f"\n⚠️  Nothing was removed.")


def main():
    if len(sys.argv) < 2:
        print("Usage: uninstall_skill.py <skill-name>")
        print("\nExample:")
        print("  uninstall_skill.py my-skill")
        sys.exit(1)

    skill_name = sys.argv[1]

    # Find where skill exists
    locations = get_skill_locations(skill_name)

    if not locations:
        print(f"❌ Skill '{skill_name}' not found in any location.")
        sys.exit(1)

    print(f"📦 Found skill '{skill_name}' in {len(locations)} location(s):")
    for name, info in locations.items():
        type_str = "symlink" if info['is_symlink'] else "directory"
        target_info = f" → {info['target']}" if info['is_symlink'] else ""
        print(f"   - {name}: {info['path']} [{type_str}{target_info}]")

    # Ask which to uninstall
    targets = ask_uninstall_targets(locations)

    if not targets:
        print("\n❌ No locations selected. Uninstall cancelled.")
        sys.exit(0)

    # Confirm
    print(f"\n⚠️  Will remove from: {', '.join(targets)}")
    response = input("Confirm? [y/N]: ").strip().lower()

    if response != 'y':
        print("❌ Uninstall cancelled.")
        sys.exit(0)

    uninstall_skill(skill_name, targets)


if __name__ == "__main__":
    main()
