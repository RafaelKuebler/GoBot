from src import settings
import random

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


class SelfCaptureException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


def sanitize_chat_id(chat_id, games):
    if chat_id not in games:
        raise InexistentGameException(settings.error_inexistent_game)


def sanitize_player_turn(player, cur_player):
    if player != cur_player:
        proverb = f"_{random.choice(settings.patience_proverbs)}_"
        raise IncorrectTurnException(f"{proverb}\n{settings.error_incorrect_turn}")


def sanitize_stone_coords(coords, board):
    x_in_range = coords[0] not in range(ord('a'), board.size_x)
    y_in_range = coords[1] not in range(0, board.size_y)
    if not x_in_range or not y_in_range:
        raise InvalidCoordinatesException(settings.error_invalid_coords)


def sanitize_pos_taken(x, y, board):
    if board.stones[x][y] is not None:
        raise CoordOccupiedException(settings.error_coord_occupied)


def sanitize_all_players_ready(game):
    if game.cur_player is None:
        raise NotEnoughPlayersException(settings.error_not_enough_players)


def check_self_capture():
    raise SelfCaptureException(settings.error_self_capture)
