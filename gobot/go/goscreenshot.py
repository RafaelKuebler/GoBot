#!/usr/bin/python
# coding: utf-8

from PIL import Image, ImageDraw
from .go import Color
from io import BytesIO
from . import settings

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class GoScreenshot:
    def __init__(self, board_x, board_y):
        self.BACKGROUND = settings.board_path
        self.img = Image.open(self.BACKGROUND)
        self.draw = ImageDraw.Draw(self.img)

        self.WHITE = (255, 255, 255, 0)
        self.BLACK = (0, 0, 0, 0)
        self.background_x, self.background_y = self.img.size
        self.board_x = board_x
        self.board_y = board_y
        self.border_x = .125 * self.background_x
        self.border_y = .125 * self.background_y
        self.width_x = self._calculate_cell_width(self.background_x, self.border_x, self.board_x)
        self.width_y = self._calculate_cell_width(self.background_y, self.border_y, self.board_y)
        self.start_x = self._calculate_start(self.background_x, self.width_x, self.board_x)
        self.start_y = self._calculate_start(self.background_y, self.width_y, self.board_y)

        self.stone_size_x = self.width_x * .9
        self.stone_size_y = self.width_y * .9

    @staticmethod
    def _calculate_cell_width(background, border, board):
        return (background - 2 * border) / (board - 1)

    @staticmethod
    def _calculate_start(background, width, board):
        return background * .5 - width * (board - 1) * .5

    # TODO: create nice board graphic where indexing and board occupy space evenly
    def take_screenshot(self, board):
        for column in board.stones:
            for stone in column:
                self._draw_stone(stone, stone == board.last_stone_placed)
        bio = BytesIO()
        self.img.save(bio, settings.image_extension)
        bio.seek(0)
        return bio

    def _draw_stone(self, stone, marked):
        if stone is None:
            return
        x, y = stone.coords
        color = self.WHITE if stone.color is Color.WHITE else self.BLACK
        bb_start = self._calc_upper_left_corner(x, y, self.stone_size_x, self.stone_size_y)
        bb_end = self._calc_lower_right_corner(bb_start, self.stone_size_x, self.stone_size_y)
        self.draw.ellipse((bb_start, bb_end), fill=color)

        if marked:
            color = self.BLACK if stone.color is Color.WHITE else self.WHITE
            bb_start = self._calc_upper_left_corner(x, y, self.stone_size_x * .5, self.stone_size_y * .5)
            bb_end = self._calc_lower_right_corner(bb_start, self.stone_size_x * .5, self.stone_size_y * .5)
            self.draw.rectangle((bb_start, bb_end), outline=color, width=3)

    def _calc_upper_left_corner(self, x, y, element_width_x, element_width_y):
        bb_start_x = self.start_x + self.width_x * x - element_width_x*.5
        bb_start_y = self.start_y + self.width_y * y - element_width_y*.5
        return bb_start_x, bb_start_y

    def _calc_lower_right_corner(self, upper_left_corner, element_width_x, element_width_y):
        bb_start_x, bb_start_y = upper_left_corner
        return bb_start_x + element_width_x, bb_start_y + element_width_y
