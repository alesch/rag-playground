# Test Optimization Plan

## Goal
Separate slow integration tests (specifically Supabase) from the default test run to improve developer feedback loops.

## Changes

1.  **Registered Marker**: Added `slow` marker in `pytest.ini`.
2.  **Configuration**: Added `--run-slow` command line option in `tests/conftest.py`.
3.  **Skip Logic**: Implemented `pytest_collection_modifyitems` hook in `tests/conftest.py` to skip tests marked as `slow` unless `--run-slow` is provided.
4.  **Marked Tests**: Applied `pytestmark = pytest.mark.slow` to `tests/test_supabase_client.py`.

## Usage

- **Default Run**: `pytest` (skips slow tests)
- **Full Run**: `pytest --run-slow` (runs all tests)
