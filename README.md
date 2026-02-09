# Skill Sync

[English](./README.md) | [简体中文](./README_zh-CN.md)

**Skill Sync** helps you manage and synchronize your AI agent skills across multiple platforms (Claude, GitHub Copilot, Cursor, Gemini, etc.) from a single central repository.

## Installation

### Method 1: Bootstrap Installation (Recommended)
You can use the included script to install `skill-sync` itself as a skill on your system.

```bash
# 1. Clone the repository
git clone https://github.com/pityfish/skill-sync.git

# 2. Run the installer
python3 skill-sync/scripts/install_skill.py ./skill-sync
```

This will:
- Register `skill-sync` in your central skill repository (`~/.skill_repo`).
- Auto-detect installed AI assistants and create symlinks.

### Method 2: Manual Installation
Copy or symlink this directory to your agent's skill directory manually.

## Usage

Once this skill is installed, you can ask your AI assistant (e.g., Claude, Gemini) to manage your skills using natural language.

**Install a Skill**
> "Install the skill from https://github.com/user/awesome-skill.git"
> "Install the local skill at ./my-new-skill/"
> "Install this skill to the current project only" (uses `--local`)

**List Skills**
> "List all my synced skills"
> "Check which skills are installed"

**Update Skills**
> "Update all my Git-based skills"
> "Check for skill updates"

**Uninstall a Skill**
> "Uninstall the 'old-skill'"
> "Remove the 'pdf-tools' skill"

## Implementation Details
Under the hood, the agent will execute the python scripts located in `scripts/`:
- `install_skill.py`: Handles installation from local paths or Git URLs.
- `list_synced.py`: Shows sync status across platforms.
- `update_skills.py`: Pulls updates for Git-based skills.
- `uninstall_skill.py`: Removes skills and symlinks.

## Features
- **Central Management**: Keep one copy of your skills in `~/.skill_repo/`.
- **Multi-Platform Sync**: Automatically syncs to Claude, Copilot, Cursor, Gemini, etc.
- **Git Support**: Install directly from Git URLs and auto-update.
- **Local Install**: Support project-level skill configuration.
- **Auto-Detection**: Scans your system to find which tools you have installed.
- **Conflict Prevention**: Checks for existing files before overwriting.

## Supported Environments

- **OS**: macOS, Linux (requires symbolic link support)
- **Python**: 3.9 or higher
- **Supported Platforms**:

| Platform | Project Path (Local) | System Path (Global) |
| :--- | :--- | :--- |
| **Claude Code** | `.claude/skills` | `~/.claude/skills` |
| **GitHub Copilot** | `.github/skills` | `~/.copilot/skills` |
| **Google Antigravity** | `.agent/skills` | `~/.gemini/antigravity/skills` |
| **Cursor** | `.cursor/skills` | `~/.cursor/skills` |
| **OpenCode** | `.opencode/skill` | `~/.config/opencode/skill` |
| **OpenAI Codex** | `.codex/skills` | `~/.codex/skills` |
| **Gemini CLI** | `.gemini/skills` | `~/.gemini/skills` |
| **Windsurf** | `.windsurf/skills` | `~/.codeium/windsurf/skills` |
| **Qwen Code** | `.qwen/skills` | `~/.qwen/skills` |
| **Qoder** | `.qoder/skills` | `~/.qoder/skills` |
