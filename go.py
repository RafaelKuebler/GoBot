from enum import Enum
import exceptions

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Color(Enum):
    WHITE = 0,
    BLACK = 1


class Stone:
    def __init__(self, x, y, color, board):
        self.coords = (x, y)
        self.color = color
        self.board = board
        self.board.stones[x][y] = self
        self.group = self.search_group()

        self.capture_neighbors()

    @property
    def neighbors(self):
        x, y = self.coords
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.board.size_x - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.board.size_y - 1:
            neighbors.append((x, y + 1))
        return neighbors

    @property
    def adjacent_groups(self):
        adjacent_groups = set()
        for x, y in self.neighbors:
            if self.board.stones[x][y] is not None:
                adjacent_groups.add(self.board.stones[x][y].group)
        return adjacent_groups

    def capture_neighbors(self):
        print('Searching for groups to capture...')
        for group in self.adjacent_groups:
            print(f'Adjacent group: {group}')
            print(f'  Liberties of group: {group.liberties}')
            if group.color != self.color and not group.liberties:
                print(f'Capturing group...')
                group.capture()

    @property
    def liberties(self):
        liberties = []
        for x, y in self.neighbors:
            if self.board.stones[x][y] is None:
                liberties.append((x, y))
        return liberties

    def capture(self):
        x, y = self.coords
        self.board.stones[x][y] = None

    def search_group(self):
        adjacent_groups = self.adjacent_groups
        group = Group(self.color)
        group.stones.add(self)
        for adj_group in adjacent_groups:
            if adj_group.color == self.color:
                print(f'Merging {group} with {adj_group}...')
                group.merge(adj_group)
        return group

    def __repr__(self):
        return f'({self.coords[0]},{self.coords[1]}, {self.color})'


class Group:
    def __init__(self, color):
        self.stones = set()
        self.color = color

    @property
    def liberties(self):
        liberties = []
        for stone in self.stones:
            liberties.extend(stone.liberties)
        return set(liberties)

    def merge(self, group):
        for stone in group.stones:
            stone.group = self
            self.stones.add(stone)

    def capture(self):
        for stone in self.stones:
            stone.capture()

    def __repr__(self):
        return f'({self.stones}, {self.color})'


class Board:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.stones = self._init_stones(self.size_x, self.size_y)

    @staticmethod
    def _init_stones(size_x, size_y):
        stones = []
        for _ in range(size_x):
            inner_stones = []
            for _ in range(size_y):
                inner_stones.append(None)
            stones.append(inner_stones)
        return stones


class GoGame:
    def __init__(self):
        self.cur_color = Color.BLACK
        self.board = Board(9, 9)

    def place_stone(self, coords):
        exceptions.sanitize_stone_coords(coords, self.board)
        x, y = self.transform_coords(coords)
        exceptions.sanitize_pos_taken(x, y, self.board)
        # TODO: "Ko" rule
        Stone(x, y, self.cur_color, self.board)
        self.change_turn()
        print(f'Changed turn to {self.cur_color}')

    def change_turn(self):
        if self.cur_color == Color.BLACK:
            self.cur_color = self.cur_color.WHITE
        else:
            self.cur_color = Color.BLACK

    @staticmethod
    def transform_coords(coords):
        letter = ord(coords[0]) - ord('a')
        number = int(coords[1]) - 1
        return letter, number
