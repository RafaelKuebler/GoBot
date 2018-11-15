#!/usr/bin/python
# coding: utf-8

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


class UnexpectedNumberOfPlayersException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


class SelfCaptureException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


class NoPermissionsException(GoGameException):
    def __init__(self, message):
        super().__init__(message)


def check_chat_id(chat_id, games):
    if chat_id not in games:
        raise InexistentGameException(settings.error_inexistent_game)


def check_player_turn(player, cur_player):
    if player != cur_player:
        proverb = "_{}_".format(random.choice(settings.patience_proverbs))
        message = "{}\n{}".format(proverb, settings.error_incorrect_turn)
        raise IncorrectTurnException(message)


def check_stone_coords(coords, board):
    x_in_range = coords[0] not in range(ord('a'), board.size_x)
    y_in_range = coords[1] not in range(0, board.size_y)
    if not x_in_range or not y_in_range:
        raise InvalidCoordinatesException(settings.error_invalid_coords)


def check_pos_taken(x, y, board):
    if board.stones[x][y] is not None:
        raise CoordOccupiedException(settings.error_coord_occupied)


def check_all_players_ready(game):
    if game.cur_player is None:
        raise UnexpectedNumberOfPlayersException(settings.error_not_enough_players)


def check_enough_players(game):
    if len(game.players) == 2:
        raise UnexpectedNumberOfPlayersException(settings.error_already_enough_players)


def check_self_capture():
    raise SelfCaptureException(settings.error_self_capture)


def check_player_permissions(player, players):
    if player not in players:
        raise NoPermissionsException(settings.error_permissions)
