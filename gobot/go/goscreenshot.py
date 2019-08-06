import os
from io import BytesIO
from PIL import Image, ImageDraw
from typing import List, Dict, Tuple

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
        self.reverse_color_map: Dict[str, Tuple[int, int, int, int]] = {
            "white": (0, 0, 0, 0),
            "black": (255, 255, 255, 0)
        }

    def _load_img(self) -> None:
        self.BACKGROUND: str = settings.board_path
        self.img: Image = Image.open(self.BACKGROUND)
        self.draw: ImageDraw = ImageDraw.Draw(self.img)

        self.background: Vec2 = Vec2(*self.img.size)
        self.border_size: Vec2 = self.background * .125
        self.cell_width: Vec2 = (self.background - self.border_size * 2) / (self.board_size - 1)
        self.grid_start: Vec2 = self.background * .5 - self.cell_width * (self.board_size - 1) * .5
        self.stone_size: Vec2 = self.cell_width * .9
        self.mark_size: Vec2 = self.stone_size * .5

    # TODO: create nice board graphic where indexing and board occupy space evenly
    def take_screenshot(self, board: List[List[GridPosition]],
                        last_stone: Tuple[int, int]):
        # TODO: return type
        self._load_img()

        for x in range(self.board_size.x):
            for y in range(self.board_size.y):
                if board[x][y].free:
                    continue
                mark: bool = (x, y) == last_stone
                self._draw_stone(x, y, board[x][y].color, mark)

        if os.environ.get('GUI', "0") == "0":
            bio = BytesIO()
            self.img.save(bio, settings.image_extension)
            bio.seek(0)
            return bio

        return self.img

    def _draw_stone(self, x: int, y: int, color: str, marked: bool) -> None:
        coord: Vec2 = Vec2(x, y)
        color_value = self.color_map[color]
        bb_start: Vec2 = self.grid_start + self.cell_width * coord - self.stone_size * .5
        bb_end: Vec2 = bb_start + self.stone_size
        self.draw.ellipse((*bb_start, *bb_end), fill=color_value)

        if marked:
            mark_color_value = self.reverse_color_map[color]
            bb_start = self.grid_start + self.cell_width * coord - self.mark_size * .5
            bb_end = bb_start + self.mark_size
            self.draw.rectangle((*bb_start, *bb_end), outline=mark_color_value, width=3)
