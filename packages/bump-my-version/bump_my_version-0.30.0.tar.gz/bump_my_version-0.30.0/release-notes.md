[Compare the full difference.](https://github.com/callowayproject/bump-my-version/compare/0.29.0...0.30.0)

### Fixes

- Fixed normalized paths in is_subpath. [d1c180b](https://github.com/callowayproject/bump-my-version/commit/d1c180b55cf19a5d3d8212bb102318f6b24a5cab)
    
- Fix formatting in docs. [5fe387c](https://github.com/callowayproject/bump-my-version/commit/5fe387ccf3ea8ce1a4e7b3b9d06f6f4446790cda)
    
### New

- Add handling for git path addition with new test coverage. [8ad5c82](https://github.com/callowayproject/bump-my-version/commit/8ad5c82182ec510ecc426656a8be1a41f3ce28f5)
    
  Enhances the `Git` class by adding the `add_path` method, improving control over tracked files. Includes comprehensive test cases to validate subpath handling, handle command failures, and ensure robustness against invalid inputs. Also includes minor refactoring with updated exception handling and code comments.
- Added tests for `utils.is_subpath`. [4e993ed](https://github.com/callowayproject/bump-my-version/commit/4e993ed423e05a8550342bd1d8b8ca82d4c17cb3)
    
- Add support for 'moveable_tags' configuration option. [2a2f1e6](https://github.com/callowayproject/bump-my-version/commit/2a2f1e6abe4c0d3e34440eacacc4b51bdb49f2df)
    
  This update introduces a new 'moveable_tags' field in the configuration model, with appropriate defaults. Test fixture files have been updated to reflect this change. This allows better handling of tags that can be relocated during versioning operations.
- Add support for 'moveable_tags' configuration option. [dd1efa5](https://github.com/callowayproject/bump-my-version/commit/dd1efa5026db2843f9ec06bcbb691a38a878fdc4)
    
  This update introduces a new 'moveable_tags' field in the configuration model, with appropriate defaults. Test fixture files have been updated to reflect this change. This allows better handling of tags that can be relocated during versioning operations.
- Added additional logging verbosity configuration in setup_logging. [2b420b8](https://github.com/callowayproject/bump-my-version/commit/2b420b82201b7b5ad129f4a6f64e99e446f0e492)
    
  Updated the logging verbosity levels to include formatting options for different verbosity levels. Added a new level (3) with detailed output including file path and line number. Refactored setup_logging to properly handle verbosity and log format settings.
### Other

- Merge remote-tracking branch 'origin/moving-tags' into moving-tags. [a2b7bd1](https://github.com/callowayproject/bump-my-version/commit/a2b7bd152a684234091c5e03c5dd55f50042fcd8)
    
- [pre-commit.ci] pre-commit autoupdate. [d03b1da](https://github.com/callowayproject/bump-my-version/commit/d03b1da16140836ef2c4c0daad12a616fedff498)
    
  **updates:** - [github.com/astral-sh/ruff-pre-commit: v0.8.6 → v0.9.2](https://github.com/astral-sh/ruff-pre-commit/compare/v0.8.6...v0.9.2)

- [pre-commit.ci] pre-commit autoupdate. [584711b](https://github.com/callowayproject/bump-my-version/commit/584711b7317a03683e442fdd908a55ee70846cca)
    
  **updates:** - [github.com/astral-sh/ruff-pre-commit: v0.8.4 → v0.8.6](https://github.com/astral-sh/ruff-pre-commit/compare/v0.8.4...v0.8.6)

- [pre-commit.ci] pre-commit autoupdate. [c583694](https://github.com/callowayproject/bump-my-version/commit/c58369411fea04f1979b5dd590862317cdccab9f)
    
  **updates:** - [github.com/astral-sh/ruff-pre-commit: v0.8.3 → v0.8.4](https://github.com/astral-sh/ruff-pre-commit/compare/v0.8.3...v0.8.4)

- Bump softprops/action-gh-release from 1 to 2 in the github-actions group. [787c241](https://github.com/callowayproject/bump-my-version/commit/787c241236c1f4da2512868135aca75a81558cca)
    
  Bumps the github-actions group with 1 update: [softprops/action-gh-release](https://github.com/softprops/action-gh-release).


  Updates `softprops/action-gh-release` from 1 to 2
  - [Release notes](https://github.com/softprops/action-gh-release/releases)
  - [Changelog](https://github.com/softprops/action-gh-release/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/softprops/action-gh-release/compare/v1...v2)

  ---
  **updated-dependencies:** - dependency-name: softprops/action-gh-release
dependency-type: direct:production
update-type: version-update:semver-major
dependency-group: github-actions

  **signed-off-by:** dependabot[bot] <support@github.com>

### Updates

- Updated some tests. [4013d86](https://github.com/callowayproject/bump-my-version/commit/4013d863c3762fee1802b012689af62a0184d85a)
    
- Remove legacy SCM implementation and add new SCM tests. [ddbe21e](https://github.com/callowayproject/bump-my-version/commit/ddbe21e4a29963caa063e554b84592d4c7a8222f)
    
  Replaced the outdated `scm_old.py` with a focused and updated SCM implementation. Added extensive tests for the new `SCMInfo` behavior, path handling, and commit/tag logic, ensuring robust functionality for Git and Mercurial. Updated fixtures and test configurations accordingly.
- Rename `scm.py` to `scm_old.py` and add new utility functions. [dac965d](https://github.com/callowayproject/bump-my-version/commit/dac965d485802668fedc8c6e329bf10d04f7c795)
    
  Refactored SCM-related imports to use the renamed `scm_old.py` for better module organization. Introduced `is_subpath` utility to simplify path checks and added support for moveable tags in version control systems. These changes improve code structure and extend functionality for tagging.
