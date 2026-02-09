#!/usr/bin/env python3
"""
Uninstall a skill from central repo and/or selected platforms.
"""

import sys
import json
import shutil
from pathlib import Path

# Import central configuration
import config


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


def get_skill_locations(skill_name: str, available_platforms: dict) -> dict:
    """Get all locations where skill exists."""
    locations = {}

    # Check Central Repo
    repo_path = config.SKILL_REPO / skill_name
    if repo_path.exists() or repo_path.is_symlink():
        locations["repo"] = {
            "name": "Central Repo",
            "path": repo_path,
            "is_symlink": repo_path.is_symlink(),
            "target": repo_path.resolve() if repo_path.is_symlink() else None,
        }

    # Check all available platforms
    for p_id, info in available_platforms.items():
        path = info["path"] / skill_name
        if path.exists() or path.is_symlink():
            is_symlink = path.is_symlink()
            locations[p_id] = {
                "name": info["name"],
                "path": path,
                "is_symlink": is_symlink,
                "target": path.resolve() if is_symlink else None,
            }

    return locations


def ask_uninstall_targets(locations: dict) -> list[str]:
    """Ask user which locations to uninstall from."""
    print("\n🗑️  Select locations to remove:")

    p_ids = list(locations.keys())
    for i, p_id in enumerate(p_ids, 1):
        info = locations[p_id]
        type_str = "symlink" if info["is_symlink"] else "directory"
        print(f"   {i}. {info['name']} [{type_str}]")

    all_idx = len(p_ids) + 1
    print(f"   {all_idx}. All locations")

    choice = input(f"\nEnter choice (e.g. '1,2' or '{all_idx}' for all): ").strip()

    if not choice:
        return []

    selected_ids = []

    # Handle 'all' case
    if str(all_idx) in choice or "all" in choice.lower():
        return p_ids

    for i, p_id in enumerate(p_ids, 1):
        if str(i) in choice.split(","):
            selected_ids.append(p_id)

    return selected_ids


def uninstall_skill(skill_name: str, selected_ids: list[str], locations: dict):
    """Uninstall skill from specified locations."""
    metadata = config.load_metadata()

    print(f"\n🗑️  Removing '{skill_name}'...\n")

    removed_any = False

    for p_id in selected_ids:
        info = locations[p_id]
        path = info["path"]

        if remove_path(path):
            print(f"   ✅ Removed from {info['name']}: {path}")
            removed_any = True
        else:
            print(f"   ⚠️  Not found in {info['name']}: {path}")

    # Update metadata
    if skill_name in metadata:
        # If repo is removed, delete entire entry
        if "repo" in selected_ids:
            del metadata[skill_name]
            print(f"\n   ✅ Removed from sync metadata")
        else:
            # Otherwise, just update targets list by checking what's still there
            remaining_targets = []
            for t in metadata[skill_name].get("targets", []):
                t_path = Path(t)
                if t_path.exists() or t_path.is_symlink():
                    remaining_targets.append(t)
            metadata[skill_name]["targets"] = remaining_targets
            print(f"\n   ✅ Updated sync metadata")

        config.save_metadata(metadata)

    if removed_any:
        print(f"\n✅ Uninstall complete!")
    else:
        print(f"\n⚠️  Nothing was removed.")


def main():
    if len(sys.argv) < 2:
        print("Usage: uninstall_skill.py <skill-name>")
        sys.exit(1)

    skill_name = sys.argv[1]

    # Get available platforms (to check for skill existence)
    available_platforms = config.get_available_platforms()

    # Find where skill exists
    locations = get_skill_locations(skill_name, available_platforms)

    if not locations:
        print(f"❌ Skill '{skill_name}' not found in any location.")
        sys.exit(1)

    print(f"📦 Found skill '{skill_name}' in {len(locations)} location(s):")
    for p_id, info in locations.items():
        type_str = "symlink" if info["is_symlink"] else "directory"
        target_info = f" → {info['target']}" if info["is_symlink"] else ""
        print(f"   - {info['name']}: {info['path']} [{type_str}{target_info}]")

    # Ask which to uninstall
    selected_ids = ask_uninstall_targets(locations)

    if not selected_ids:
        print("\n❌ No locations selected. Uninstall cancelled.")
        sys.exit(0)

    # Confirm
    print(
        f"\n⚠️  Will remove from: {', '.join([locations[pid]['name'] for pid in selected_ids])}"
    )
    response = input("Confirm? [y/N]: ").strip().lower()

    if response != "y":
        print("❌ Uninstall cancelled.")
        sys.exit(0)

    uninstall_skill(skill_name, selected_ids, locations)


if __name__ == "__main__":
    main()
