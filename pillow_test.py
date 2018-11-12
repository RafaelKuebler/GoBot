from PIL import Image,ImageDraw, ImageEnhance

BACKGROUND = 'images/ramin.jpg'
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

im = Image.open(BACKGROUND)

draw = ImageDraw.Draw(im)

for i in range(size_x):  # vertical
    draw.line(((startx+i*widthx, starty), (startx+i*widthx, starty+widthy*(size_y-1))), fill=BLACK, width=3)
for i in range(size_y):  # horizontal
    draw.line(((startx, starty + i * widthy), (startx + widthx * (size_x-1), starty + i * widthy)), fill=BLACK, width=3)

circle_positions = [(3, 3), (3, 7), (5, 5), (7, 3), (7, 7)]
circle_sizex = widthx/15
circle_sizey = widthy/15
for x, y in circle_positions:
    draw.ellipse(((startx+widthx*(x-1)-circle_sizex, starty+widthy*(y-1)-circle_sizey), (startx+widthx*(x-1)+circle_sizex, starty+widthy*(y-1)+circle_sizey)), fill=BLACK)

im.save('images/board.jpg')
#im.show()
