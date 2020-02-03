from PIL import Image, ImageDraw
from vec2 import Vec2

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


dots = {
    '9': [(2, 2), (6, 2), (4, 4), (2, 6), (6, 6)],
    '13': [(3, 3), (9, 3), (6, 6), (3, 9), (9, 9)],
    '19': [(3, 3), (9, 3), (15, 3), (3, 9), (9, 9), (15, 9), (3, 15), (9, 15), (15, 15)],
}

size = 19
board_size = Vec2(size, size)
black = (0, 0, 0, 0)
line_width = 2
dot_size = 0.2

img: Image = Image.open('../../images/ramin.jpg')
draw: ImageDraw = ImageDraw.Draw(img)

background: Vec2 = Vec2(*img.size)
border_size: Vec2 = background * .125
line_length: Vec2 = background - border_size * 2
cell_width: Vec2 = line_length / (board_size - 1)
grid_start: Vec2 = background * .5 - line_length * .5

for x in range(board_size.x):
    x = grid_start.x + x*cell_width.x
    start = (x, grid_start.y)
    end = (x, grid_start.y+line_length.y)
    draw.line([start, end], fill=black, width=line_width)

for y in range(board_size.y):
    y = grid_start.y + y * cell_width.y
    start = (grid_start.x, y)
    end = (grid_start.x+line_length.x, y)
    draw.line([start, end], fill=black, width=line_width)

if str(board_size.x) in dots:
    for x, y in dots[str(board_size.x)]:
        start = grid_start + Vec2(x, y)*cell_width - cell_width*dot_size*0.5 + 1.25
        end = start + cell_width*dot_size
        draw.ellipse([(*start), (*end)], fill=black, width=line_width)

img.save('../../images/generated.jpg', "JPEG")
