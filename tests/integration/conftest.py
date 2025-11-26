import os
from unittest.mock import patch

import pytest
from telegram.ext import ExtBot

from gobot.log_utils import setup_logging


def pytest_configure():
    """Set environment variables before any tests run"""
    # TODO: TOKEN is not overidden because the python-telegram-bot library
    # actually validates the provided token against the telegram API.
    # This means TOKEN has to be real and provided in the env var when running the tests.
    os.environ["USE_LOCAL_DB"] = "true"
    os.environ["DYNAMODB_ENDPOINT"] = "http://localhost:8000"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


@pytest.fixture(autouse=True)
def logs():
    setup_logging()


@pytest.fixture
def mock_send_message():
    with patch.object(ExtBot, "send_message", autospec=True) as mock_send_message:
        yield mock_send_message


@pytest.fixture
def mock_send_photo():
    with patch.object(ExtBot, "send_photo", autospec=True) as mock_send_photo:
        yield mock_send_photo
