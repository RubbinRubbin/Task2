# Python Best Practices

## Code Structure and Organization

A well-organized Python project follows a clear directory structure. Use packages and modules to group related functionality. Each module should have a single, well-defined responsibility. Avoid circular imports by structuring dependencies in a directed acyclic graph.

Use `__init__.py` files to define public APIs for your packages. Keep them minimal — re-export only what consumers need.

## Error Handling

Catch specific exceptions rather than bare `except` clauses. Never silence errors without logging them. Use custom exception classes for domain-specific errors to make debugging easier.

```python
# Good
try:
    result = parse_config(path)
except FileNotFoundError:
    logger.error("Config file not found: %s", path)
    raise
except json.JSONDecodeError as e:
    logger.error("Invalid JSON in config: %s", e)
    raise ConfigError(f"Malformed config at {path}") from e

# Bad
try:
    result = parse_config(path)
except:
    pass
```

Use context managers (`with` statements) for resource management — files, database connections, locks. This ensures cleanup even when exceptions occur.

## Type Hints

Use type hints consistently across your codebase. They serve as documentation, enable IDE autocompletion, and allow static analysis tools like `mypy` to catch bugs before runtime.

```python
from typing import Optional

def find_user(user_id: int, include_inactive: bool = False) -> Optional[User]:
    """Find a user by ID, optionally including inactive accounts."""
    ...
```

For complex types, use `TypeAlias` or `TypeVar` to keep signatures readable. Prefer `collections.abc` types (`Sequence`, `Mapping`) over concrete types (`list`, `dict`) in function signatures for flexibility.

## Virtual Environments

Always use virtual environments to isolate project dependencies. This prevents version conflicts between projects and ensures reproducible builds.

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -e ".[dev]"
```

Pin your dependencies with exact versions in `requirements.txt` or use `pyproject.toml` with version constraints. Use tools like `pip-compile` or `poetry` for deterministic dependency resolution.

## Testing

Write tests at multiple levels: unit tests for individual functions, integration tests for component interactions, and end-to-end tests for critical paths. Aim for high coverage on business logic, but don't chase 100% coverage on boilerplate.

Use `pytest` as your test framework. It provides fixtures for setup/teardown, parametrize for data-driven tests, and a rich plugin ecosystem.

```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Alice", email="alice@example.com")

def test_user_full_name(sample_user):
    assert sample_user.full_name == "Alice"

@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("", False),
])
def test_email_validation(email, valid):
    assert validate_email(email) == valid
```

## Logging

Use the `logging` module instead of `print()` for production code. Configure logging at application startup, not in library code. Use structured logging for machine-parseable output in production environments.

Set appropriate log levels: DEBUG for development details, INFO for operational events, WARNING for unexpected but handled situations, ERROR for failures that need attention.
