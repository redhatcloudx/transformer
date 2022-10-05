"""Configuration for tests."""
from __future__ import annotations


def pytest_configure(config: any) -> None:
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
