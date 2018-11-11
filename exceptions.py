__author__ = "Rafael Kuebler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class InexistentGameException(Exception):
    pass


class IncorrectTurnException(Exception):
    pass


class CoordOccupiedException(Exception):
    pass


class AlreadyEnoughPlayersException(Exception):
    pass
