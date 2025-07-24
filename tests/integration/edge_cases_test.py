import json
import time
from unittest.mock import patch

import pytest
from telegram.ext import ExtBot

import main

DEFAULT_CHAT_ID = 123456
FIRST_USER_ID = 111111
FIRST_USERNAME = "'Alice'"
SECOND_USER_ID = 222222
SECOND_USERNAME = "'Bob'"


def build_event(
    command: str,
    chat_id: int | None = None,
    user_id: int | None = None,
    user_name: str | None = None,
):
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
                        "id": user_id or FIRST_USER_ID,
                        "first_name": "...",
                        "is_bot": False,
                        "username": user_name or FIRST_USERNAME,
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


def initialize_game(mock_send_message, mock_send_photo):
    event = build_event("/new")
    main.lambda_handler(event, None)
    event = build_event("/join", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME)
    main.lambda_handler(event, None)
    mock_send_photo.reset_mock()
    mock_send_message.reset_mock()


def test_uppercase_coordinates(mock_send_message, mock_send_photo):
    """Uppercase coordinates should be accepted as valid"""
    # Arrange: Both players join, joiner moves first
    initialize_game(mock_send_message, mock_send_photo)
    event = build_event("/place A1", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME)

    # Act
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    assert mock_send_photo.call_count == 1
    assert any("turn" in str(call) for call in mock_send_message.call_args_list)


def test_occupied_coordinate(mock_send_message, mock_send_photo):
    """Placing a stone on an occupied coordinate returns the expected error message"""
    # Arrange: Both players join, joiner moves first, then creator tries same spot
    initialize_game(mock_send_message, mock_send_photo)
    event1 = build_event("/place b2", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME)
    event2 = build_event("/place b2", user_id=FIRST_USER_ID, user_name=FIRST_USERNAME)

    # Act
    main.lambda_handler(event1, None)
    response = main.lambda_handler(event2, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    found = any("already holds a stone" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    if not found:
        print("All send_message calls:")
        for call in mock_send_message.call_args_list:
            print(call.kwargs.get("text", ""))
    assert found, "Expected occupied coordinate error message not found in send_message calls"


@pytest.mark.parametrize("coord", ["z9", "a0", "foo", "a30", "1a"])
def test_invalid_coordinate(mock_send_message, mock_send_photo, coord):
    """Invalid coordinates return the expected error message"""
    # Arrange: Both players join, second player makes invalid moves
    initialize_game(mock_send_message, mock_send_photo)
    event = build_event(f"/place {coord}", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME)

    # Act
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    found = any("does not exist on the board" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    if not found:
        print("All send_message calls:")
        for call in mock_send_message.call_args_list:
            print(call.kwargs.get("text", ""))
    assert found, "Expected 'invalid coordinate error' message not found in send_message calls"


def test_self_capture(mock_send_message, mock_send_photo):
    """Self-capture is not allowed and returns the expected error message.

    Playing '!' is not allowed for white:
      A B C
    1 ! B .
    2 B B .
    3 . . .
    """
    # Arrange: creator fills a2, b1, b2, joiner pass and finally playplays a1
    initialize_game(mock_send_message, mock_send_photo)
    commands = [
        "/place a2",
        "/place b1",
        "/place b2",
    ]
    for command in commands:
        main.lambda_handler(build_event("/pass", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME), None)
        main.lambda_handler(build_event(command, user_id=FIRST_USER_ID, user_name=FIRST_USERNAME), None)
    event = build_event("/place a1", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME)

    # Act
    response = main.lambda_handler(build_event("/show"), None)
    response = main.lambda_handler(event, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    found = any("self-capture" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    if not found:
        print("All send_message calls:")
        for call in mock_send_message.call_args_list:
            print(call.kwargs.get("text", ""))
    assert found, "Expected self-capture error message not found in send_message calls"


def test_ko_rule(mock_send_message, mock_send_photo):
    """Ko rule violation returns the expected error message

    Playing White can capture at !:
      A B C D
    1 . B W .
    2 B ! B W
    3 . B W .

    But Ko rule prevents Black from capturing back at !:
      A B C D
    1 . B W .
    2 B W ! W
    3 . B W .
    """
    # Arrange
    initialize_game(mock_send_message, mock_send_photo)
    moves_black = [
        "/place b1",
        "/place b3",
        "/place a2",
    ]
    moves_white = [
        "/place c1",
        "/place c3",
        "/place d2",
    ]
    for black_move, white_move in zip(moves_black, moves_white):
        main.lambda_handler(build_event(black_move, user_id=SECOND_USER_ID, user_name=SECOND_USERNAME), None)
        main.lambda_handler(build_event(white_move, user_id=FIRST_USER_ID, user_name=FIRST_USERNAME), None)
    # finish setting up ko position
    main.lambda_handler(build_event("/place c2", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME), None)

    # Act
    # white captures first
    main.lambda_handler(build_event("/place b2", user_id=FIRST_USER_ID, user_name=FIRST_USERNAME), None)
    # black attempts to re-capture
    response = main.lambda_handler(build_event("/place c2", user_id=SECOND_USER_ID, user_name=SECOND_USERNAME), None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    found_ko = any("Ko rule" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    if not found_ko:
        print("All send_message calls:")
        for call in mock_send_message.call_args_list:
            print(call.kwargs.get("text", ""))
    assert found_ko, "Expected Ko rule error message not found in send_message calls"
    found_ko_proverb = any("Ko don't Play Go" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    assert found_ko_proverb, "Expected Ko proverb message not found in send_message calls"


def test_move_out_of_turn(mock_send_message, mock_send_photo):
    """Moving out of turn returns the expected error message"""
    # Arrange
    initialize_game(mock_send_message, mock_send_photo)

    # Act
    response = main.lambda_handler(build_event("/place a1", user_id=FIRST_USER_ID, user_name=FIRST_USERNAME), None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    found = any("not your turn" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    if not found:
        print("All send_message calls:")
        for call in mock_send_message.call_args_list:
            print(call.kwargs.get("text", ""))
    assert found, "Expected 'It is not your turn!' error message not found in send_message calls"


def test_not_enough_players(mock_send_message, mock_send_photo):
    """Trying to move before both players have joined returns the expected error message"""
    # Arrange
    main.lambda_handler(build_event("/new"), None)
    event_place = build_event("/place a1")

    # Act
    response = main.lambda_handler(event_place, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    found = any("Another player needs to join the game" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    if not found:
        print("All send_message calls:")
        for call in mock_send_message.call_args_list:
            print(call.kwargs.get("text", ""))
    assert found, "Expected 'Another player needs to join the game!' error message not found in send_message calls"


def test_wrong_turn(mock_send_message, mock_send_photo):
    """Trying to move wout of turn returns the expected error message"""
    # Arrange
    initialize_game(mock_send_message, mock_send_photo)
    event_place = build_event("/place a1", user_id=FIRST_USER_ID, user_name=FIRST_USERNAME)

    # Act
    main.lambda_handler(event_place, None)
    response = main.lambda_handler(event_place, None)

    # Assert
    assert response == {"statusCode": 200, "body": "Success"}
    found = any("not your turn" in call.kwargs.get("text", "") for call in mock_send_message.call_args_list)
    if not found:
        print("All send_message calls:")
        for call in mock_send_message.call_args_list:
            print(call.kwargs.get("text", ""))
    assert found, "Expected 'It is not your turn!' error message not found in send_message calls"


# TODO: user that is not part of the game attempts to start new game
# TODO: user that is not part of the game attempts to place a stone
