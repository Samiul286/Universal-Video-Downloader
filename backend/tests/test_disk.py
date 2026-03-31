"""BE-U6: Disk space check — accept when free > estimated; reject when free < estimated."""
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.disk import has_enough_space


def test_has_enough_space_when_unknown_estimated(tmp_path):
    with patch("app.services.disk.get_free_bytes", return_value=100 * 1024 * 1024):
        assert has_enough_space(Path(tmp_path)) is True


def test_has_enough_space_accept_when_free_above_estimated(tmp_path):
    with patch("app.services.disk.get_free_bytes", return_value=200 * 1024 * 1024):
        assert has_enough_space(Path(tmp_path), estimated_bytes=50 * 1024 * 1024) is True


def test_has_enough_space_reject_when_free_below_estimated(tmp_path):
    with patch("app.services.disk.get_free_bytes", return_value=30 * 1024 * 1024):
        assert has_enough_space(Path(tmp_path), estimated_bytes=50 * 1024 * 1024) is False
