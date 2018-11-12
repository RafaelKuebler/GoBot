from PIL import Image, ImageDraw
from go import Color

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

BACKGROUND = 'images/board.jpg'
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


def take_screenshot(board):
    im = Image.open(BACKGROUND)
    draw = ImageDraw.Draw(im)
    for row in board.stones:
        for stone in row:
            draw_stone(draw, stone)
    # im.save('images/board.jpg')
    return im


def draw_stone(draw, stone):
    if stone is None:
        return
    x, y = stone.coords
    color = WHITE if stone.color == Color.White else BLACK
    bb_start = (startx+widthx*(x-1)-stone_sizex, starty+widthy*(y-1)-stone_sizey)
    bb_end = (startx+widthx*(x-1)+stone_sizex, starty+widthy*(y-1)+stone_sizey)
    draw.ellipse((bb_start, bb_end), fill=color)


"""
for i in range(size_x):  # vertical
    draw.line(((startx+i*widthx, starty), (startx+i*widthx, starty+widthy*(size_y-1))), fill=BLACK, width=3)
for i in range(size_y):  # horizontal
    draw.line(((startx, starty + i * widthy), (startx + widthx * (size_x-1), starty + i * widthy)), fill=BLACK, width=3)

circle_positions = [(3, 3), (3, 7), (5, 5), (7, 3), (7, 7)]
circle_sizex = widthx/15
circle_sizey = widthy/15
for x, y in circle_positions:
    draw.ellipse(((startx+widthx*(x-1)-circle_sizex, starty+widthy*(y-1)-circle_sizey), (startx+widthx*(x-1)+circle_sizex, starty+widthy*(y-1)+circle_sizey)), fill=BLACK)
"""


