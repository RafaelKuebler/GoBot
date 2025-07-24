from io import BytesIO

from PIL import Image, ImageDraw
from PIL.ImageFile import ImageFile

from gobot.go import strings
from gobot.go.go import GoGame
from gobot.go.vec2 import Vec2

StoneRGBAColor = tuple[int, int, int, int]

board_map = {
    9: strings.board_9_path,
    13: strings.board_13_path,
    19: strings.board_19_path,
}
stone_colors: dict[str, StoneRGBAColor] = {
    "white": (255, 255, 255, 0),
    "black": (0, 0, 0, 0),
}
stone_border_colors: dict[str, StoneRGBAColor] = {
    "white": stone_colors["black"],
    "black": stone_colors["white"],
}


def take_in_memory_screenshot(go_game: GoGame) -> BytesIO:
    bytes_io = BytesIO()
    image = take_screenshot(go_game)
    image.save(bytes_io, "JPEG")
    bytes_io.seek(0)
    return bytes_io


def take_screenshot(go_game: GoGame) -> ImageFile:
    background_image: str = board_map[go_game.size_x]
    img = Image.open(background_image)
    draw = ImageDraw.Draw(img)

    background = Vec2(*img.size)
    border_size: Vec2 = background * 0.125
    cell_width: Vec2 = (background - border_size * 2) / (go_game.size_x - 1)
    grid_start: Vec2 = background * 0.5 - cell_width * (go_game.size_x - 1) * 0.5
    stone_size: Vec2 = cell_width * 0.9
    mark_size: Vec2 = stone_size * 0.5

    def _get_bounding_box(coord: Vec2, stone_size: Vec2):
        bb_start: Vec2 = grid_start + cell_width * coord - stone_size * 0.5
        bb_end: Vec2 = bb_start + stone_size
        return bb_start, bb_end

    for x in range(go_game.size_x):
        for y in range(go_game.size_y):
            if go_game.board[x][y].is_free:
                continue

            stone_color = stone_colors[go_game.board[x][y].color]  # type: ignore
            border_color = stone_border_colors[go_game.board[x][y].color]  # type: ignore

            coord: Vec2 = Vec2(x, y)
            # only draw black borders on white stones
            if go_game.board[x][y].color == "white":
                bb_start, bb_end = _get_bounding_box(coord, stone_size)
                draw.ellipse((*bb_start, *bb_end), fill=border_color)
                bb_start, bb_end = _get_bounding_box(coord, stone_size * 0.85)
            else:
                bb_start, bb_end = _get_bounding_box(coord, stone_size)
            draw.ellipse((*bb_start, *bb_end), fill=stone_color)

            if (x, y) == go_game.last_stone_placed:
                mark_color_value = border_color
                bb_start = grid_start + cell_width * coord - mark_size * 0.5
                bb_end = bb_start + mark_size
                draw.rectangle((*bb_start, *bb_end), outline=mark_color_value, width=3)

    return img
