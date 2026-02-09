#!/usr/bin/env python3
import os
import json
from pathlib import Path

# Central Skill Repository
SKILL_REPO = Path.home() / ".skill_repo"
SYNC_METADATA = SKILL_REPO / ".skill_sync_metadata.json"

# Supported Platforms Configuration
# Format: { "Display Name": { "id": "internal_id", "global": Path, "local": "local_project_path" } }
SUPPORTED_PLATFORMS = {
    "Claude Code": {
        "id": "claude",
        "global": Path.home() / ".claude" / "skills",
        "local": ".claude/skills"
    },
    "GitHub Copilot": {
        "id": "copilot",
        "global": Path.home() / ".copilot" / "skills",
        "local": ".github/skills"
    },
    "Google Antigravity": {
        "id": "antigravity",
        "global": Path.home() / ".gemini" / "antigravity" / "skills",
        "local": ".agent/skills"
    },
    "Cursor": {
        "id": "cursor",
        "global": Path.home() / ".cursor" / "skills",
        "local": ".cursor/skills"
    },
    "OpenCode": {
        "id": "opencode",
        "global": Path.home() / ".config" / "opencode" / "skill",
        "local": ".opencode/skill"
    },
    "OpenAI Codex": {
        "id": "codex",
        "global": Path.home() / ".codex" / "skills",
        "local": ".codex/skills"
    },
    "Gemini CLI": {
        "id": "gemini",
        "global": Path.home() / ".gemini" / "skills",
        "local": ".gemini/skills"
    },
    "Windsurf": {
        "id": "windsurf",
        "global": Path.home() / ".codeium" / "windsurf" / "skills",
        "local": ".windsurf/skills"
    },
    "Qwen Code": {
        "id": "qwen",
        "global": Path.home() / ".qwen" / "skills",
        "local": ".qwen/skills"
    },
    "Qoder": {
        "id": "qoder",
        "global": Path.home() / ".qoder" / "skills",
        "local": ".qoder/skills"
    }
}

def get_available_platforms():
    """
    Scan the system to see which platforms are installed.
    A platform is considered 'available' if its global parent directory exists.
    """
    available = {}
    for name, config in SUPPORTED_PLATFORMS.items():
        # Check if the parent directory of the skills folder exists
        # e.g., for ~/.claude/skills, check if ~/.claude exists
        global_path = config["global"]
        if global_path.parent.exists():
            available[config["id"]] = {
                "name": name,
                "path": global_path,
                "local_path": config["local"]
            }
    return available

def load_metadata():
    """Load sync metadata from file."""
    if SYNC_METADATA.exists():
        with open(SYNC_METADATA, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_metadata(metadata):
    """Save sync metadata to file."""
    SKILL_REPO.mkdir(parents=True, exist_ok=True)
    with open(SYNC_METADATA, 'w') as f:
        json.dump(metadata, f, indent=2)
