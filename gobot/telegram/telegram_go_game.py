from io import BytesIO
from typing import Literal, override

from gobot.go.go import GoGame
from gobot.go.goscreenshot import GoScreenShot


class TelegramGoGame(GoGame):
    def __init__(self, chat_id: int, board_x: int, board_y: int) -> None:
        super().__init__(board_x, board_y)
        self.chat_id = chat_id
        self.player_ids: list[int | None] = [None, None]
        self.player_names: list[str | None] = []
        self.cur_player_id: int | None = None
        self.cur_player_color: Literal["white", "black"] = "black"
        self.player_passed: list[bool] = [False, False]
        self.screenshot: GoScreenShot = GoScreenShot(board_x, board_y)

    @property
    def both_players_passed(self) -> bool:
        if not self.player_passed:
            return False
        return all(self.player_passed)

    @property
    def cur_player_name(self) -> str | None:
        if self.cur_player_id is None:
            return None
        return self.player_names[self.player_ids.index(self.cur_player_id)]

    def add_player(self, player_id: int) -> None:
        self.player_ids.append(player_id)
        self.cur_player_id = player_id
        self.player_passed.append(False)

    @override
    def place_stone_str_coord(self, coord: str, color: str | None = None) -> None:
        super().place_stone_str_coord(coord, self.cur_player_color)
        del self.player_passed[0]
        self.player_passed.append(False)
        self._change_turn()

    def pass_turn(self) -> None:
        del self.player_passed[0]
        self.player_passed.append(True)
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

    def has_enough_players(self) -> bool:
        return len(self.player_ids) == 2

    def take_screenshot(self) -> BytesIO:
        image = self.screenshot.take_screenshot(self.board, self.last_stone_placed)

        bio = BytesIO()
        image.save(bio, "JPEG")
        bio.seek(0)
        return bio
