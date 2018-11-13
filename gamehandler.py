from go import GoGame
import exceptions
import goscreenshot

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Game:
    def __init__(self, chat_id, player):
        self.go_game = GoGame()
        self.players = [player]
        self.chat_id = chat_id
        self.cur_player = None

    def add_player(self, player):
        self.players.append(player)
        self.cur_player = player


class GameHandler:
    def __init__(self):
        self.games = {}

    def new_game(self, chat_id, player):
        # TODO: only allow one of the current players to overwrite the game
        self.games[chat_id] = Game(chat_id, player)

    def join(self, chat_id, player):
        # TODO: import of detected saved games
        # TODO: reject join request if game is already full
        game = self.get_game_with_chat_id(chat_id)
        game.add_player(player)

    def place_stone(self, chat_id, player, coord):
        game = self.get_game_with_chat_id(chat_id)
        exceptions.sanitize_all_players_ready(game)
        exceptions.sanitize_player_turn(player, game.cur_player)
        game.go_game.place_stone(coord)
        self.change_turn(game)

    @staticmethod
    def change_turn(game):
        game.go_game.change_turn()
        if game.cur_player == game.players[0]:
            game.cur_player = game.players[1]
        else:
            game.cur_player = game.players[0]

    def cur_player(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        return game.cur_player

    def pass_turn(self, chat_id, player):
        # TODO: implement pass
        game = self.get_game_with_chat_id(chat_id)
        exceptions.sanitize_player_turn(player, game.cur_player)

    def create_image(self, chat_id):
        game = self.get_game_with_chat_id(chat_id)
        screenshot = goscreenshot.take_screenshot(game.go_game.board.stones)
        return screenshot

    def save_game(self, chat_id):
        # TODO: export game to hard disc
        pass

    def get_game_with_chat_id(self, chat_id):
        exceptions.sanitize_chat_id(chat_id, self.games)
        return self.games[chat_id]
