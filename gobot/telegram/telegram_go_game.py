import pprint
from typing import override

from gobot.go.go import GoGame
from gobot.telegram.player import Player
from gobot.telegram.player_color import PlayerColor


class TelegramGoGame(GoGame):
    def __init__(self, chat_id: int, board_x: int, board_y: int) -> None:
        super().__init__(board_x, board_y)
        self.chat_id = chat_id
        self.players: list[Player] = []
        self.current_player_index: int = 0

    @property
    def is_game_over(self) -> bool:
        """The game is over when both players have passed"""
        return all(player.did_pass for player in self.players)

    @property
    def current_player(self) -> Player | None:
        if not self.players:
            return None
        return self.players[self.current_player_index]

    def add_player(self, player_id: int, player_name: str) -> None:
        is_first_player = not self.players
        color = PlayerColor.WHITE if is_first_player else PlayerColor.BLACK
        self.players.append(Player(player_id, player_name, color))
        self.current_player_index = len(self.players) - 1

    @override
    def place_stone_str_coord(self, coord: str, color: str | None = None) -> None:
        assert self.current_player
        super().place_stone_str_coord(coord, self.current_player.color)
        self.current_player.did_pass = False
        self._change_turn()

    def pass_turn(self) -> None:
        assert self.current_player
        self.current_player.did_pass = True
        self._change_turn()

    def _change_turn(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % 2

    def has_enough_players(self) -> bool:
        return len(self.players) == 2

    def __str__(self):
        return pprint.pformat(
            {
                "Chat ID": self.chat_id,
                "Players": self.players,
                "Curr player": self.current_player,
            }
        )
