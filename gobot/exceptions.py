#!/usr/bin/python
# coding: utf-8

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
