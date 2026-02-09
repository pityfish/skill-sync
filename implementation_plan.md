# Implementation Plan - Skill Sync Enchancements

This plan outlines the steps to implement three new features for `skill-sync`: Direct Git Install, Local Project Installation, and Skill Updates.

## User Requirements
1.  **Direct Install from Git URL**: Allow installing skills directly using a Git URL.
2.  **Local/Project-Level Install**: Support installing skills to the current project's local configuration directories (e.g., `./.claude/skills`).
3.  **Update Check (Feature 4)**: Provide a way to update installed skills (specifically Git-based ones).

## Proposed Changes

### 1. `scripts/install_skill.py`
-   **Add Argument Parsing**: Use `argparse` to handle `skill_path` (positional) and optional `--local` flag.
-   **Git Support**:
    -   Detect if `skill_path` is a URL.
    -   If URL, clone the repository to a temporary location or directly to `~/.skill_repo` (staging).
    -   Extract skill name from the URL.
-   **Local Installation Support**:
    -   If `--local` flag is set:
        -   Instead of using `config.SUPPORTED_PLATFORMS[id]['global']`, use `Current Working Directory` joined with `config.SUPPORTED_PLATFORMS[id]['local']`.
        -   Ensure local config directories exist (create if needed).
    -   If no flag (default): Use existing global behavior.

### 2. `scripts/update_skills.py` (New Script)
-   **Functionality**:
    -   Iterate through all directories in `~/.skill_repo`.
    -   Check if a directory is a Git repository.
    -   If yes, execute `git pull` to fetch updates.
    -   Report success/failure/no-updates for each skill.

### 3. `scripts/config.py`
-   Ensure `SUPPORTED_PLATFORMS` structure is robust enough for local path composition (it already seems to be).
-   Add helper to resolve local platform paths based on CWD.

### 4. Documentation
-   Update `README.md` and `README_zh-CN.md` with usage instructions for new features.
-   Update `SKILL.md`.

## Verification Plan

### Manual Verification
-   **Git Install**: Try installing a skill from a public GitHub URL (e.g., a dummy repo or the `skill-sync` repo itself as a test).
-   **Local Install**:
    -   Create a dummy project folder.
    -   Run `install_skill.py <skill> --local`.
    -   Verify symlinks are created in `./.claude/skills`, etc., inside the dummy project.
-   **Update**:
    -   Go to a skill in `.skill_repo`, reset it to an older commit (if possible) or just run the update script and check output.

## Task List
1.  [ ] Update `scripts/install_skill.py` to support Git URLs and `--local` flag.
2.  [ ] Create `scripts/update_skills.py`.
3.  [ ] Update `README.md` and `README_zh-CN.md`.
4.  [ ] Verify all features.
