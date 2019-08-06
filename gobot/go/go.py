from typing import List, Dict, Set, Tuple, Optional

from . import settings
from .exceptions import *

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

REVERSE: Dict[str, str] = {
    "white": "black",
    "black": "white"
}


class GridPosition:
    def __init__(self) -> None:
        self.group: Set[Tuple[int, int]] = set()
        self.color: Optional[str] = None

    @property
    def free(self) -> bool:
        return self.color is None

    def clear(self) -> None:
        self.group = set()
        self.color = None


class GoGame:
    def __init__(self, size_x: int = 9, size_y: int = 9) -> None:
        self.size_x: int = size_x
        self.size_y: int = size_y
        self.board: List[List[GridPosition]] = []
        self.last_stone_placed: Optional[Tuple[int, int]] = None

        self._check_board_size(size_x, size_y)
        self._create_board()
        self._last_captured_single_stone: Optional[Tuple[int, int]] = None
        # TODO: persist last captured stone for ko check

    def _create_board(self) -> None:
        for x in range(self.size_x):
            column: List[GridPosition] = []
            for y in range(self.size_y):
                column.append(GridPosition())
            self.board.append(column)

    def place_stone_str_coord(self, coord: str, color: str) -> None:
        self._check_stone_str_coord(coord)
        x, y = self._transform_coord(coord)
        self.place_stone(x, y, color)

    def place_stone(self, x: int, y: int, color: str) -> None:
        self._check_stone_coord(x, y)
        self._check_pos_taken(x, y)

        adjacent_groups = self._detect_adjacent_groups(x, y, color)
        own_group = {item for groups in adjacent_groups
                     for item in groups}  # flatten
        own_group.add((x, y))
        adjacent_opponent_groups = self._detect_adjacent_groups(x, y, REVERSE[color])
        opponent_groups_atari = [group for group in adjacent_opponent_groups
                                 if len(self._group_liberties(group)) == 1]

        self._check_ko(opponent_groups_atari)
        self._check_self_capture((x, y), own_group, opponent_groups_atari)

        self._capture_neighbors(opponent_groups_atari)
        self._merge_groups(own_group, color)
        self.last_stone_placed = (x, y)

    def _capture_neighbors(self, opponent_groups: List[Set[Tuple[int, int]]]) -> None:
        if len(opponent_groups) == 1 and len(opponent_groups[0]) == 1:
            self._last_captured_single_stone = list(opponent_groups[0])[0]

        for group in opponent_groups:
            for x, y in group.copy():
                self.board[x][y].group.remove((x, y))  # remove stone from the group
                self.board[x][y].clear()  # clear board position

    def _merge_groups(self, new_group: Set[Tuple[int, int]], color: str) -> None:
        for x, y in new_group:
            self.board[x][y].group = new_group
            self.board[x][y].color = color

    def _group_liberties(self, group: Set[Tuple[int, int]])\
            -> Set[Tuple[int, int]]:
        group_liberties: Set[Tuple[int, int]] = set()
        for stone in group:
            stone_liberties = {(x, y) for x, y in self._neighbors_of(*stone)
                               if self.board[x][y].free}
            group_liberties = group_liberties.union(stone_liberties)
        return group_liberties

    def _detect_adjacent_groups(self, x: int, y: int, color: str)\
            -> List[Set[Tuple[int, int]]]:
        return [self.board[x][y].group
                for x, y in self._neighbors_of(x, y, color)]

    def _neighbors_of(self, x: int, y: int, color: Optional[str] = None)\
            -> List[Tuple[int, int]]:
        neighbors: List[Tuple[int, int]] = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.size_x - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.size_y - 1:
            neighbors.append((x, y + 1))

        if color is not None:
            neighbors = [(x, y) for x, y in neighbors
                         if self.board[x][y].color == color]
        return neighbors

    @staticmethod
    def _transform_coord(coord: str) -> Tuple[int, int]:
        # TODO: implement notation as in https://senseis.xmp.net/?Coordinates
        letter = ord(coord[0]) - ord('a')
        number = int(coord[1:]) - 1
        return letter, number

    @staticmethod
    def _check_board_size(size_x: int, size_y: int) -> None:
        if (size_x, size_y) not in [(9, 9), (13, 13), (19, 19)]:
            raise InvalidBoardSizeException(settings.error_invalid_size)

    @staticmethod
    def _check_stone_str_coord(coord: str) -> None:
        has_letter = ord('a') <= ord(coord[0]) < ord('z')
        has_digit = coord[1:].isdigit()
        if not has_letter or not has_digit:
            raise InvalidCoordinateException(settings.error_invalid_coords)

    def _check_stone_coord(self, x: int, y: int) -> None:
        x_in_range: bool = 0 <= x < self.size_x
        y_in_range: bool = 0 <= y < self.size_y
        if not x_in_range or not y_in_range:
            raise InvalidCoordinateException(settings.error_invalid_coords)

    def _check_pos_taken(self, x: int, y: int) -> None:
        if not self.board[x][y].free:
            raise CoordOccupiedException(settings.error_coord_occupied)

    def _check_ko(self, opponent_groups: List[Set[Tuple[int, int]]]) -> None:
        """
        Conditions:
        - Last round exactly one stone was captured
        - The newly placed stone would capture exactly one stone
        - The stone that would be captured is the last placed stone
        """

        if self._last_captured_single_stone is None:
            return

        single_threatened_neighbor: Optional[Tuple[int, int]] = None
        for group in opponent_groups:
            group_liberties = len(self._group_liberties(group))
            if group_liberties == 1 and len(group) == 1:
                more_than_one_target = single_threatened_neighbor is not None
                if more_than_one_target:
                    return
                single_threatened_neighbor = list(group)[0]

        if self.last_stone_placed == single_threatened_neighbor:
            raise KoException(settings.error_ko)

    def _check_self_capture(self, stone: Tuple[int, int],
                            group: Set[Tuple[int, int]],
                            opponent_groups: List[Set[Tuple[int, int]]])\
            -> None:
        if opponent_groups:
            return

        group_liberties = self._group_liberties(group)
        if stone in group_liberties:
            group_liberties.remove(stone)
        if not group_liberties:
            raise SelfCaptureException(settings.error_self_capture)
