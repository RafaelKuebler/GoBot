#!/usr/bin/python
# coding: utf-8

from PIL import Image, ImageDraw
from .go import Color
from io import BytesIO
import settings

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

BACKGROUND = settings.board_path
WHITE = (255, 255, 255, 0)
BLACK = (0, 0, 0, 0)

board_x = 820
board_y = 820
size_x = 9
size_y = 9
border_x = .125 * board_x
border_y = .125 * board_y
width_x = (board_x - 2 * border_x) / (size_x - 1)
width_y = (board_y - 2 * border_y) / (size_y - 1)
start_x = board_x * .5 - width_x * (size_x - 1) * .5
start_y = board_y * .5 - width_y * (size_y - 1) * .5

stone_size_x = width_x * .9
stone_size_y = width_y * .9


# TODO: create nice board graphic where indexing and board occupy space evenly
def take_screenshot(board):
    img = Image.open(BACKGROUND)
    draw = ImageDraw.Draw(img)
    for column in board.stones:
        for stone in column:
            draw_stone(draw, stone, stone == board.last_stone_placed)
    bio = BytesIO()
    img.save(bio, settings.image_extension)
    bio.seek(0)
    return bio


def draw_stone(draw, stone, marked):
    if stone is None:
        return
    x, y = stone.coords
    color = WHITE if stone.color is Color.WHITE else BLACK
    bb_start = calc_upper_left_corner(x, y, stone_size_x, stone_size_y)
    bb_end = calc_lower_right_corner(bb_start, stone_size_x, stone_size_y)
    draw.ellipse((bb_start, bb_end), fill=color)

    if marked:
        color = BLACK if stone.color is Color.WHITE else WHITE
        bb_start = calc_upper_left_corner(x, y, stone_size_x*.5, stone_size_y*.5)
        bb_end = calc_lower_right_corner(bb_start, stone_size_x*.5, stone_size_y*.5)
        draw.rectangle((bb_start, bb_end), outline=color, width=3)


def calc_upper_left_corner(x, y, element_width_x, element_width_y):
    bb_start_x = start_x + width_x * x - element_width_x*.5
    bb_start_y = start_y + width_y * y - element_width_y*.5
    return bb_start_x, bb_start_y


def calc_lower_right_corner(upper_left_corner, element_width_x, element_width_y):
    bb_start_x, bb_start_y = upper_left_corner
    return bb_start_x + element_width_x, bb_start_y + element_width_y
