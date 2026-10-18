## [1.3.3] - 2026-10-18

### 🚀 Features

- Add pre-commit (#23)
- Add check-dependencies support + pre-commit/ci integration (#27)
- Add auto-changelog generation (#30)

### 🚜 Refactor

- Restructure action tests (#28)

### ⚙️ Miscellaneous Tasks

- Bump version to 1.3.3

### 💼 Other

- Bump setuptools from 78.1.1 to 83.0.0 (#24)
- Bump pytest from 8.3.5 to 9.0.3 (#22)
- Add Ruff, devcontainers and pyproject.toml setup (#25)
- Migrate to uv (#26)
## [1.3.2] - 2026-03-04

### ⚙️ Miscellaneous Tasks

- Replace cronjob with separate canary action to force cache invalidation (#21)

### 💼 Other

- Release v1.3.2
## [1.3.1] - 2026-03-04

### ⚙️ Miscellaneous Tasks

- Add monthly conjob that runs ci (#20)

### 💼 Other

- Modularize integration test setup (#16)
- *(texlive)* Upgrade defaults and tests to texlive 2026 (#19)
- Release v1.3.1
## [1.3.0] - 2025-09-10

### 💼 Other

- Add action integration tests (#12)
- V1.3.0
## [1.2.1] - 2025-07-19

### 💼 Other

- Update README.md
- Change README.md to use JSONC Markdown dialect
- Bump setuptools from 76.0.0 to 78.1.1
- Merge pull request #9 from SSW-JKU/dependabot/pip/setuptools-78.1.1
- Replace no longer available texlive setup action (#11)
## [1.2.0] - 2025-05-19

### 💼 Other

- Fix build result when exercise directory does not exist and add integration test
- Merge pull request #8 from SSW-JKU/issue/7/fix_action_output
- Update changelog
## [1.1.1] - 2025-05-19

### 💼 Other

- Add status badge
- Add CHANGELOG
- Add matrix strategy + automatic release drafts
- Separate lint and test steps and add release job
- Merge pull request #3 from SSW-JKU/ci/release_action
- Add changed files as action output
- Merge pull request #4 from SSW-JKU/issue/2/add_action_outputs
- Release v1.1.0
- Fix CHANGELOG parsing
- Merge pull request #6 from SSW-JKU/issue/5/fix_ci_changelog_parsing
- Prepare v1.1.1
## [1.0.0] - 2025-04-05

### 💼 Other

- Initial commit
- Add Python scripts and initial config
- Fix working directory
- Add latexmk dependency
- Move main method to __main__ file, update dirhash, fix integration test build command
- Restructure action
- Try different paths/workdirs
- Fix paths
- Fix paths v2
- Fix requirements file name
- Try fix for setup-python path
- Update workdir for actual script execution
- Update action paths
- Fix typo
- Finalize documentation for v1
