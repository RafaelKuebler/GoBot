
__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class GoGameException(Exception):
    def __init__(self, message):
        super(GoGameException, self).__init__(message)


class InvalidCoordinateException(GoGameException):
    def __init__(self, message):
        super(InvalidCoordinateException, self).__init__(message)


class CoordOccupiedException(GoGameException):
    def __init__(self, message):
        super(CoordOccupiedException, self).__init__(message)


class SelfCaptureException(GoGameException):
    def __init__(self, message):
        super(SelfCaptureException, self).__init__(message)


class InvalidBoardSizeException(GoGameException):
    def __init__(self, message):
        super(InvalidBoardSizeException, self).__init__(message)


class KoException(GoGameException):
    def __init__(self, message):
        super(KoException, self).__init__(message)
