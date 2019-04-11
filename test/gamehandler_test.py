import pytest
from gobot.gamehandler import Game, GameHandler
from gobot.exceptions import *

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class TestGame:
    @pytest.fixture
    def global_vars(self):
        self.player1_id = "ExamplePlayer1ID"
        self.player2_id = "ExamplePlayer2ID"

    def setup_game(self, num_players=2):
        game = Game(9, 9)
        if num_players > 0:
            game.add_player(self.player1_id)
        if num_players > 1:
            game.add_player(self.player2_id)
        return game

    def test_players_empty(self, global_vars):
        game = self.setup_game(num_players=0)

        assert not game.player_ids
        assert not game.cur_player_id
        assert not game.both_players_passed

    def test_add_player(self, global_vars):
        game = self.setup_game(num_players=1)

        assert len(game.player_ids) == 1
        assert self.player1_id in game.player_ids
        assert game.cur_player_id == self.player1_id
        assert not game.both_players_passed

    def test_add_2_players(self, global_vars):
        game = self.setup_game(num_players=2)

        assert len(game.player_ids) == 2
        assert self.player1_id in game.player_ids
        assert self.player2_id in game.player_ids
        assert game.cur_player_id == self.player2_id
        assert not game.both_players_passed

    def test_place_stone(self, mocker, global_vars):
        game = self.setup_game(num_players=2)
        coord = "a1"
        mock_place_stone = mocker.patch('gobot.go.go.GoGame.place_stone')

        game.place_stone(coord)

        mock_place_stone.assert_called_with(coord)
        assert game.cur_player_id == self.player1_id
        assert not game.both_players_passed

    def test_pass_turn_once(self, global_vars):
        game = self.setup_game(num_players=2)
        game.pass_turn()

        assert not game.both_players_passed
        assert game.cur_player_id == self.player1_id

    def test_pass_turn_twice(self, global_vars):
        game = self.setup_game(num_players=2)
        game.pass_turn()
        game.pass_turn()

        assert game.both_players_passed
        assert game.cur_player_id == self.player2_id


class TestGameHandler:
    @pytest.fixture
    def game_handler(self):
        return GameHandler()

    @pytest.fixture
    def global_vars(self):
        self.chat_id = "dummy_chat_id"
        self.player1_id = "ExamplePlayer1ID"
        self.player1_name = "ExamplePlayer1Name"
        self.player2_id = "ExamplePlayer2ID"
        self.player2_name = "ExamplePlayer2Name"

    def setup_game(self, game_handler, num_players=2):
        game_handler.new_game(self.chat_id, self.player1_id)
        if num_players > 0:
            game_handler.join(self.chat_id, self.player1_id, self.player1_name)
        if num_players > 1:
            game_handler.join(self.chat_id, self.player2_id, self.player2_name)

    def test_new_game(self, game_handler, global_vars):
        self.setup_game(game_handler, num_players=1)

        assert len(game_handler.games) == 1
        assert self.chat_id in game_handler.games
        assert type(game_handler.games[self.chat_id]) is Game
        assert len(game_handler.players) == 1
        assert self.player1_id in game_handler.players
        assert game_handler.players[self.player1_id] == self.player1_name

    def test_restart_game(self, game_handler, global_vars):
        self.setup_game(game_handler, num_players=1)

        game_handler.new_game(self.chat_id, self.player1_id)

    def test_no_permission_to_restart(self, game_handler, global_vars):
        self.setup_game(game_handler, num_players=1)

        with pytest.raises(NoPermissionsException):
            game_handler.new_game(self.chat_id, self.player2_id)

    def test_join_1_player(self, mocker, game_handler, global_vars):
        self.setup_game(game_handler, num_players=0)
        game = game_handler.games[self.chat_id]
        add_player = mocker.patch.object(game, 'add_player')

        game_handler.join(self.chat_id, self.player1_id, self.player1_name)

        add_player.assert_called_with(self.player1_id)
        assert len(game_handler.players) == 1
        assert self.player1_id in game_handler.players
        assert game_handler.players[self.player1_id] == self.player1_name

    def test_join_2_players(self, game_handler, global_vars):
        self.setup_game(game_handler)

        assert len(game_handler.players) == 2
        assert self.player1_id in game_handler.players
        assert self.player2_id in game_handler.players
        assert game_handler.players[self.player1_id] == self.player1_name
        assert game_handler.players[self.player2_id] == self.player2_name

    def test_join_inexistent_game(self, game_handler, global_vars):
        with pytest.raises(InexistentGameException):
            game_handler.join(self.chat_id, self.player1_id, self.player1_name)

    def test_join_full_game(self, game_handler, global_vars):
        new_player_id3 = "ExamplePlayerID3"
        new_player_name3 = "ExamplePlayerName3"
        self.setup_game(game_handler)

        with pytest.raises(UnexpectedNumberOfPlayersException):
            game_handler.join(self.chat_id, new_player_id3, new_player_name3)

    def test_place_stone(self, mocker, game_handler, global_vars):
        self.setup_game(game_handler)
        game = game_handler.games[self.chat_id]
        mock_place_stone = mocker.patch.object(game, 'place_stone')
        coord = "a1"

        game_handler.place_stone(self.chat_id, self.player2_id, coord)

        mock_place_stone.assert_called_with(coord)
