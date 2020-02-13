import os
import json
import logging
import psycopg2
from typing import List, Dict, Tuple, Optional, NamedTuple
from pypika import PostgreSQLQuery, Table, Tables

from .go.go import GridPosition

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class GameState(NamedTuple):
    player_ids: Tuple[int, int]
    size_x: int
    size_y: int
    board: Dict[str, str]
    turn_color: str
    turn_player: int
    last_stone: str
    last_capt_stone: str
    player_passed: str
    player1_name: str
    player2_name: str


class Postgres:
    def __init__(self):
        self.use_db: bool = os.environ.get('DB', '1') == '1'
        if not self.use_db:
            logging.info("Not using DB")
            return

        # TODO: make db connection more flexible (no need for code change for local testing)
        self._conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        logging.info("Established connection to DB")
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

        games, players = Tables('games', 'players')
        logging.info(f"Creating new game {chat_id} in DB")
        player1_query = PostgreSQLQuery.into(players) \
            .insert(player1_id, player1_name) \
            .on_conflict(players.id).do_update(players.name, player1_name)
        player2_query = PostgreSQLQuery.into(players) \
            .insert(player2_id, player2_name) \
            .on_conflict(players.id).do_update(players.name, player2_name)

        new_game_query = PostgreSQLQuery.into(games) \
            .insert(chat_id, player1_id, player2_id,
                    size_x, size_y, '{}', 'black',
                    player2_id, '', '', 'False,False')

        self._cur.execute(player1_query.get_sql())
        self._cur.execute(player2_query.get_sql())
        self._cur.execute(new_game_query.get_sql())
        self._conn.commit()

    def delete_game(self, chat_id: int) -> None:
        if not self.use_db:
            return

        games = Table('games')
        logging.info(f"Removing game {chat_id} from DB")
        delete_game_query = PostgreSQLQuery.from_(games) \
            .delete() \
            .where(games.chat_id == chat_id)
        self._cur.execute(delete_game_query.get_sql())
        self._conn.commit()

    def update_game(self,
                    chat_id: int,
                    cur_player: int,
                    cur_color: str,
                    player_passed: List[bool],
                    board: List[List[GridPosition]],
                    last_placed_stone: Tuple[int, int],
                    last_capt_stone: Optional[Tuple[int, int]]) -> None:
        if not self.use_db:
            return

        clean_state: Dict[str, str] = {}
        for x in range(len(board)):
            for y in range(len(board[x])):
                if not board[x][y].free:
                    clean_state[f"{x},{y}"] = board[x][y].color

        last_capt_stone_str = ""
        if last_capt_stone is not None:
            last_capt_stone_str = f"{last_capt_stone[0]},{last_capt_stone[1]}"

        games = Table('games')
        update_game_query = PostgreSQLQuery.update(games) \
            .set(games.state, json.dumps(clean_state)) \
            .set(games.turn_color, cur_color) \
            .set(games.turn_player, cur_player) \
            .set(games.last_stone, f'{last_placed_stone[0]},{last_placed_stone[1]}') \
            .set(games.last_capt_stone, last_capt_stone_str) \
            .set(games.player_passed, f'{player_passed[0]},{player_passed[1]}') \
            .where(games.chat_id == chat_id)
        self._cur.execute(update_game_query.get_sql())
        self._conn.commit()

    def load_game(self, chat_id: int) -> Optional[GameState]:
        if not self.use_db:
            return None

        games, players = Tables('games', 'players')
        logging.info(f"Loading game {chat_id} from DB")
        load_game_query = PostgreSQLQuery.from_(games) \
            .select(games.player1,
                    games.player2,
                    games.size_x,
                    games.size_y,
                    games.state,
                    games.turn_color,
                    games.turn_player,
                    games.last_stone,
                    games.last_capt_stone,
                    games.player_passed) \
            .where(games.chat_id == chat_id)
        self._cur.execute(load_game_query.get_sql())

        rows = self._cur.fetchall()
        if not rows:
            logging.info(f"Game {chat_id} not fround in DB")
            return None
        row = rows[0]

        get_player1_query = PostgreSQLQuery.from_(players) \
            .select(players.name) \
            .where(players.id == row[0])
        self._cur.execute(get_player1_query.get_sql())
        player1_name = self._cur.fetchall()[0][0]

        get_player2_query = PostgreSQLQuery.from_(players) \
            .select(players.name) \
            .where(players.id == row[1])
        self._cur.execute(get_player2_query.get_sql())
        player2_name = self._cur.fetchall()[0][0]

        return GameState(
            player_ids=(row[0], row[1]),
            size_x=row[2],
            size_y=row[3],
            board=row[4],
            turn_color=row[5],
            turn_player=row[6],
            last_stone=row[7],
            last_capt_stone=row[8],
            player_passed=row[9],
            player1_name=player1_name,
            player2_name=player2_name
        )
