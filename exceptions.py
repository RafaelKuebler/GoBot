__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class GoGameException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InexistentGameException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


class IncorrectTurnException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


class InvalidCoordinatesException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


class CoordOccupiedException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


class NotEnoughPlayersException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


def sanitize_chat_id(chat_id, games):
    if chat_id not in games:
        raise InexistentGameException("Please start a game with /new first!")


def sanitize_player_turn(player, cur_player):
    if player != cur_player:
        raise IncorrectTurnException("It is not your turn!")


def sanitize_stone_coords(coords, board):
    x_in_range = coords[0] not in range(ord('a'), board.size_x)
    y_in_range = coords[1] not in range(0, board.size_y)
    if not x_in_range or not y_in_range:
        raise InvalidCoordinatesException("This coordinate does not exist on the board!")


def sanitize_pos_taken(x, y, board):
    if board.stones[x][y] is not None:
        raise CoordOccupiedException("This coordinate already holds a stone!")


def sanitize_all_players_ready(game):
    if game.cur_player is None:
        raise NotEnoughPlayersException("Another player needs to join the game!")
