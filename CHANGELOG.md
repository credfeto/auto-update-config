# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Please ADD ALL Changes to the UNRELASED SECTION and not a specific release
-->

## [Unreleased]
### Security
### Added
- Added .ai-instructions with reminder to wire new environment variables into workflow env blocks
- Refactored Python scripts to use dependency injection and added pytest test suite
- Split test classes into one-per-file and documented convention in ai/local/python-tests.instructions.md
- GitHubActionsTestLogger package to packages.json

### Fixed
- Pass ALWAYS_COLLABORATORS secret to workflow so collaborator invites are actually sent
- Improved logging for collaborator invite step
- Fixed obsolete pylint options in super-linter config that caused lint-code check to fail
- Copy .yamllint.yml to all managed repos to prevent yamllint using default settings and blocking commits via pre-commit hook
- Removed unnecessary flake8 F401 and F841 ignores that are no longer needed
- Removed unnecessary pylint suppressions that are no longer needed
- Fixed missing trailing newline in personal/repos.lst flagged by the pre-commit end-of-file-fixer baseline check

### Changed
### Deprecated
### Removed
- Removed unused branch protection enforcement code and its tests
### Deployment Changes
<!--
Releases that have at least been deployed to staging, BUT NOT necessarily released to live.  Changes should be moved from [Unreleased] into here as they are merged into the appropriate release branch
-->
## [0.0.0] - Project created