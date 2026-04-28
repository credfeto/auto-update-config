# Python Conventions

[Back to Local Instructions Index](index.md)

## Language version

Always target the latest stable release of Python 3. Do not use compatibility shims or feature guards for older versions.

## Style

Write idiomatic Python: use comprehensions, generators, `enumerate`, `zip`, `any`/`all`, context managers, and dataclasses where they make intent clearer. Follow PEP 8 naming and layout conventions throughout.

## Standard library first

Prefer the Python standard library over third-party packages. Only reach for an external dependency when the standard library genuinely cannot do the job (e.g. `httpx` for async-capable HTTP, `python-graphql-client` for GraphQL). Do not write custom implementations of things the standard library already provides (e.g. use `pathlib` not string manipulation for paths, `json` not manual serialisation, `urllib.parse` not hand-rolled URL building).

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
