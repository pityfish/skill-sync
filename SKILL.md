---
name: skill-sync
description: Cross-platform skill synchronization tool. Installs skills to central repo (~/.skill_repo/) and creates symlinks to Gemini, Claude Code, and Antigravity. Supports interactive platform selection, conflict detection, and sync status tracking.
---

# Skill Sync

Cross-platform skill synchronization tool that manages skills in a central repository and syncs to multiple AI platforms via symbolic links.

## Architecture

```
~/.skill_repo/                    ← Central Repository (source of truth)
    ├── my-skill/
    ├── another-skill/
    └── .skill_sync_metadata.json

~/.gemini/skills/                 ← Symlink → ~/.skill_repo/
~/.claude/skills/                 ← Symlink → ~/.skill_repo/
~/.gemini/antigravity/skills/     ← Symlink → ~/.skill_repo/
```

## Core Scripts

### 1. Install Skill (`install_skill.py`)

Install a skill to central repo and sync to selected platforms.

**Usage**:
```bash
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py <path-to-skill>
```

**Supported inputs**:
- Local skill directory: `./my-skill/`
- Packaged .skill file: `./my-skill.skill`
- Cloned GitHub repo: `/path/to/cloned-repo/`

**Workflow**:
1. Extract skill name from path or filename
2. Check for conflicts in repo and platforms
3. Ask user confirmation if conflicts exist
4. Install to `~/.skill_repo/` (central)
5. Ask user which platforms to enable (interactive selection)
6. Create symlinks to selected platforms
7. Update sync metadata

**Platform Selection Menu**:
```
🔗 Select platforms to enable this skill:
   1. Gemini (~/.gemini/skills)
   2. Claude Code (~/.claude/skills)
   3. Google Antigravity (~/.gemini/antigravity/skills)
   4. All (default)

Enter choice (e.g. '1,2' or '4'):
```

**Examples**:
```bash
# Install from directory
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ./pdf-editor/

# Install from .skill file
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ./pdf-editor.skill

# Install from cloned GitHub repo
git clone https://github.com/user/awesome-skill.git
python3 ~/.claude/skills/skill-sync/scripts/install_skill.py ./awesome-skill/
```

### 2. List All Skills (`list_synced.py`)

Display all skills in central repo and their sync status across all platforms.

**Usage**:
```bash
python3 ~/.claude/skills/skill-sync/scripts/list_synced.py
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

### 3. Uninstall Skill (`uninstall_skill.py`)

Remove a skill from selected locations with interactive selection.

**Usage**:
```bash
python3 ~/.claude/skills/skill-sync/scripts/uninstall_skill.py <skill-name>
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

**Format**:
```json
{
  "skill-name": {
    "source": "/Users/user/.skill_repo/skill-name",
    "targets": [
      "/Users/user/.gemini/skills/skill-name",
      "/Users/user/.claude/skills/skill-name",
      "/Users/user/.gemini/antigravity/skills/skill-name"
    ]
  }
}
```

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
