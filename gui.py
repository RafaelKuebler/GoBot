from tkinter import *
from PIL import Image, ImageTk

import gobot.go.settings as settings

from gobot.go.go import GoGame
from gobot.go.goscreenshot import GoScreenShot
from gobot.go.exceptions import GoGameException

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

# TODO: Gui does only work with 9x9

root = Tk()
window = Canvas(root, width=500, height=500)
window.pack()

original = Image.open(settings.board_9_path)

game = GoGame(9, 9)
screenshot = GoScreenShot(game.size_x, game.size_y)

img = screenshot.take_screenshot(game.board, None)
img = img.resize((500, 500))
img = ImageTk.PhotoImage(img)
photo = window.create_image(0, 0, image=img, anchor="nw")

cell_width = 47
cols = 9


def _coords(pixel_x, pixel_y):
    x = int((pixel_x-63+cell_width/2)/374 * (cols-1))
    if not 0 <= x < cols:
        return None
    y = int((pixel_y-63+cell_width/2)/374 * (cols-1))
    if not 0 <= y < cols:
        return None
    return f"{chr(x + ord('a'))}{y+1}"


def _replace_image():
    global window, photo, img
    img = screenshot.take_screenshot(game.board, game.last_stone_placed)
    img = img.resize((500, 500))
    img = ImageTk.PhotoImage(img)
    window.itemconfig(photo, image=img)


def _left_click(event):
    x = event.x
    y = event.y
    coord = _coords(x, y)
    try:
        game.place_stone_str_coord(coord, "white")
    except GoGameException as exception:
        print(exception)
    _replace_image()


def _right_click(event):
    x = event.x
    y = event.y
    coord = _coords(x, y)
    try:
        game.place_stone_str_coord(coord, "black")
    except GoGameException as exception:
        print(exception)
    _replace_image()


window.bind("<Button-1>", _left_click)
window.bind("<Button-3>", _right_click)

root.mainloop()
