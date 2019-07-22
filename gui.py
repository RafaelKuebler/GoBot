from tkinter import *
from PIL import Image, ImageTk

from gobot.go.go import GoGame
from gobot.go.goscreenshot import GoScreenShot

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


root = Tk()
w = Canvas(root, width=500, height=500)
w.pack()

original = Image.open('images/board.jpg')

game = GoGame()
screenshot = GoScreenShot(game.size_x, game.size_y)

img = screenshot.take_screenshot(game.board, None)
img = img.resize((500, 500))
img = ImageTk.PhotoImage(img)
photo = w.create_image(0, 0, image=img, anchor="nw")

cell_width = 47
cols = 9


def coords(pixel_x, pixel_y):
    x = int((pixel_x-63+cell_width/2)/374 * (cols-1))
    if not 0 <= x < cols:
        return None
    y = int((pixel_y-63+cell_width/2)/374 * (cols-1))
    if not 0 <= y < cols:
        return None
    return f"{chr(x + ord('a'))}{y+1}"


def replace_image():
    global w, photo, img
    img = screenshot.take_screenshot(game.board, game.last_stone_placed)
    img = img.resize((500, 500))
    img = ImageTk.PhotoImage(img)
    w.itemconfig(photo, image=img)


def left_click(event):
    x = event.x
    y = event.y
    coord = coords(x, y)
    game.place_stone(coord, "white")
    replace_image()


def right_click(event):
    x = event.x
    y = event.y
    coord = coords(x, y)
    game.place_stone(coord, "black")
    replace_image()


w.bind("<Button-1>", left_click)
w.bind("<Button-3>", right_click)

root.mainloop()
