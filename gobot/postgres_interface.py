import os
import json
import psycopg2
from typing import List, Dict, Any, Tuple

from .go.go import GridPosition

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class Postgres:
    def __init__(self):
        self.use_db: bool = os.environ.get('MODE') != 'TEST'
        if not self.use_db:
            return

        self._conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        self._cur = self._conn.cursor()

    def new_game(self,
                 chat_id: int,
                 player1_id: int,
                 player2_id: int,
                 player1_name: str,
                 player2_name: str,
                 size_x: int,
                 size_y: int) -> None:
        if not self.use_db:
            return

        self._cur.execute(f"INSERT INTO players (id, name) "
                          f"VALUES ({player1_id}, '{player1_name}') "
                          f"ON CONFLICT (id) DO UPDATE SET name='{player1_name}';")
        self._cur.execute(f"INSERT INTO players (id, name) "
                          f"VALUES ({player2_id}, '{player2_name}') "
                          f"ON CONFLICT (id) DO UPDATE SET name='{player1_name}';")

        self._cur.execute(f"INSERT INTO games (chat_id, player1, player2, size_x, size_y, "
                          f"state, turn_color, turn_player, last_stone, player_passed)"
                          f"VALUES ({chat_id}, {player1_id}, {player2_id}, {size_x}, {size_y}, "
                          "'{}', 'black', "
                          f"'{player2_id}', '', 'False,False');")
        self._conn.commit()

    def delete_game(self, chat_id: int) -> None:
        if not self.use_db:
            return

        self._cur.execute(f"DELETE FROM games "
                          f"WHERE chat_id={chat_id};")
        self._conn.commit()

    def update_game(self,
                    chat_id: int,
                    cur_player: int,
                    cur_color: str,
                    player_passed: List[bool],
                    board: List[List[GridPosition]],
                    last_stone: Tuple[int, int]) -> None:
        if not self.use_db:
            return

        clean_state: Dict[str, str] = {}
        for x in range(len(board)):
            for y in range(len(board[x])):
                if not board[x][y].free:
                    clean_state[f"{x},{y}"] = board[x][y].color

        self._cur.execute(f"UPDATE games SET "
                          f"state='{json.dumps(clean_state)}', "
                          f"turn_color='{cur_color}', "
                          f"turn_player={cur_player}, "
                          f"last_stone='{last_stone[0]},{last_stone[1]}', "
                          f"player_passed='{player_passed[0]},{player_passed[1]}' "
                          f"WHERE chat_id='{chat_id}';")
        self._conn.commit()

    def load_game(self, chat_id: int) -> Dict[str, Any]:
        if not self.use_db:
            return {}

        self._cur.execute(f"SELECT * FROM games "
                          f"FULL OUTER JOIN players first ON first.id=games.player1 "
                          f"FULL OUTER JOIN players second ON second.id=games.player2 "
                          f"WHERE games.chat_id={chat_id};")

        rows = self._cur.fetchall()
        if not rows:
            return {}
        row = rows[0]

        game_state = {
            'player_ids': (row[1], row[2]),
            'size_x': row[3],
            'size_y': row[4],
            'board': row[5],
            'turn_color': row[6],
            'turn_player': row[7],
            'last_stone': row[8],
            'player_passed': row[9],
            'player1_name': row[10],
            'player2_name': row[11] if len(row) == 12 else row[10]
        }

        return game_state
