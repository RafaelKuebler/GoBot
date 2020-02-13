import os
from io import BytesIO
from PIL import Image, ImageDraw
from typing import List, Dict, Tuple, Optional, Any

from . import settings
from .go import GridPosition
from .vec2 import Vec2

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class GoScreenShot:
    def __init__(self, board_x: int, board_y: int) -> None:
        self.board_size: Vec2 = Vec2(board_x, board_y)
        self.color_map: Dict[str, Tuple[int, int, int, int]] = {
            "white": (255, 255, 255, 0),
            "black": (0, 0, 0, 0)
        }
        self.mark_color_map: Dict[str, Tuple[int, int, int, int]] = {
            "white": self.color_map["black"],
            "black": self.color_map["white"]
        }
        self.border_color_map = self.mark_color_map

    def _load_img(self) -> None:
        board_map = {
            9: settings.board_9_path,
            13: settings.board_13_path,
            19: settings.board_19_path
        }
        self.background_image: str = board_map[self.board_size.x]
        self.img: Image = Image.open(self.background_image)
        self.draw: ImageDraw = ImageDraw.Draw(self.img)

        self.background: Vec2 = Vec2(*self.img.size)
        self.border_size: Vec2 = self.background * .125
        self.cell_width: Vec2 = (self.background - self.border_size * 2) / (self.board_size - 1)
        self.grid_start: Vec2 = self.background * .5 - self.cell_width * (self.board_size - 1) * .5
        self.stone_size: Vec2 = self.cell_width * .9
        self.mark_size: Vec2 = self.stone_size * .5

    # TODO: create nice board graphic where indexing and board occupy space evenly
    def take_screenshot(self, board: List[List[GridPosition]],
                        last_stone: Optional[Tuple[int, int]]) -> Any:
        self._load_img()

        for x in range(self.board_size.x):
            for y in range(self.board_size.y):
                if board[x][y].free:
                    continue
                mark = (x, y) == last_stone
                draw_border = board[x][y].color == "white"
                self._draw_stone(x, y, board[x][y].color, mark, draw_border=draw_border)

        if os.environ["MODE"] != "GUI":
            bio = BytesIO()
            self.img.save(bio, settings.image_extension)
            bio.seek(0)
            return bio

        return self.img

    def _draw_stone(self, x: int, y: int, color: str, marked: bool, draw_border: bool) -> None:
        coord: Vec2 = Vec2(x, y)
        color_value = self.color_map[color]
        stone_size = self.stone_size
        if draw_border:
            bb_start, bb_end = self._get_bb(coord, self.stone_size)
            self.draw.ellipse((*bb_start, *bb_end), fill=self.border_color_map[color])
            stone_size = self.stone_size * .85
        bb_start, bb_end = self._get_bb(coord, stone_size)
        self.draw.ellipse((*bb_start, *bb_end), fill=color_value)

        if marked:
            mark_color_value = self.mark_color_map[color]
            bb_start = self.grid_start + self.cell_width * coord - self.mark_size * .5
            bb_end = bb_start + self.mark_size
            self.draw.rectangle((*bb_start, *bb_end), outline=mark_color_value, width=3)

    def _get_bb(self, coord: Vec2, stone_size: Vec2):
        bb_start: Vec2 = self.grid_start + self.cell_width * coord - stone_size * .5
        bb_end: Vec2 = bb_start + stone_size
        return bb_start, bb_end
