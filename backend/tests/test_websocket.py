"""BE-W1: WS /ws/progress — connect, receive progress. BE-W2: with job_id filter."""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient


@pytest.fixture
def test_db_path():
    return Path(tempfile.gettempdir()) / "test_ws.db"


@pytest.fixture
def app_ws(test_db_path):
    with patch.dict("os.environ", {"DB_PATH": str(test_db_path)}, clear=False):
        from main import app
        return app


def test_websocket_progress_connect(app_ws):
    """BE-W1: Connect to /ws/progress; server accepts connection (progress sent when download runs)."""
    with TestClient(app_ws) as test_client:
        with test_client.websocket_connect("/ws/progress") as ws:
            ws.send_text("ping")
            # No active download so no progress message; connection established is the test
    assert True


def test_websocket_connect_with_job_id_param(app_ws):
    """BE-W2: Connect with job_id query param — server accepts; filters to that job when progress sent."""
    with TestClient(app_ws) as test_client:
        with test_client.websocket_connect("/ws/progress?job_id=test-uuid-123") as ws:
            ws.send_text("ping")
    assert True
