---
name: skill-sync
description: Cross-platform skill synchronization tool. Installs skills to central repo (~/.skill_repo/) and dynamically syncs to detected AI platforms (Claude, GitHub Copilot, Cursor, Gemini, etc.). Supports interactive platform selection, system scanning, conflict detection, and sync status tracking.
---

# Skill Sync

Cross-platform skill synchronization tool that manages skills in a central repository and syncs to multiple AI platforms via symbolic links. It automatically scans your system to detect which platforms you use.

## Architecture

```
~/.skill_repo/                    ← Central Repository (source of truth)
    ├── my-skill/
    ├── another-skill/
    └── .skill_sync_metadata.json

~/.claude/skills/                 ← Symlink → ~/.skill_repo/
~/.github/skills/                 ← Symlink → ~/.skill_repo/ (Copilot)
~/.cursor/skills/                 ← Symlink → ~/.skill_repo/
~/.gemini/antigravity/skills/     ← Symlink → ~/.skill_repo/ (Antigravity)
...and others
```

## Supported Platforms

The tool automatically detects if any of the following platforms are installed:
- Claude Code (`~/.claude/skills`)
- GitHub Copilot (`~/.copilot/skills`)
- Google Antigravity (`~/.gemini/antigravity/skills`)
- Cursor (`~/.cursor/skills`)
- OpenCode (`~/.config/opencode/skill`)
- OpenAI Codex (`~/.codex/skills`)
- Gemini CLI (`~/.gemini/skills`)
- Windsurf (`~/.codeium/windsurf/skills`)
- Qwen Code (`~/.qwen/skills`)
- Qoder (`~/.qoder/skills`)

## Core Scripts

### 1. Install Skill (`install_skill.py`)

Install a skill to central repo and sync to selected platforms.

**Usage**:
```bash
python3 scripts/install_skill.py <path-or-url> [--local]
```

**Supported inputs**:
- Local skill directory: `./my-skill/`
- Packaged .skill file: `./my-skill.skill`
- **Git Repository URL**: `https://github.com/user/my-skill.git`

**Flags**:
- `--local`: Install skill to the current project's local configuration (e.g., `./.claude/skills`) instead of the global system directory.

**Workflow**:
1. Extract skill name from path, filename, or Git URL
2. **Scan system** (or local project) for available AI platforms
3. Check for conflicts in repo and discovered platforms
4. Ask user confirmation if conflicts exist
5. Install to `~/.skill_repo/` (central). *Note: Git URLs are cloned here.*
6. Ask user which detected platforms to enable (interactive selection)
7. Create symlinks to selected platforms
8. Update sync metadata

**Platform Selection Menu (Dynamic)**:
```
🔗 Detected platforms. Select which to enable this skill:
   1. Claude Code (~/.claude/skills)
   2. Gemini CLI (~/.gemini/skills)
   3. All detected (default)

Enter choice (e.g. '1' or '3'):
```

# Install from cloned GitHub repo
git clone https://github.com/user/awesome-skill.git
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ./awesome-skill/
```

### 2. Update Skills (`update_skills.py`)

Update all Git-based skills in the central repository by running `git pull`.

**Usage**:
```bash
python3 scripts/update_skills.py [skill-name ...] [--all]
```

**Features**:
- **Parallel Check**: Rapidly checks git status for all skills concurrently.
- **Detailed Status**: Shows if updates are available and how many commits behind.
- **Selective Update**: Interactive menu to choose which skills to update (if no args provided).
- **Specific Update**: `python3 scripts/update_skills.py my-skill`
- **Update All**: `python3 scripts/update_skills.py --all`

### 3. List All Skills (`list_synced.py`)

Display all skills in central repo and their sync status across all detected platforms.

**Usage**:
```bash
python3 scripts/list_synced.py
```

**Status Icons**:
| Icon | Meaning |
|------|---------|
| ✅ | Synced (symlink points to central repo) |
| 🔗 | Linked (symlink points elsewhere) |
| 📁 | Local directory (not synced) |
| ❌ | Not installed |
| ⚠️ | Broken symlink |

**Example output**:
```
📚 All Skills (3 total)

================================================================================

📦 pdf-editor
   Repo:         ✅ ~/.skill_repo/pdf-editor
   Gemini       ✅ Synced → ~/.skill_repo/pdf-editor
   Claude       ✅ Synced → ~/.skill_repo/pdf-editor
   Antigravity  ❌ Not installed

📦 other-skill
   Repo:         ❌ Not in central repo
   Gemini       📁 Local directory (not synced)
   Claude       ❌ Not installed
   Antigravity  ❌ Not installed

================================================================================

📊 Summary:
   Total skills:     3
   In central repo:  2
   Synced to 1+ platforms: 2
```

### 4. Uninstall Skill (`uninstall_skill.py`)

Remove a skill from selected locations with interactive selection.

**Usage**:
```bash
python3 scripts/uninstall_skill.py <skill-name>
```

**Workflow**:
1. Detect all locations where skill exists
2. Display locations with type info (directory vs symlink)
3. Ask user which locations to remove (supports multi-select)
4. Confirm before deletion
5. Update sync metadata

**Uninstall Selection Menu**:
```
📦 Found skill 'my-skill' in 3 location(s):
   - repo: ~/.skill_repo/my-skill [directory]
   - gemini: ~/.gemini/skills/my-skill [symlink → ~/.skill_repo/my-skill]
   - claude: ~/.claude/skills/my-skill [symlink → ~/.skill_repo/my-skill]

🗑️  Select locations to remove:
   1. Central Repo (~/.skill_repo) [directory]
   2. Gemini (~/.gemini/skills) [symlink]
   3. Claude Code (~/.claude/skills) [symlink]
   4. All locations

Enter choice (e.g. '1,2' or '4' for all):
```

**Example**:
```bash
python3 ~/.claude/skills/skill-sync/scripts/uninstall_skill.py pdf-editor
```

## Metadata Tracking

Sync status stored in: `~/.skill_repo/.skill_sync_metadata.json`

## Integration with AI Workflows

### When AI generates a new skill

```bash
# AI creates skill at ./new-skill/
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ./new-skill/
```

### When cloning from GitHub

```bash
git clone https://github.com/user/awesome-skill.git
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ./awesome-skill/
```

### When installing from .skill file

```bash
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ~/Downloads/my-skill.skill
```

## Troubleshooting

**Check sync status**:
```bash
python3 ~/.claude/skills/skill-sync/scripts/list_synced.py
```

**Reinstall/resync a skill**:
```bash
# Re-run install from central repo to update symlinks
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ~/.skill_repo/my-skill
```

**Permissions**:
```bash
# Ensure scripts are executable
chmod +x ~/.claude/skills/skill-sync/scripts/*.py
```

**Missing directories**:
The scripts automatically create platform directories if they don't exist.
