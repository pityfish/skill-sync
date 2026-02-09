# Skill Sync

[English](./README.md) | [简体中文](./README_zh-CN.md)

**Skill Sync** 旨在帮助你从一个中央仓库管理并同步你的 AI 智能体技能（Skill）到多个平台（Claude, GitHub Copilot, Cursor, Gemini 等）。

## 安装

### 方法一：引导式安装（推荐）
你可以使用内置脚本将 `skill-sync` 本身作为一个技能安装到你的系统中。

```bash
# 1. 克隆仓库
git clone https://github.com/pityfish/skill-sync.git

# 2. 运行安装程序
python3 skill-sync/scripts/install_skill.py ./skill-sync
```

这将涉及：
- 在你的中央技能仓库 (`~/.skill_repo`) 中注册 `skill-sync`。
- 自动检测已安装的 AI 助手并创建符号链接。

### 方法二：手动安装
手动将此目录复制或链接到你的智能体技能目录中。

## 使用方法

安装此 Skill 后，您可以直接通过自然语言指示 AI 助手（如 Claude, Gemini, Antigravity）来管理您的技能库。

**安装技能**
> "从 https://github.com/user/awesome-skill.git 安装这个技能"
> "把 ./my-new-skill/ 目录下的技能安装起来"
> "只在当前项目安装这个技能" (对应 `--local` 模式)

**查看已安装技能**
> "列出我所有已同步的技能"
> "检查有哪些技能安装成功了"

**更新技能**
> "更新所有通过 Git 安装的技能"
> "检查技能更新"

**卸载技能**
> "卸载 'old-skill' 这个技能"
> "删除 'pdf-tools'"

## 技术实现
在后台，Agent 会调用 `scripts/` 目录下的 Python 脚本来完成操作：
- `install_skill.py`: 处理本地路径或 Git URL 的安装逻辑。
- `list_synced.py`: 展示各平台的同步状态。
- `update_skills.py`: 拉取 Git仓库的最新更新。
- `uninstall_skill.py`: 安全移除技能文件及软链接。

## 功能特性
- **中央化管理**：在 `~/.skill_repo/` 中保留一份技能副本。
- **多平台同步**：自动同步到 Claude, Copilot, Cursor, Gemini 等。
- **Git 支持**：直接从 Git URL 安装并支持自动更新。
- **局部安装**：支持项目级别的技能配置。
- **自动检测**：扫描你的系统以发现你已安装的工具。
- **冲突预防**：在覆盖前检查现有文件。

## 支持的环境

- **操作系统**: macOS, Linux (需要支持符号链接)
- **Python**: 3.9 或更高版本
- **支持的平台**:

| 平台 | 项目目录 (Local) | 系统目录 (Global) |
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
