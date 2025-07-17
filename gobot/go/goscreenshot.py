from PIL import Image, ImageDraw
from PIL.ImageFile import ImageFile

from gobot.go import strings
from gobot.go.go import GridPosition
from gobot.go.vec2 import Vec2


class GoScreenShot:
    def __init__(self, board_x: int, board_y: int) -> None:
        self.board_size: Vec2 = Vec2(board_x, board_y)
        self.color_map: dict[str, tuple[int, int, int, int]] = {"white": (255, 255, 255, 0), "black": (0, 0, 0, 0)}
        self.mark_color_map: dict[str, tuple[int, int, int, int]] = {"white": self.color_map["black"], "black": self.color_map["white"]}
        self.border_color_map = self.mark_color_map

    def _load_img(self) -> None:
        board_map = {9: strings.board_9_path, 13: strings.board_13_path, 19: strings.board_19_path}
        self.background_image: str = board_map[self.board_size.x]
        self.img = Image.open(self.background_image)
        self.draw = ImageDraw.Draw(self.img)

        self.background = Vec2(*self.img.size)
        self.border_size: Vec2 = self.background * 0.125
        self.cell_width: Vec2 = (self.background - self.border_size * 2) / (self.board_size - 1)
        self.grid_start: Vec2 = self.background * 0.5 - self.cell_width * (self.board_size - 1) * 0.5
        self.stone_size: Vec2 = self.cell_width * 0.9
        self.mark_size: Vec2 = self.stone_size * 0.5

    # TODO: create nice board graphic where indexing and board occupy space evenly
    def take_screenshot(self, board: list[list[GridPosition]], last_stone: tuple[int, int] | None) -> ImageFile:
        self._load_img()

        for x in range(self.board_size.x):
            for y in range(self.board_size.y):
                if board[x][y].free:
                    continue
                mark = (x, y) == last_stone
                draw_border = board[x][y].color == "white"
                self._draw_stone(x, y, board[x][y].color, mark, draw_border=draw_border)  # type:ignore

        return self.img

    def _draw_stone(self, x: int, y: int, color: str, marked: bool, draw_border: bool) -> None:
        coord: Vec2 = Vec2(x, y)
        color_value = self.color_map[color]
        stone_size = self.stone_size
        if draw_border:
            bb_start, bb_end = self._get_bb(coord, self.stone_size)
            self.draw.ellipse((*bb_start, *bb_end), fill=self.border_color_map[color])
            stone_size = self.stone_size * 0.85
        bb_start, bb_end = self._get_bb(coord, stone_size)
        self.draw.ellipse((*bb_start, *bb_end), fill=color_value)

        if marked:
            mark_color_value = self.mark_color_map[color]
            bb_start = self.grid_start + self.cell_width * coord - self.mark_size * 0.5
            bb_end = bb_start + self.mark_size
            self.draw.rectangle((*bb_start, *bb_end), outline=mark_color_value, width=3)

    def _get_bb(self, coord: Vec2, stone_size: Vec2):
        bb_start: Vec2 = self.grid_start + self.cell_width * coord - stone_size * 0.5
        bb_end: Vec2 = bb_start + stone_size
        return bb_start, bb_end
