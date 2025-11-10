import random
from typing import Literal, overload

from gobot.persistence import persistence_factory
from gobot.telegram import proverbs
from gobot.telegram.telegram_go_game import TelegramGoGame


class GameHandlerException(Exception):
    pass


class GameHandler:
    def __init__(self) -> None:
        self.DB = persistence_factory.get_db_adapter()

    @overload
    def get_game_with_chat_id(self, chat_id: int, raise_if_not_found: Literal[True]) -> TelegramGoGame: ...
    @overload
    def get_game_with_chat_id(self, chat_id: int, raise_if_not_found: Literal[False] = False) -> TelegramGoGame | None: ...
    def get_game_with_chat_id(self, chat_id: int, raise_if_not_found: bool = False):
        if (game := self.DB.load_game(chat_id)) is None and raise_if_not_found:
            raise GameHandlerException("Please start a game with /new first!")
        return game

    def new_game(self, chat_id: int, player_id: int, player_name: str, board_size: int = 9) -> TelegramGoGame:
        old_game = self.get_game_with_chat_id(chat_id)
        if old_game is not None:
            check_if_participating_player(player_id, old_game)

        if board_size not in (9, 13, 19):
            raise GameHandlerException("The board size has to be 9, 13 or 19!")

        new_game = TelegramGoGame(
            chat_id=chat_id,
            board_x=board_size,
            board_y=board_size,
        )
        new_game.add_player(player_id, player_name)
        self.DB.new_game(new_game)
        return new_game

    def join(self, chat_id: int, player_id: int, player_name: str) -> TelegramGoGame:
        game = self.get_game_with_chat_id(chat_id, raise_if_not_found=True)
        if game.has_enough_players():
            raise GameHandlerException("The game already has 2 players!")

        game.add_player(player_id, player_name)
        self.DB.update_game(game)
        return game

    def place_stone(self, chat_id: int, player_id: int, coord: str) -> TelegramGoGame:
        game = self.get_game_with_chat_id(chat_id, raise_if_not_found=True)
        check_if_enough_players(game)
        check_if_participating_player(player_id, game)
        check_if_player_turn(player_id, game)

        game.place_stone_str_coord(coord)
        self.DB.update_game(game)
        return game

    def pass_turn(self, chat_id: int, player_id: int) -> TelegramGoGame:
        game = self.get_game_with_chat_id(chat_id, raise_if_not_found=True)
        check_if_enough_players(game)
        check_if_participating_player(player_id, game)
        check_if_player_turn(player_id, game)

        game.pass_turn()
        self.DB.update_game(game)
        return game

    def calculate_result(self, chat_id: int):
        # TODO
        raise NotImplementedError()
        game = self._get_game_with_chat_id(chat_id)
        return game.calculate_result()

    def remove_game(self, chat_id: int) -> None:
        self.DB.delete_game(chat_id)


def check_if_participating_player(player_id: int, game: TelegramGoGame) -> None:
    if player_id not in [player.id_ for player in game.players]:
        raise GameHandlerException("You are not part of a current game and therefore not allowed to perform this action!")


def check_if_player_turn(player_id: int, game: TelegramGoGame) -> None:
    if not game.current_player:
        raise GameHandlerException("The game has no players yet! Join the game with /join")
    if player_id != game.current_player.id_:
        message = f"{random.choice(proverbs.patience_proverbs)}\nIt is not your turn!"
        raise GameHandlerException(message)


def check_if_enough_players(game: TelegramGoGame) -> None:
    if not game.has_enough_players():
        raise GameHandlerException("Another player needs to join the game with /join!")
