import random
from PIL.JpegImagePlugin import JpegImageFile
from typing import List, Dict, Optional
from gobot.go.go import GoGame
from gobot.go.goscreenshot import GoScreenShot
from .exceptions import *
from . import settings

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Game(GoGame):
    def __init__(self, board_x: int, board_y: int) -> None:
        super().__init__(board_x, board_y)
        self.player_ids: List[int] = []
        self.cur_player_id: Optional[int] = None
        self.cur_player_color: str = "black"
        self._player_passed: List[bool] = []
        self.screenshot: GoScreenShot = GoScreenShot(board_x, board_y)

    @property
    def both_players_passed(self) -> bool:
        if not self._player_passed:
            return False
        return all(self._player_passed)

    def add_player(self, player_id: int) -> None:
        self.player_ids.append(player_id)
        self.cur_player_id = player_id
        self._player_passed.append(False)

    def place_stone(self, coord: str, color: Optional[str] = None) -> None:
        super().place_stone(coord, self.cur_player_color)
        del self._player_passed[0]
        self._player_passed.append(False)
        self._change_turn()

    def pass_turn(self) -> None:
        del self._player_passed[0]
        self._player_passed.append(True)
        self._change_turn()

    def _change_turn(self) -> None:
        if self.cur_player_id == self.player_ids[0]:
            self.cur_player_id = self.player_ids[1]
        else:
            self.cur_player_id = self.player_ids[0]

        if self.cur_player_color == "white":
            self.cur_player_color = "black"
        else:
            self.cur_player_color = "white"

    def take_screenshot(self) -> JpegImageFile:
        image = self.screenshot.take_screenshot(self.board, self.last_stone_placed)
        return image


class GameHandler:
    def __init__(self) -> None:
        self.games: Dict[int, Game] = {}
        self.players: Dict[int, str] = {}

    def new_game(self, chat_id: int, player_id: int) -> None:
        if chat_id in self.games:
            game = self.games[chat_id]
            self._check_player_permissions(player_id, game.player_ids)
        self.games[chat_id] = Game(9, 9)

    def join(self, chat_id: int, player_id: int, player_name: str) -> None:
        # TODO: import of detected saved games
        game = self._get_game_with_chat_id(chat_id)
        self._check_player_limit(game)
        self.players[player_id] = player_name
        game.add_player(player_id)

    def place_stone(self, chat_id: int, player_id: int, coord: str) -> None:
        game = self._get_game_with_chat_id(chat_id)
        self._check_enough_players(game)
        self._check_player_permissions(player_id, game.player_ids)
        self._check_player_turn(player_id, game.cur_player_id)
        game.place_stone(coord)

    def pass_turn(self, chat_id: int, player_id: int) -> None:
        game = self._get_game_with_chat_id(chat_id)
        self._check_enough_players(game)
        self._check_player_permissions(player_id, game.player_ids)
        self._check_player_turn(player_id, game.cur_player_id)
        game.pass_turn()

    def both_players_passed(self, chat_id: int) -> bool:
        game = self._get_game_with_chat_id(chat_id)
        return game.both_players_passed

    def calculate_result(self, chat_id: int):
        raise NotImplementedError()

        game = self._get_game_with_chat_id(chat_id)
        return game.calculate_result()

    def cur_player_name(self, chat_id: int) -> str:
        game = self._get_game_with_chat_id(chat_id)
        return self.players[game.cur_player_id]

    def cur_player_color(self, chat_id: int) -> str:
        game = self._get_game_with_chat_id(chat_id)
        return game.cur_player_color

    def create_image(self, chat_id: int) -> JpegImageFile:
        game = self._get_game_with_chat_id(chat_id)
        return game.take_screenshot()

    def save_games(self) -> None:
        # TODO: export all games to file system
        pass

    def remove_game(self, chat_id: int) -> None:
        if chat_id in self.games:
            del self.games[chat_id]

    def _get_game_with_chat_id(self, chat_id: int) -> Game:
        self._check_chat_id(chat_id, self.games)
        return self.games[chat_id]

    @staticmethod
    def _check_player_turn(player: int, cur_player: int) -> None:
        if player != cur_player:
            proverb = "_{}_".format(random.choice(settings.patience_proverbs))
            message = "{}\n{}".format(proverb, settings.error_incorrect_turn)
            raise IncorrectTurnException(message)

    @staticmethod
    def _check_enough_players(game: Game) -> None:
        if len(game.player_ids) < 2:
            raise UnexpectedNumberOfPlayersException(settings.error_not_enough_players)

    @staticmethod
    def _check_player_limit(game: Game) -> None:
        if len(game.player_ids) == 2:
            raise UnexpectedNumberOfPlayersException(settings.error_already_enough_players)

    @staticmethod
    def _check_player_permissions(player: int, players: List[int]) -> None:
        if player not in players:
            raise NoPermissionsException(settings.error_permissions)

    @staticmethod
    def _check_chat_id(chat_id: int, games: Dict[int, Game]) -> None:
        if chat_id not in games:
            raise InexistentGameException(settings.error_inexistent_game)
