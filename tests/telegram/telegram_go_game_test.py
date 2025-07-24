import os

from gobot.telegram.gamehandler import TelegramGoGame
from gobot.telegram.player_color import PlayerColor

os.environ["DB"] = "0"

DEFAULT_CHAT_ID = 123456
FIRST_USER_ID = 111111
FIRST_USERNAME = "'Alice'"
SECOND_USER_ID = 222222
SECOND_USERNAME = "'Bob'"


class TestGame:
    def setup_game(self, num_players: int = 2) -> TelegramGoGame:
        """Set up a TelegramGoGame with the number of players"""
        game = TelegramGoGame(DEFAULT_CHAT_ID, 9, 9)
        if num_players > 0:
            game.add_player(FIRST_USER_ID, FIRST_USERNAME)
        if num_players > 1:
            game.add_player(SECOND_USER_ID, SECOND_USERNAME)
        return game

    def test_players_initially_empty(self):
        # Arrange & Act
        game = self.setup_game(num_players=0)
        # Assert
        assert not game.players
        assert game.current_player is None

    def test_add_player(self):
        # Arrange & Act
        game = self.setup_game(num_players=1)
        # Assert
        assert len(game.players) == 1
        assert game.current_player is not None
        assert game.current_player_index == 0
        assert game.current_player == game.players[0]
        assert game.current_player.id_ == FIRST_USER_ID
        assert game.current_player.name == FIRST_USERNAME
        assert not game.current_player.did_pass
        assert game.current_player.color == PlayerColor.WHITE

    def test_add_2_players(self):
        # Arrange & Act
        game = self.setup_game()
        # Assert
        assert len(game.players) == 2
        assert game.current_player is not None
        assert game.current_player_index == 1
        assert game.current_player == game.players[1]
        # player 1
        assert game.players[0].id_ == FIRST_USER_ID
        assert game.players[0].name == FIRST_USERNAME
        assert not game.players[0].did_pass
        assert game.players[0].color == PlayerColor.WHITE
        # player 2
        assert game.players[1].id_ == SECOND_USER_ID
        assert game.players[1].name == SECOND_USERNAME
        assert not game.players[1].did_pass
        assert game.players[1].color == PlayerColor.BLACK

    def test_place_stone(self):
        # Arrange
        game = self.setup_game()
        # Act
        game.place_stone_str_coord("a1")
        # Assert
        assert game.board[0][0].color == "black"

    def test_pass_turn_once(self):
        # Arrange
        game = self.setup_game()
        # Act
        game.pass_turn()
        # Assert
        assert not game.is_game_over
        assert game.current_player_index == 0
        assert game.current_player is not None
        assert game.current_player.color == "white"

    def test_pass_turn_twice(self):
        # Arrange
        game = self.setup_game()
        # Act
        game.pass_turn()
        game.pass_turn()
        # Assert
        assert game.is_game_over
