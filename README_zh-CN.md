# Skill Sync

[English](./README.md) | [简体中文](./README_zh-CN.md)

**Skill Sync** 帮助你在一个中心仓库中管理你的 AI Agent 技能，并将其同步到多个平台（Gemini, Claude Code, Google Antigravity）。

## 安装

### 方法 1: 引导安装 (推荐)
你可以使用包含的脚本将 `skill-sync` 本身作为一个技能安装到你的系统中。

```bash
# 1. 克隆仓库
git clone https://github.com/pityfish/skill-sync.git

# 2. 运行安装程序
python3 skill-sync/scripts/install_skill.py ./skill-sync
```

这将执行以下操作：
- 将 `skill-sync` 注册到你的中心技能仓库 (`~/.skill_repo`)。
- 为你活跃的 AI 助手（Gemini, Claude, Antigravity）创建软链接。

### 方法 2: 手动安装
手动复制或软链接此目录到你的 Agent 技能目录（例如 `~/.gemini/antigravity/skills/`）。

## 使用方法

安装完成后，你可以使用自然语言要求你的 AI 助手管理你的技能。

**示例：**
- "安装位于 `./pdf-tools/` 的技能"
- "将 `web-search` 技能同步到所有平台"
- "列出我所有已安装的技能"
- "卸载 `deprecated-skill`"

## 功能特性
- **集中管理**：在 `~/.skill_repo/` 中保留一份技能副本。
- **多平台同步**：自动同步到 Gemini, Claude 和 Antigravity。
- **冲突预防**：在覆盖前检查是否存在现有文件。

## 支持环境

- **操作系统**: macOS, Linux (需要支持软链接)
- **Python**: 3.9 或更高版本
- **支持的 Agent**:
    - Google Gemini (~/.gemini)
    - Claude Code (~/.claude)
    - Google Antigravity (~/.gemini/antigravity)
