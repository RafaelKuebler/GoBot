from unittest.mock import patch

import pytest
from telegram.ext import ExtBot

from gobot.log_utils import setup_logging


@pytest.fixture(autouse=True)
def logs():
    setup_logging()


@pytest.fixture(autouse=True)
def patch_dynamodb_env(monkeypatch):
    monkeypatch.setenv("USE_LOCAL_DB", "true")
    monkeypatch.setenv("DYNAMODB_ENDPOINT", "http://localhost:8000")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "foo")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "bar")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")


@pytest.fixture
def mock_send_message():
    with patch.object(ExtBot, "send_message", autospec=True) as mock_send_message:
        yield mock_send_message


@pytest.fixture
def mock_send_photo():
    with patch.object(ExtBot, "send_photo", autospec=True) as mock_send_photo:
        yield mock_send_photo
