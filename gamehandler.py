from go import GoGame
import exceptions
import goscreenshot

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Game:
    def __init__(self, chat_id, players):
        self.go_game = GoGame()
        self.players = players
        self.chat_id = chat_id
        self.cur_player = players[1]


class GameHandler:
    def __init__(self):
        self.games = {}

    def new_game(self, chat_id, players):
        # TODO: add import for detected saved games
        self.games[chat_id] = Game(chat_id, players)

    def place_stone(self, chat_id, player, coord):
        game = self.get_game_with_chat_id(chat_id)
        exceptions.sanitize_player_turn(player, game.cur_player)
        game.place_stone(player, coord)

    def cur_player(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        return game.cur_player

    def pass_turn(self, chat_id, player):
        game = self.get_game_with_chat_id(chat_id)
        exceptions.sanitize_player_turn(player, game.cur_player)
        # TODO: implement pass

    def create_image(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        screenshot = goscreenshot.take_screenshot(game.go_game.board)
        return screenshot

    def save_game(self, chat_id):
        # TODO: export game to hard disc
        pass

    def calculate_result(self, chat_id):
        # TODO: Calculate the area each player has
        pass

    def get_game_with_chat_id(self, chat_id):
        exceptions.sanitize_chat_id(chat_id, self.games)
        return self.games[chat_id]
