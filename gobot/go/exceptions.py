#!/usr/bin/python
# coding: utf-8

from . import settings

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class GoGameException(Exception):
    def __init__(self, message):
        super(GoGameException, self).__init__(message)


class InvalidCoordinatesException(GoGameException):
    def __init__(self, message):
        super(InvalidCoordinatesException, self).__init__(message)


class CoordOccupiedException(GoGameException):
    def __init__(self, message):
        super(CoordOccupiedException, self).__init__(message)


class SelfCaptureException(GoGameException):
    def __init__(self, message):
        super(SelfCaptureException, self).__init__(message)


def check_stone_coords(coords, board):
    if not coords[1:].isdigit():
        raise InvalidCoordinatesException(settings.error_invalid_coords)

    x_in_range = ord('a') <= ord(coords[0]) < ord('a') + board.size_x
    y_in_range = 1 <= int(coords[1:]) <= board.size_y
    if not x_in_range or not y_in_range:
        raise InvalidCoordinatesException(settings.error_invalid_coords)


def check_pos_taken(x, y, board):
    if board.stones[x][y] is not None:
        raise CoordOccupiedException(settings.error_coord_occupied)


def check_self_capture():
    raise SelfCaptureException(settings.error_self_capture)
