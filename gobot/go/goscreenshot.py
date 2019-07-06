from PIL import Image, ImageDraw
from io import BytesIO

from .go import Color
from . import settings
from .point import Point

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

WHITE = (255, 255, 255, 0)
BLACK = (0, 0, 0, 0)


class GoScreenShot:
    def __init__(self, board_x, board_y):
        self.board_size = Point(board_x, board_y)

    def _load_img(self):
        self.BACKGROUND = settings.board_path
        self.img = Image.open(self.BACKGROUND)
        self.draw = ImageDraw.Draw(self.img)

        self.background = Point(*self.img.size)
        self.border_size = self.background * .125
        self.cell_width = (self.background - self.border_size * 2) / (self.board_size - 1)
        self.grid_start = self.background * .5 - self.cell_width * (self.board_size - 1) * .5
        self.stone_size = self.cell_width * .9
        self.mark_size = self.stone_size * .5

    # TODO: create nice board graphic where indexing and board occupy space evenly
    def take_screenshot(self, board):
        self._load_img()

        for column in board.stones:
            for stone in column:
                mark = (stone == board.last_stone_placed)
                self._draw_stone(stone, mark)
        bio = BytesIO()
        self.img.save(bio, settings.image_extension)
        bio.seek(0)
        return bio

    def _draw_stone(self, stone, marked):
        if stone is None:
            return
        coord = Point(*stone.coord)
        color = WHITE if stone.color is Color.WHITE else BLACK
        bb_start = self.grid_start + self.cell_width * coord - self.stone_size * .5
        bb_end = bb_start + self.stone_size
        self.draw.ellipse((*bb_start, *bb_end), fill=color)

        if marked:
            color = BLACK if stone.color is Color.WHITE else WHITE
            bb_start = self.grid_start + self.cell_width * coord - self.mark_size * .5
            bb_end = bb_start + self.mark_size
            self.draw.rectangle((*bb_start, *bb_end), outline=color, width=3)
