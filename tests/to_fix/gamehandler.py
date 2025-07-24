import os

import pytest

from gobot.telegram.gamehandler import GameHandler, GameHandlerException, TelegramGoGame

os.environ["DB"] = "0"

DEFAULT_CHAT_ID = 123456
FIRST_USER_ID = 111111
FIRST_USERNAME = "'Alice'"
SECOND_USER_ID = 222222
SECOND_USERNAME = "'Bob'"
THIRD_USER_ID = 333333
THIRD_USER_ID = "'Carson'"


class TestGameHandler:
    @pytest.fixture
    def game_handler(self):
        return GameHandler()

    def setup_game(self, game_handler, num_players=2):
        game_handler.new_game(self.chat_id, self.player1_id)
        if num_players > 0:
            game_handler.join(self.chat_id, self.player1_id, self.player1_name)
        if num_players > 1:
            game_handler.join(self.chat_id, self.player2_id, self.player2_name)

    def test_new_game(self, game_handler):
        self.setup_game(game_handler, num_players=1)

        assert len(game_handler.games) == 1
        assert self.chat_id in game_handler.games
        assert type(game_handler.games[self.chat_id]) is TelegramGoGame
        assert len(game_handler.players) == 1
        assert self.player1_id in game_handler.players
        assert game_handler.players[self.player1_id] == self.player1_name

    def test_restart_game(self, game_handler):
        self.setup_game(game_handler, num_players=1)
        game_handler.new_game(self.chat_id, self.player1_id)

    def test_no_permission_to_restart(self, game_handler):
        self.setup_game(game_handler, num_players=1)
        with pytest.raises(GameHandlerException):
            game_handler.new_game(self.chat_id, self.player2_id)

    def test_join_1_player(self, game_handler):
        self.setup_game(game_handler, num_players=0)
        mock_add_player = mocker.patch("gobot.gamehandler.TelegramGoGame.add_player")

        game_handler.join(self.chat_id, self.player1_id, self.player1_name)
        mock_add_player.assert_called_with(self.player1_id)
        assert len(game_handler.players) == 1
        assert self.player1_id in game_handler.players
        assert game_handler.players[self.player1_id] == self.player1_name

    def test_join_2_players(self, game_handler):
        self.setup_game(game_handler)

        assert len(game_handler.players) == 2
        assert self.player1_id in game_handler.players
        assert self.player2_id in game_handler.players
        assert game_handler.players[self.player1_id] == self.player1_name
        assert game_handler.players[self.player2_id] == self.player2_name

    def test_join_inexistent_game(self, game_handler):
        with pytest.raises(GameHandlerException):
            game_handler.join(self.chat_id, self.player1_id, self.player1_name)

    def test_join_full_game(self, game_handler):
        self.setup_game(game_handler)
        with pytest.raises(GameHandlerException):
            game_handler.join(self.chat_id, self.player3_id, self.player3_name)

    def test_first_player_black(self, game_handler):
        self.setup_game(game_handler)

        assert game_handler.cur_player_color(self.chat_id) == "black"

    def test_place_stone(self, game_handler):
        self.setup_game(game_handler)
        mock_place_stone = mocker.patch("gobot.gamehandler.TelegramGoGame.place_stone_str_coord")

        game_handler.place_stone(self.chat_id, self.player2_id, self.coord)
        mock_place_stone.assert_called_with(self.coord)

    def test_place_stone_not_enough_players(self, game_handler):
        self.setup_game(game_handler, num_players=1)
        with pytest.raises(GameHandlerException):
            game_handler.place_stone(self.chat_id, self.player1_id, self.coord)

    def test_place_stone_no_permission(self, game_handler):
        self.setup_game(game_handler)
        with pytest.raises(GameHandlerException):
            game_handler.place_stone(self.chat_id, self.player3_id, self.coord)

    def test_place_stone_incorrect_turn(self, game_handler):
        self.setup_game(game_handler)
        with pytest.raises(GameHandlerException):
            game_handler.place_stone(self.chat_id, self.player1_id, self.coord)

    def test_pass_turn(self, game_handler):
        self.setup_game(game_handler)
        mock_pass_turn = mocker.patch("gobot.gamehandler.TelegramGoGame.pass_turn")

        game_handler.pass_turn(self.chat_id, self.player2_id)
        mock_pass_turn.assert_called_once()

    def test_pass_turn_not_enough_players(self, game_handler):
        self.setup_game(game_handler, num_players=1)
        with pytest.raises(GameHandlerException):
            game_handler.pass_turn(self.chat_id, self.player1_id)

    def test_pass_turn_no_permission(self, game_handler):
        self.setup_game(game_handler)
        with pytest.raises(GameHandlerException):
            game_handler.pass_turn(self.chat_id, self.player3_id)

    def test_pass_turn_incorrect_turn(self, game_handler):
        self.setup_game(game_handler)
        with pytest.raises(GameHandlerException):
            game_handler.pass_turn(self.chat_id, self.player1_id)

    def test_no_player_passed(self, game_handler):
        self.setup_game(game_handler)
        assert not game_handler.both_players_have_passed(self.chat_id)

    def test_one_player_passed(self, game_handler):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        assert not game_handler.both_players_have_passed(self.chat_id)

    def test_both_player_passed(self, game_handler):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        game_handler.pass_turn(self.chat_id, self.player1_id)
        assert game_handler.both_players_have_passed(self.chat_id)

    def test_cur_player_name_player1(self, game_handler):
        self.setup_game(game_handler)
        assert game_handler.cur_player_name(self.chat_id) == self.player2_name

    def test_cur_player_name_player2(self, game_handler):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        assert game_handler.cur_player_name(self.chat_id) == self.player1_name

    def test_cur_player_color_player1(self, game_handler):
        self.setup_game(game_handler)
        assert game_handler.cur_player_color(self.chat_id) == "black"

    def test_cur_player_color_player2(self, game_handler):
        self.setup_game(game_handler)
        game_handler.pass_turn(self.chat_id, self.player2_id)
        assert game_handler.cur_player_color(self.chat_id) == "white"

    def test_create_image(self, game_handler):
        self.setup_game(game_handler)
        mock_screenshot = mocker.patch("gobot.gamehandler.TelegramGoGame.take_screenshot")

        game_handler.create_image(self.chat_id)
        mock_screenshot.assert_called_once()

    def test_remove_game(self, game_handler):
        self.setup_game(game_handler)
        game_handler.remove_game(self.chat_id)
        assert self.chat_id not in game_handler.games

    # TODO: test calculate_result
