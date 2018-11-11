from go import GoGame
from exceptions import IncorrectTurnException, InexistentGameException, CoordOccupiedException

__author__ = "Rafael Kuebler da Silva <rafael_kuebler@yahoo.es>"
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
        self.games[chat_id] = Game(chat_id, players)
        return f"Started new game with players {players}\nCurrent turn: {players[1]}"

    def place_stone(self, chat_id, player, coord):
        if chat_id not in self.games:
            raise InexistentGameException()
        game = self.games[chat_id]
        if game.cur_player != player:
            raise IncorrectTurnException()
        return game.place_stone(player, coord)

    def pass_turn(self, chat_id, player):
        pass

    def create_image(self, chat_id):
        pass

    def save_game(self, chat_id):
        pass

    def result(self, chat_id):
        pass
