# Skill Sync

[English](./README.md) | [简体中文](./README_zh-CN.md)

**Skill Sync** helps you manage and synchronize your AI agent skills across multiple platforms (Gemini, Claude Code, Google Antigravity) from a single central repository.

## Installation

### Method 1: Bootstrap Installation (Recommended)
You can use the included script to install `skill-sync` itself as a skill on your system.

```bash
# 1. Clone the repository
git clone https://github.com/pyan1024/skill-sync.git

# 2. Run the installer
python3 skill-sync/scripts/install_skill.py ./skill-sync
```

This will:
- Register `skill-sync` in your central skill repository (`~/.skill_repo`).
- Create symlinks for your active AI assistants (Gemini, Claude, Antigravity).

### Method 2: Manual Installation
Copy or symlink this directory to your agent's skill directory manually (e.g., `~/.gemini/antigravity/skills/`).

## Usage

Once installed, you can ask your AI assistant to manage your skills using natural language.

**Examples:**
- "Install the skill located at `./pdf-tools/`"
- "Sync the `web-search` skill to all platforms"
- "List all my installed skills"
- "Uninstall the `deprecated-skill`"

## Features
- **Central Management**: Keep one copy of your skills in `~/.skill_repo/`.
- **Multi-Platform Sync**: Automatically syncs to Gemini, Claude, and Antigravity.
- **Conflict Prevention**: Checks for existing files before overwriting.
