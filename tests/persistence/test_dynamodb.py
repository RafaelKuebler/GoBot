from gobot.persistence.dynamodb import to_db_format, to_domain
from gobot.telegram.player_color import PlayerColor
from gobot.telegram.telegram_go_game import TelegramGoGame


class TestToDbFormat:
    def test_converts_minimal_game_with_one_player(self):
        game = TelegramGoGame(chat_id=123456, board_x=9, board_y=9)
        game.add_player(111, "Player1")

        result = to_db_format(game)

        assert result["chat_id"] == 123456
        assert result["size_x"] == 9
        assert result["size_y"] == 9
        assert result["player1_id"] == 111
        assert result["player1_name"] == "Player1"
        assert result["player1_passed"] is False
        assert result["player2_id"] is None
        assert result["player2_name"] is None
        assert result["player2_passed"] is False
        assert result["turn_player_index"] == 0
        assert result["last_stone"] is None
        assert result["last_capt_stone"] is None
        assert result["board"] == {}

    def test_converts_game_with_two_players(self):
        game = TelegramGoGame(chat_id=123456, board_x=9, board_y=9)
        game.add_player(111, "Player1")
        game.add_player(222, "Player2")

        result = to_db_format(game)

        assert result["player1_id"] == 111
        assert result["player1_name"] == "Player1"
        assert result["player2_id"] == 222
        assert result["player2_name"] == "Player2"

    def test_converts_game_with_stones_on_board(self):
        game = TelegramGoGame(chat_id=123456, board_x=9, board_y=9)
        game.add_player(111, "Player1")
        game.add_player(222, "Player2")
        game.place_stone(3, 3, PlayerColor.WHITE)
        game.place_stone(4, 4, PlayerColor.BLACK)

        result = to_db_format(game)

        assert result["board"]["3,3"] == PlayerColor.WHITE
        assert result["board"]["4,4"] == PlayerColor.BLACK
        assert len(result["board"]) == 2

    def test_converts_game_with_last_stone_placed(self):
        game = TelegramGoGame(chat_id=123456, board_x=9, board_y=9)
        game.add_player(111, "Player1")
        game.add_player(222, "Player2")
        game.place_stone_str_coord("d4")  # Uses string coord which sets last_stone_placed

        result = to_db_format(game)

        assert result["last_stone"] == "3,3"

    def test_converts_game_with_player_passed(self):
        game = TelegramGoGame(chat_id=123456, board_x=9, board_y=9)
        game.add_player(111, "Player1")
        game.add_player(222, "Player2")
        game.players[0].did_pass = True

        result = to_db_format(game)

        assert result["player1_passed"] is True


class TestToDomain:
    def test_converts_minimal_db_format_to_game(self):
        db_format = {
            "chat_id": 123456,
            "size_x": 9,
            "size_y": 9,
            "player1_id": 111,
            "player1_name": "Player1",
            "player1_passed": False,
            "player2_id": None,
            "player2_name": None,
            "player2_passed": False,
            "turn_player_index": 0,
            "last_stone": None,
            "last_capt_stone": None,
            "board": {},
        }

        game = to_domain(db_format)

        assert game.chat_id == 123456
        assert game.size_x == 9
        assert game.size_y == 9
        assert len(game.players) == 1
        assert game.players[0].id_ == 111
        assert game.players[0].name == "Player1"
        assert game.players[0].did_pass is False
        assert game.current_player_index == 0
        assert game.last_stone_placed is None

    def test_converts_db_format_with_two_players(self):
        db_format = {
            "chat_id": 123456,
            "size_x": 9,
            "size_y": 9,
            "player1_id": 111,
            "player1_name": "Player1",
            "player1_passed": False,
            "player2_id": 222,
            "player2_name": "Player2",
            "player2_passed": True,
            "turn_player_index": 1,
            "last_stone": None,
            "last_capt_stone": None,
            "board": {},
        }

        game = to_domain(db_format)

        assert len(game.players) == 2
        assert game.players[1].id_ == 222
        assert game.players[1].name == "Player2"
        assert game.players[1].did_pass is True
        assert game.current_player_index == 1

    def test_converts_db_format_with_board_state(self):
        db_format = {
            "chat_id": 123456,
            "size_x": 9,
            "size_y": 9,
            "player1_id": 111,
            "player1_name": "Player1",
            "player1_passed": False,
            "player2_id": 222,
            "player2_name": "Player2",
            "player2_passed": False,
            "turn_player_index": 0,
            "last_stone": "3,3",
            "last_capt_stone": None,
            "board": {
                "3,3": PlayerColor.WHITE,
                "4,4": PlayerColor.BLACK,
            },
        }

        game = to_domain(db_format)

        assert not game.board[3][3].is_free
        assert game.board[3][3].color == PlayerColor.WHITE
        assert not game.board[4][4].is_free
        assert game.board[4][4].color == PlayerColor.BLACK
        assert game.last_stone_placed == (3, 3)


class TestRoundTrip:
    def test_round_trip_preserves_game_state(self):
        original_game = TelegramGoGame(chat_id=999, board_x=19, board_y=19)
        original_game.add_player(111, "Alice")
        original_game.add_player(222, "Bob")
        original_game.place_stone(10, 10, PlayerColor.WHITE)
        original_game.place_stone(11, 11, PlayerColor.BLACK)
        original_game.players[0].did_pass = False
        original_game.players[1].did_pass = True

        db_format = to_db_format(original_game)
        restored_game = to_domain(db_format)

        assert restored_game.chat_id == original_game.chat_id
        assert restored_game.size_x == original_game.size_x
        assert restored_game.size_y == original_game.size_y
        assert len(restored_game.players) == len(original_game.players)
        assert restored_game.players[0].id_ == original_game.players[0].id_
        assert restored_game.players[1].id_ == original_game.players[1].id_
        assert restored_game.players[0].name == original_game.players[0].name
        assert restored_game.players[1].name == original_game.players[1].name
        assert restored_game.players[0].did_pass == original_game.players[0].did_pass
        assert restored_game.players[1].did_pass == original_game.players[1].did_pass
        assert restored_game.board[10][10].color == PlayerColor.WHITE
        assert restored_game.board[11][11].color == PlayerColor.BLACK
