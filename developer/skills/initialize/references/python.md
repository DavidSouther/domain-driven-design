# Python Project Reference

Toolchain: uv + ruff (format + lint) + pyright + PyPA layout

## Required Layout

```
<project>/
  pyproject.toml
  uv.lock             # commit to version-lock dependencies
  src/
    <package>/
      __init__.py
  tests/
    __init__.py
    features/
      test_<feature>.py   # feature/integration tests live here
    unit/
      test_<module>.py    # unit tests
  .python-version     # pin Python version
```

## Required Config Files

### `pyproject.toml` (minimum)

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "pyright", "ruff"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "RUF"]

[tool.pyright]
pythonVersion = "3.12"
strict = true
include = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### `.python-version`

```
3.12
```

## Validation Checklist

- [ ] `uv` is installed (`uv --version`)
- [ ] `pyproject.toml` exists with `[project]` section
- [ ] `src/<package>/__init__.py` exists
- [ ] `tests/` directory exists with `__init__.py`
- [ ] `tests/features/` directory exists
- [ ] `uv sync --dev` exits 0
- [ ] `uv run pyright` exits 0 with no errors
- [ ] `uv run ruff check src tests` exits 0
- [ ] `uv run pytest` exits 0

## Scaffolding (if validation fails)

```bash
# New project (from parent directory)
uv init --package <name>
cd <name>
mkdir -p src/<name> tests/features tests/unit
touch tests/__init__.py tests/features/__init__.py tests/unit/__init__.py

# Install dev dependencies
uv add --dev pytest pyright ruff

# Verify
uv run ruff check src tests
uv run pyright
uv run pytest
```

## Development Hooks

| Hook | Command |
|---|---|
| Format | `uv run ruff format <edited-file>` |
| Check | `uv run pyright && uv run ruff check src tests` |
| Test | `uv run pytest` |
| Lint | `uv run ruff check --fix src tests` |

## Feature Tests

Feature tests live in `tests/features/`. They test end-to-end flows without mocking the domain.

```python
# tests/features/test_user_login.py
import pytest
from my_project import App

def test_user_logs_in_and_sees_dashboard() -> None:
    app = App.for_testing()
    app.create_user(email="a@example.com", password="secret")

    response = app.post("/login", data={"email": "a@example.com", "password": "secret"})

    assert response.status_code == 302
    assert response.headers["location"] == "/dashboard"

    dashboard = app.get("/dashboard", cookies=response.cookies)
    assert "Welcome" in dashboard.text
```

## Verification Command

```bash
uv run pytest -v
```

Expected: all tests collected and passed, no warnings.
