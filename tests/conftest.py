"""Configuration for tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()

