import os

import pytest

from gobot.telegram.exceptions import IncorrectTurnException, InexistentGameException, NoPermissionsException, UnexpectedNumberOfPlayersException
from gobot.telegram.gamehandler import Game, GameHandler

os.environ["DB"] = "0"


class TestGame:
    @pytest.fixture
    def global_vars(self):
        self.player1_id = 5555555
        self.player2_id = 7777777

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
        game = self.setup_game()

        assert len(game.player_ids) == 2
        assert self.player1_id in game.player_ids
        assert self.player2_id in game.player_ids
        assert game.cur_player_id == self.player2_id
        assert not game.both_players_passed

    def test_place_stone(self, mocker, global_vars):
        game = self.setup_game()
        coord = "a1"
        mock_place_stone = mocker.patch("gobot.go.go.GoGame.place_stone_str_coord")

        game.place_stone_str_coord(coord)
        mock_place_stone.assert_called_with(coord, "black")
        assert game.cur_player_id == self.player1_id
        assert not game.both_players_passed

    def test_pass_turn_once(self, global_vars):
        game = self.setup_game()
        game.pass_turn()

        assert not game.both_players_passed
        assert game.cur_player_id == self.player1_id
        assert game.cur_player_color == "white"

    def test_pass_turn_twice(self, global_vars):
        game = self.setup_game()
        game.pass_turn()
        game.pass_turn()

        assert game.both_players_passed
        assert game.cur_player_id == self.player2_id
        assert game.cur_player_color == "black"

    def test_take_screenshot(self, mocker, global_vars):
        game = self.setup_game()
        mock_screenshot = mocker.patch("gobot.go.goscreenshot.GoScreenShot.take_screenshot")

        game.take_screenshot()
        mock_screenshot.assert_called_with(game.board, None)


class TestGameHandler:
    @pytest.fixture
    def game_handler(self):
        return GameHandler()

    @pytest.fixture
    def global_vars(self):
        self.chat_id = 9999999
        self.player1_id = 555555
        self.player1_name = "ExamplePlayer1Name"
        self.player2_id = 777777
        self.player2_name = "ExamplePlayer2Name"
        self.player3_id = 888888
        self.player3_name = "ExamplePlayerName3"
        self.coord = "a1"

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
        mock_add_player = mocker.patch("gobot.gamehandler.Game.add_player")

        game_handler.join(self.chat_id, self.player1_id, self.player1_name)
        mock_add_player.assert_called_with(self.player1_id)
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
        self.setup_game(game_handler)
        with pytest.raises(UnexpectedNumberOfPlayersException):
            game_handler.join(self.chat_id, self.player3_id, self.player3_name)

    def test_first_player_black(self, game_handler, global_vars):
        self.setup_game(game_handler)

        assert game_handler.cur_player_color(self.chat_id) == "black"

    def test_place_stone(self, mocker, game_handler, global_vars):
        self.setup_game(game_handler)
        mock_place_stone = mocker.patch("gobot.gamehandler.Game.place_stone_str_coord")

        game_handler.place_stone(self.chat_id, self.player2_id, self.coord)
        mock_place_stone.assert_called_with(self.coord)

    def test_place_stone_not_enough_players(self, game_handler, global_vars):
        self.setup_game(game_handler, num_players=1)
        with pytest.raises(UnexpectedNumberOfPlayersException):
            game_handler.place_stone(self.chat_id, self.player1_id, self.coord)

    def test_place_stone_no_permission(self, game_handler, global_vars):
        self.setup_game(game_handler)
        with pytest.raises(NoPermissionsException):
            game_handler.place_stone(self.chat_id, self.player3_id, self.coord)

    def test_place_stone_incorrect_turn(self, game_handler, global_vars):
        self.setup_game(game_handler)
        with pytest.raises(IncorrectTurnException):
            game_handler.place_stone(self.chat_id, self.player1_id, self.coord)

    def test_pass_turn(self, mocker, game_handler, global_vars):
        self.setup_game(game_handler)
        mock_pass_turn = mocker.patch("gobot.gamehandler.Game.pass_turn")

        game_handler.pass_turn(self.chat_id, self.player2_id)
        mock_pass_turn.assert_called_once()

    def test_pass_turn_not_enough_players(self, game_handler, global_vars):
        self.setup_game(game_handler, num_players=1)
        with pytest.raises(UnexpectedNumberOfPlayersException):
            game_handler.pass_turn(self.chat_id, self.player1_id)

    def test_pass_turn_no_permission(self, game_handler, global_vars):
        self.setup_game(game_handler)
        with pytest.raises(NoPermissionsException):
            game_handler.pass_turn(self.chat_id, self.player3_id)

    def test_pass_turn_incorrect_turn(self, game_handler, global_vars):
        self.setup_game(game_handler)
        with pytest.raises(IncorrectTurnException):
            game_handler.pass_turn(self.chat_id, self.player1_id)

    def test_no_player_passed(self, game_handler, global_vars):
        self.setup_game(game_handler)
        assert not game_handler.both_players_passed(self.chat_id)

    def test_one_player_passed(self, game_handler, global_vars):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        assert not game_handler.both_players_passed(self.chat_id)

    def test_both_player_passed(self, game_handler, global_vars):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        game_handler.pass_turn(self.chat_id, self.player1_id)
        assert game_handler.both_players_passed(self.chat_id)

    def test_cur_player_name_player1(self, game_handler, global_vars):
        self.setup_game(game_handler)
        assert game_handler.cur_player_name(self.chat_id) == self.player2_name

    def test_cur_player_name_player2(self, game_handler, global_vars):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        assert game_handler.cur_player_name(self.chat_id) == self.player1_name

    def test_cur_player_color_player1(self, game_handler, global_vars):
        self.setup_game(game_handler)
        assert game_handler.cur_player_color(self.chat_id) == "black"

    def test_cur_player_color_player2(self, game_handler, global_vars):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        assert game_handler.cur_player_color(self.chat_id) == "white"

    def test_create_image(self, mocker, game_handler, global_vars):
        self.setup_game(game_handler)
        mock_screenshot = mocker.patch("gobot.gamehandler.Game.take_screenshot")

        game_handler.create_image(self.chat_id)
        mock_screenshot.assert_called_once()

    def test_remove_game(self, game_handler, global_vars):
        self.setup_game(game_handler)
        game_handler.remove_game(self.chat_id)
        assert self.chat_id not in game_handler.games

    # TODO: test calculate_result
