#!/usr/bin/python
# coding: utf-8

from PIL import Image, ImageDraw
from .go import Color
from io import BytesIO
from . import settings
from gobot.utils.point import Point

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class GoScreenshot:
    def __init__(self, board_x, board_y):
        self.BACKGROUND = settings.board_path
        self.img = Image.open(self.BACKGROUND)
        self.draw = ImageDraw.Draw(self.img)

        self.WHITE = (255, 255, 255, 0)
        self.BLACK = (0, 0, 0, 0)
        self.background = Point(*self.img.size)
        self.board = Point(board_x, board_y)
        self.border = self.background * .125
        self.width = (self.background - self.border * 2) / (self.board - 1)
        self.start = self.background * .5 - self.width * (self.board - 1) * .5
        self.stone_size = self.width * .9
        self.mark_size = self.stone_size * .5

    # TODO: create nice board graphic where indexing and board occupy space evenly
    def take_screenshot(self, board):
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
        coords = Point(*stone.coords)
        color = self.WHITE if stone.color is Color.WHITE else self.BLACK
        bb_start = self.start + self.width * coords - self.stone_size * .5
        bb_end = bb_start + self.stone_size
        self.draw.ellipse((*bb_start, *bb_end), fill=color)

        if marked:
            color = self.BLACK if stone.color is Color.WHITE else self.WHITE
            bb_start = self.start + self.width * coords - self.mark_size * .5
            bb_end = bb_start + self.mark_size
            self.draw.rectangle((*bb_start, *bb_end), outline=color, width=3)
