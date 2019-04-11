import pytest
from gobot.gamehandler import Game, GameHandler
from gobot.exceptions import *

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class TestGame:
    def test_players_empty(self):
        chat_id = "dummy_chat_id"
        game = Game(chat_id, 9, 9)
        assert not game.players

    def test_add_player(self):
        chat_id = "dummy_chat_id"
        new_player = "ExamplePlayer1"
        game = Game(chat_id, 9, 9)
        game.add_player(new_player)
        assert len(game.players) == 1
        assert new_player in game.players

    def test_add_2_players(self):
        chat_id = "dummy_chat_id"
        new_player1 = "ExamplePlayerID1"
        new_player2 = "ExamplePlayerID2"
        game = Game(chat_id, 9, 9)
        game.add_player(new_player1)
        game.add_player(new_player2)
        assert len(game.players) == 2
        assert new_player1 in game.players
        assert new_player2 in game.players


class TestGameHandler:
    def test_new_game(self):
        chat_id = "dummy_chat_id"
        game_handler = GameHandler()
        new_player_id = "ExamplePlayerID1"
        new_player_name = "ExamplePlayerName1"

        game_handler.new_game(chat_id, new_player_id)
        game_handler.join(chat_id, new_player_id, new_player_name)
        assert len(game_handler.players) == 1
        assert new_player_id in game_handler.players
        assert game_handler.players[new_player_id] == new_player_name

    def test_restart_game(self):
        chat_id = "dummy_chat_id"
        game_handler = GameHandler()
        new_player_id = "ExamplePlayerID1"
        new_player_name = "ExamplePlayerName1"

        game_handler.new_game(chat_id, new_player_id)
        game_handler.join(chat_id, new_player_id, new_player_name)
        game_handler.new_game(chat_id, new_player_id)

    def test_no_permission_to_restart(self):
        chat_id = "dummy_chat_id"
        game_handler = GameHandler()
        new_player_id = "ExamplePlayerID1"

        game_handler.new_game(chat_id, new_player_id)
        with pytest.raises(NoPermissionsException):
            game_handler.new_game(chat_id, new_player_id)

    def test_join_player(self):
        game_handler = GameHandler()
        chat_id = "dummy_chat_id"
        new_player_id = "ExamplePlayerID1"
        new_player_name = "ExamplePlayerName1"

        game_handler.new_game(chat_id, new_player_id)
        game_handler.join(chat_id, new_player_id, new_player_name)
        assert len(game_handler.players) == 1
        assert new_player_id in game_handler.players
        assert game_handler.players[new_player_id] == new_player_name

    def test_join_2_players(self):
        game_handler = GameHandler()
        chat_id = "dummy_chat_id"
        new_player_id1 = "ExamplePlayerID1"
        new_player_name1 = "ExamplePlayerName1"
        new_player_id2 = "ExamplePlayerID2"
        new_player_name2 = "ExamplePlayerName2"

        game_handler.new_game(chat_id, new_player_id1)
        game_handler.join(chat_id, new_player_id1, new_player_name1)
        game_handler.join(chat_id, new_player_id2, new_player_name2)
        assert len(game_handler.players) == 2
        assert new_player_id1 in game_handler.players
        assert new_player_id2 in game_handler.players
        assert game_handler.players[new_player_id1] == new_player_name1
        assert game_handler.players[new_player_id2] == new_player_name2

    def test_join_inexistent_game(self):
        game_handler = GameHandler()
        chat_id = "dummy_chat_id"
        new_player_id = "ExamplePlayerID1"
        new_player_name = "ExamplePlayerName1"

        with pytest.raises(InexistentGameException):
            game_handler.join(chat_id, new_player_id, new_player_name)

    def test_join_full_game(self):
        with pytest.raises(InexistentGameException):
            game_handler = GameHandler()
            chat_id = "dummy_chat_id"
            new_player_id1 = "ExamplePlayerID1"
            new_player_name1 = "ExamplePlayerName1"
            new_player_id2 = "ExamplePlayerID2"
            new_player_name2 = "ExamplePlayerName2"
            new_player_id3 = "ExamplePlayerID3"
            new_player_name3 = "ExamplePlayerName3"

            game_handler.join(chat_id, new_player_id1, new_player_name1)
            game_handler.join(chat_id, new_player_id2, new_player_name2)
            with pytest.raises(UnexpectedNumberOfPlayersException):
                game_handler.join(chat_id, new_player_id3, new_player_name3)
