import tkinter as tk
from tkinter.messagebox import showerror

from PIL import Image, ImageTk

import gobot.go.strings as strings
from gobot.go.exceptions import GoGameException
from gobot.go.go import GoGame
from gobot.go.goscreenshot import GoScreenShot

# TODO: GUI does only work with 9x9

root = tk.Tk()
window = tk.Canvas(root, width=500, height=500)
window.pack()

original = Image.open(strings.board_9_path)

game = GoGame(9, 9)
screenshot = GoScreenShot(game.size_x, game.size_y)

img = screenshot.take_screenshot(game.board, None)
img = img.resize((500, 500))
img = ImageTk.PhotoImage(img)
photo = window.create_image(0, 0, image=img, anchor="nw")

cell_width = 47
cols = 9


def get_coords(pixel_x, pixel_y):
    x = int((pixel_x - 63 + cell_width / 2) / 374 * (cols - 1))
    if not 0 <= x < cols:
        return None
    y = int((pixel_y - 63 + cell_width / 2) / 374 * (cols - 1))
    if not 0 <= y < cols:
        return None
    return f"{chr(x + ord('a'))}{y + 1}"


def replace_image():
    global window, photo, img
    img = screenshot.take_screenshot(game.board, game.last_stone_placed)
    img = img.resize((500, 500))
    img = ImageTk.PhotoImage(img)
    window.itemconfig(photo, image=img)


def left_click(event):
    print("Left click!")
    handle_click(event, "white")


def right_click(event):
    print("Right click!")
    handle_click(event, "black")


def handle_click(event, color: str):
    x = event.x
    y = event.y
    coord = get_coords(x, y)
    if coord is None:
        return
    try:
        game.place_stone_str_coord(coord, color)
    except GoGameException as exception:
        showerror("Error", str(exception))
        print(exception)
    replace_image()


window.bind("<Button-1>", left_click)
window.bind("<Button-2>", right_click)
window.bind("<Button-3>", right_click)

root.mainloop()
