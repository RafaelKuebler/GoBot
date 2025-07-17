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
    # Split command and arguments
    if " " in command:
        cmd, _ = command.split(" ", 1)
    else:
        cmd = command
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
                    "entities": [{"type": "bot_command", "offset": 0, "length": len(cmd)}],
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


def test_start_prints_instructions(mock_send_message):
    """Calling /start prints welcome message and instructions"""
    # Arrange
    event = build_event("/start")

    # Act
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_message.assert_any_call(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text="Hi! 🤗 I am <b>Go Sensei</b> and will take care of your <b>Go</b> game!",
        parse_mode="HTML",
    )
    mock_send_message.assert_any_call(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text=(
            "These are my available commands:<br>"
            "  /start - to show this introductory message<br>"
            "  /new - start a new 9x9 game<br>"
            "  /join - join an already created game<br>"
            "  /place <i>coords</i> - play a stone of your color at given coordinates (e.g. <code>/place a1</code>)<br>"
            "  /pass - to skip your turn<br>"
            "  /show - show the current board state<br>"
            "  /proverb - display a proverb"
        ),
        parse_mode="HTML",
    )
    mock_send_message.assert_any_call(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text="To get started, simply send /new to this chat and have a friend join you with /join!",
        parse_mode="HTML",
    )


def initialize_game(mock_send_message, mock_send_photo):
    event = build_event("/new")
    main.lambda_handler(event, None)
    event = build_event("/join")
    main.lambda_handler(event, None)
    mock_send_photo.reset_mock()
    mock_send_message.reset_mock()


def test_proverb(mock_send_message):
    """Proverbs can always be sent"""
    # Arrange
    event = build_event("/proverb")

    # Act
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_message.assert_called_once_with(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text=ANY,
        parse_mode="HTML",
    )


def test_user_id_can_contain_special_characters(mock_send_message, mock_send_photo):
    """User IDs can contain markdown characters"""
    # Arrange
    initialize_game(mock_send_message, mock_send_photo)

    # Act
    event = build_event("/place b3")
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_photo.assert_called_once()
    mock_send_message.assert_called_once_with(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text=f"It is @{DEFAULT_USERNAME.replace("'", '')}'s (white) turn",
        parse_mode="HTML",
    )


def test_show_board_sends_photo(mock_send_message, mock_send_photo):
    """/show sends a photo of the board"""
    # Arrange: Start a new game and join
    initialize_game(mock_send_message, mock_send_photo)

    # Act: Call /show
    event = build_event("/show")
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_photo.assert_called_once()


def test_pass_turn(mock_send_message, mock_send_photo):
    """/pass notifies and switches turn"""
    # Arrange: Start a new game and join
    initialize_game(mock_send_message, mock_send_photo)

    # Act: Call /pass
    event = build_event("/pass")
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    # Should notify that player passed and show board/turn
    assert any("passed" in str(call) for call in mock_send_message.call_args_list)
    mock_send_photo.assert_called_once()


def test_new_game_with_board_size(mock_send_message):
    """/new with board size argument starts a game with that size"""
    # Arrange
    event = build_event("/new 13")

    # Act
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_message.assert_any_call(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text="<b>You created a new game!</b> Another player can join with the /join command.",
        parse_mode="HTML",
    )


def test_unknown_command(mock_send_message):
    """Unknown commands are handled gracefully"""
    # Arrange
    event = build_event("/foobar")

    # Act
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    mock_send_message.assert_any_call(
        ANY,
        chat_id=DEFAULT_CHAT_ID,
        text="This command is not known to me 🤔\nPlease call /start for a list of known commands!",
        parse_mode="HTML",
    )
