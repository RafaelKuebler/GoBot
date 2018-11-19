#!/usr/bin/python
# coding: utf-8

import random
from . import settings
from gobot.go.exceptions import GoGameException

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class InexistentGameException(GoGameException):
    def __init__(self, message):
        super(InexistentGameException, self).__init__(message)


class IncorrectTurnException(GoGameException):
    def __init__(self, message):
        super(IncorrectTurnException, self).__init__(message)


class UnexpectedNumberOfPlayersException(GoGameException):
    def __init__(self, message):
        super(UnexpectedNumberOfPlayersException, self).__init__(message)


class NoPermissionsException(GoGameException):
    def __init__(self, message):
        super(NoPermissionsException, self).__init__(message)


def check_chat_id(chat_id, games):
    if chat_id not in games:
        raise InexistentGameException(settings.error_inexistent_game)


def check_player_turn(player, cur_player):
    if player != cur_player:
        proverb = "_{}_".format(random.choice(settings.patience_proverbs))
        message = "{}\n{}".format(proverb, settings.error_incorrect_turn)
        raise IncorrectTurnException(message)


def check_all_players_ready(game):
    if game.cur_player is None:
        raise UnexpectedNumberOfPlayersException(settings.error_not_enough_players)


def check_enough_players(game):
    if len(game.players) == 2:
        raise UnexpectedNumberOfPlayersException(settings.error_already_enough_players)


def check_player_permissions(player, players):
    if player not in players:
        raise NoPermissionsException(settings.error_permissions)
