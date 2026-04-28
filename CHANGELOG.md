# Changelog
All notable changes to this project will be documented in this file.

<!--
Please ADD ALL Changes to the UNRELASED SECTION and not a specific release
-->

## [Unreleased]
### Added

- Added .ai-instructions with reminder to wire new environment variables into workflow env blocks
- Refactored Python scripts to use dependency injection and added pytest test suite
- Split test classes into one-per-file and documented convention in ai/local/python-tests.instructions.md

### Fixed

- Pass ALWAYS_COLLABORATORS secret to workflow so collaborator invites are actually sent
- Improved logging for collaborator invite step
- Fixed obsolete pylint options in super-linter config that caused lint-code check to fail

### Changed
### Removed
### Deployment Changes

<!--
Releases that have at least been deployed to staging, BUT NOT necessarily released to live.  Changes should be moved from [Unreleased] into here as they are merged into the appropriate release branch
-->
## [0.0.0] - Project created
