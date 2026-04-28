# Python Test Conventions

[Back to Local Instructions Index](index.md)

## One class per file

Each test class must live in its own file. Name the file after the class in snake_case, dropping the `Test` prefix:

| Test class | File |
| --- | --- |
| `TestFooBar` | `tests/test_foo_bar.py` |
| `TestIsExcluded` | `tests/test_is_excluded.py` |

This mirrors the dotnet and npm conventions used in this project.

## Pylint disable comments

Add only the `# pylint: disable=` codes actually needed by that file at the top. Common ones:

| Code | When needed |
| --- | --- |
| `missing-class-docstring` | All test files (test classes don't need docstrings) |
| `too-few-public-methods` | Files with a test class that has only one test method |
| `too-many-arguments,too-many-positional-arguments` | Files with helper functions that have many keyword params |
| `unused-argument` | Files where inner `handler(req)` functions don't use `req` |

## Shared helpers

Small, file-specific helpers (e.g. `_make_client`) may be duplicated across files. Extract to `conftest.py` only if the same fixture is used in more than three files.
