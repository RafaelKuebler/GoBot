from gobot.go.go import GoGame
from gobot.go.goscreenshot import GoScreenshot
from . import exceptions

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Game(GoGame):
    def __init__(self, chat_id, player, board_x, board_y):
        super().__init__(board_x, board_y)
        self.players = [player]
        self.chat_id = chat_id
        self.cur_player = None
        self.player_passed = [False]
        self.screenshot = GoScreenshot(board_x, board_y)

    def add_player(self, player):
        self.players.append(player)
        self.cur_player = player
        self.player_passed.append(False)

    def change_turn(self):
        super().change_turn()
        if self.cur_player == self.players[0]:
            self.cur_player = self.players[1]
        else:
            self.cur_player = self.players[0]

class GameHandler:
    def __init__(self):
        self.games = {}
        self.players = {}

    def new_game(self, chat_id, player_id, player_name):
        if chat_id in self.games:
            game = self.games[chat_id]
            exceptions.check_player_permissions(player_id, game.players)
            self.players[player_id] = player_name
        self.games[chat_id] = Game(chat_id, player_id, 9, 9)

    def join(self, chat_id, player_id, player_name):
        # TODO: import of detected saved games
        game = self.get_game_with_chat_id(chat_id)
        exceptions.check_enough_players(game)
        self.players[player_id] = player_name
        game.add_player(player_id)

    def place_stone(self, chat_id, player, coord):
        game = self.get_game_with_chat_id(chat_id)
        exceptions.check_all_players_ready(game)
        exceptions.check_player_permissions(player, game.players)
        exceptions.check_player_turn(player, game.cur_player)
        game.place_stone(coord)
        del game.player_passed[0]
        game.player_passed.append(False)
        game.change_turn()

    def pass_turn(self, chat_id, player):
        game = self.get_game_with_chat_id(chat_id)
        exceptions.check_all_players_ready(game)
        exceptions.check_player_permissions(player, game.players)
        exceptions.check_player_turn(player, game.cur_player)
        del game.player_passed[0]
        game.player_passed.append(True)
        game.change_turn()

    def both_players_passed(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        for passed in game.player_passed:
            if not passed:
                return False
        return True

    def calculate_result(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        return game.calculate_result()

    def cur_player_name(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        return self.players[game.cur_player]

    def cur_player_color(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        return game.cur_color.value

    def create_image(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        image = game.screenshot.take_screenshot(game.board)
        return image

    def save_games(self):
        # TODO: export all games to hard disc
        pass

    def remove_game(self, chat_id):
        if chat_id in self.games:
            del self.games[chat_id]

    def get_game_with_chat_id(self, chat_id):
        exceptions.check_chat_id(chat_id, self.games)
        return self.games[chat_id]
