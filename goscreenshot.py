from PIL import Image, ImageDraw
from go import Color
from io import BytesIO
import settings

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

BACKGROUND = settings.board_path
BOARD_SIZE = (820, 820)
WHITE = (255, 255, 255, 0)
BLACK = (0, 0, 0, 0)

boardx = 820
boardy = 820
size_x = 9
size_y = 9
borderx = 0.125 * boardx
bordery = 0.125 * boardy
widthx = (boardx-2*borderx)/(size_x-1)
widthy = (boardy-2*bordery)/(size_y-1)
startx = boardx/2-widthx*(size_x-1)/2
starty = boardy/2-widthy*(size_y-1)/2

stone_sizex = widthx*0.45
stone_sizey = widthy*0.45


def take_screenshot(stones):
    img = Image.open(BACKGROUND)
    draw = ImageDraw.Draw(img)
    for column in stones:
        for stone in column:
            draw_stone(draw, stone)
    bio = BytesIO()
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio


def draw_stone(draw, stone):
    if stone is None:
        return
    x, y = stone.coords
    color = WHITE if stone.color is Color.WHITE else BLACK
    bb_start = (startx+widthx*x-stone_sizex, starty+widthy*y-stone_sizey)
    bb_end = (startx+widthx*x+stone_sizex, starty+widthy*y+stone_sizey)
    draw.ellipse((bb_start, bb_end), fill=color)
