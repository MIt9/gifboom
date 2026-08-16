# Contributing to gifboom

Thank you for your interest in contributing!

## Setup

```bash
git clone https://github.com/gifboom/gifboom
cd gifboom
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

We use `ruff` for linting and formatting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Adding a New Provider

1. Create `src/gifboom/providers/yourprovider.py`
2. Inherit from `BaseProvider` in `src/gifboom/providers/__init__.py`
3. Implement `search()` and `get_by_id()`
4. Register it in `src/gifboom/providers/registry.py`
5. Add settings key to `src/gifboom/config.py`
6. Add the MCP tool to `src/gifboom/mcp/__init__.py`
7. Document it in `skills/gifboom.md`

## Releasing

Tag a version to trigger PyPI publish:

```bash
git tag v0.2.0
git push origin v0.2.0
```
