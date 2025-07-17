import json
import time
from unittest.mock import ANY, patch

import pytest
from telegram.ext import ExtBot

import main

DEFAULT_CHAT_ID = 123456
DEFAULT_USER_ID = 111111
DEFAULT_USERNAME = "'RafaelKdS'"


def build_event(
    command: str,
    chat_id: int | None = None,
    user_id: int | None = None,
    user_name: str | None = None,
):
    # for message format see https://core.telegram.org/bots/api#update
    return {
        "body": json.dumps(
            {
                "update_id": 1,
                "message": {
                    "message_id": 1,
                    "from": {
                        "id": user_id or DEFAULT_USER_ID,
                        "first_name": "...",
                        "is_bot": False,
                        "username": user_name or DEFAULT_USERNAME,
                    },
                    "chat": {"id": chat_id or DEFAULT_CHAT_ID, "type": "group"},
                    "date": time.time(),
                    "text": command,
                    "entities": [{"type": "bot_command", "offset": 0, "length": len(command.encode("utf-16"))}],
                },
            }
        )
    }


@pytest.fixture
def mock_send_message():
    with patch.object(ExtBot, "send_message", autospec=True) as mock_send_message:
        yield mock_send_message


@pytest.fixture
def mock_send_photo():
    with patch.object(ExtBot, "send_photo", autospec=True) as mock_send_photo:
        yield mock_send_photo


def test_proverb(mock_send_message):
    """Proverbs can always be sent, even if no game exists"""
    # arrange
    event = build_event("/proverb")

    # act
    response = main.lambda_handler(event, None)
    print(mock_send_message.call_args_list)

    # assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_message.assert_called_once_with(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text=ANY,
        parse_mode="HTML",
    )


def test_user_id_can_contain_markdown_characters(mock_send_message, mock_send_photo):
    """User IDs can contain markdown characters"""
    # arrange
    user_name = "user_name"
    escaped_user_name = "user\\_name"
    event = build_event("/new", user_name=user_name)
    response = main.lambda_handler(event, None)
    event = build_event("/join", user_name=user_name)
    response = main.lambda_handler(event, None)

    # act
    event = build_event("/show", user_name=user_name)
    response = main.lambda_handler(event, None)
    print(mock_send_message.call_args_list)

    # assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_photo.assert_called_once()
    mock_send_message.assert_called_with(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text=f"It is @{escaped_user_name}'s (black) turn",
        parse_mode="HTML",
    )
    mock_send_photo.assert_called()


def test_start_prints_instructions(mock_send_message, mock_send_photo):
    """User IDs can contain markdown characters"""
    # arrange
    user_name = "user_name"
    escaped_user_name = "user\\_name"
    event = build_event("/new", user_name=user_name)
    response = main.lambda_handler(event, None)
    event = build_event("/join", user_name=user_name)
    response = main.lambda_handler(event, None)

    # act
    event = build_event("/show", user_name=user_name)
    response = main.lambda_handler(event, None)
    print(mock_send_message.call_args_list)

    # assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_message.assert_called_with(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text=f"It is @{escaped_user_name}'s (black) turn",
        parse_mode="HTML",
    )
    mock_send_photo.assert_called()
