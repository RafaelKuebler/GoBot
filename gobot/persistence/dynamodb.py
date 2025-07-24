import logging
from typing import Any, override

import boto3
from botocore.client import ClientError

import gobot.settings as settings
from gobot.persistence.persistence_port import PersistencePort, TelegramGoGame
from gobot.telegram.player import Player
from gobot.telegram.player_color import PlayerColor

logger = logging.getLogger(__name__)

GAMES_TABLE_NAME = "gobot_games"


def to_db_format(game: TelegramGoGame) -> dict[str, Any]:
    """Convert a TelegramGoGame to DynamoDB format"""
    db_board = {}
    for x in range(len(game.board)):
        for y in range(len(game.board[x])):
            if not game.board[x][y].is_free:
                db_board[f"{x},{y}"] = game.board[x][y].color

    player1 = game.players[0]
    db_format = {
        "chat_id": dynamodb_format(game.chat_id),
        "size_x": dynamodb_format(game.size_x),
        "size_y": dynamodb_format(game.size_y),
        "player1_id": dynamodb_format(player1.id_),
        "player1_name": dynamodb_format(player1.name),
        "player1_passed": dynamodb_format(player1.did_pass),
        "player2_id": dynamodb_format(None),
        "player2_name": dynamodb_format(None),
        "player2_passed": dynamodb_format(False),
        "turn_player_index": dynamodb_format(game.current_player_index),
        "last_stone": dynamodb_format(f"{game.last_stone_placed[0]},{game.last_stone_placed[1]}" if game.last_stone_placed else None),
        "last_capt_stone": dynamodb_format(
            f"{game.last_captured_single_stone[0]},{game.last_captured_single_stone[1]}" if game.last_captured_single_stone else None
        ),
        "board": dynamodb_format(db_board),
    }
    if len(game.players) > 1:
        player2 = game.players[1]
        db_format.update(
            {
                "player2_id": dynamodb_format(player2.id_),
                "player2_name": dynamodb_format(player2.name),
                "player2_passed": dynamodb_format(player2.did_pass),
            }
        )
    return db_format


def to_domain(game_state: dict[str, Any]) -> TelegramGoGame:
    """Convert a DynamoDB format game to a TelegramGoGame"""
    chat_id = int(game_state["chat_id"]["N"])
    size_x = int(game_state["size_x"]["N"])
    size_y = int(game_state["size_y"]["N"])
    player1_id = int(game_state["player1_id"]["N"])
    player1_name = game_state["player1_name"]["S"]
    player1_passed = game_state["player1_passed"]["BOOL"]
    player2_id = int(game_state["player2_id"]["N"]) if "N" in game_state["player2_id"] else None
    player2_name = game_state["player2_name"]["S"] if "S" in game_state["player2_name"] else None
    player2_passed = game_state["player2_passed"]["BOOL"]
    last_stone = game_state["last_stone"]["S"] if "S" in game_state["last_stone"] else None
    last_capt_stone = game_state["last_capt_stone"]["S"] if "S" in game_state["last_capt_stone"] else None

    game = TelegramGoGame(chat_id, size_x, size_y)
    game.players = [Player(player1_id, player1_name, PlayerColor.WHITE, player1_passed)]
    if player2_id and player2_name:
        game.players.append(Player(player2_id, player2_name, PlayerColor.BLACK, player2_passed))
    game.current_player_index = int(game_state["turn_player_index"]["N"])
    game.last_stone_placed = tuple(int(x) for x in last_stone.split(",")) if last_stone else None  # type:ignore

    board = game_state["board"]["M"]
    for coord in board:
        x, y = [int(val) for val in coord.split(",")]
        color = board[coord]["S"]
        game.place_stone(x, y, color)
    # this has to be set last to not be overwritten by the stone placements
    game.last_captured_single_stone = tuple(int(x) for x in last_capt_stone.split(",")) if last_capt_stone else None  # type:ignore

    return game


def dynamodb_format(value):
    """Convert a Python value to the appropriate DynamoDB type"""
    if isinstance(value, str):
        return {"S": value}
    elif isinstance(value, bool):
        return {"BOOL": value}
    elif isinstance(value, int):
        return {"N": str(value)}
    elif isinstance(value, dict):
        return {"M": {k: dynamodb_format(v) for k, v in value.items()}}
    elif isinstance(value, list):
        return {"L": [dynamodb_format(v) for v in value]}
    elif value is None:
        return {"NULL": True}
    else:
        logger.error(f"Cannot convert type {type(value)} to DynamoDB format")
        raise ValueError(f"Unsupported type: {type(value)}")


class DynamoDBAdapter(PersistencePort):
    def __init__(self):
        settings_ = settings.get_settings()
        if settings_.USE_LOCAL_DB:
            self.client = boto3.client(
                "dynamodb",
                endpoint_url=settings_.DYNAMODB_ENDPOINT,
                region_name="eu-west-1",
            )
            self._ensure_table_exists()
        else:
            self.client = boto3.client("dynamodb")

    def _ensure_table_exists(self):
        existing_tables = self.client.list_tables()["TableNames"]
        if GAMES_TABLE_NAME not in existing_tables:
            self.client.create_table(
                TableName=GAMES_TABLE_NAME,
                AttributeDefinitions=[{"AttributeName": "chat_id", "AttributeType": "N"}],
                KeySchema=[{"AttributeName": "chat_id", "KeyType": "HASH"}],
                ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            )
            # Wait for the table to be active
            waiter = self.client.get_waiter("table_exists")
            waiter.wait(TableName=GAMES_TABLE_NAME)

    @override
    def new_game(self, game: TelegramGoGame) -> None:
        self.delete_game(game.chat_id)
        self.update_game(game)

    @override
    def load_game(self, chat_id: int) -> TelegramGoGame | None:
        logger.info(f"Loading game {chat_id} from DynamoDB...")
        try:
            response = self.client.get_item(TableName=GAMES_TABLE_NAME, Key={"chat_id": dynamodb_format(chat_id)})
            game_state = response.get("Item")
            if game_state is None:
                return None
            as_domain = to_domain(game_state)
        except ClientError as err:
            logger.error(f"Couldn't read game {chat_id} from DynamoDB: {err.response['Error']['Message']}")  # type: ignore
            raise
        except Exception as err:
            logger.error(f"Couldn't read game from DynamoDB: {err}")
            raise
        logger.info("Loaded game successfully!")
        return as_domain

    @override
    def update_game(self, game: TelegramGoGame) -> None:
        logger.info(f"Upserting game {game.chat_id} in DynamoDB...")
        try:
            self.client.put_item(
                TableName=GAMES_TABLE_NAME,
                Item=to_db_format(game),
            )
            logger.info("Updated game successfully!")
        except ClientError as err:
            logger.error(f"Couldn't update game in DynamoDB: {err.response['Error']['Message']}")  # type: ignore
            raise
        except Exception as err:
            logger.error(f"Couldn't update game in DynamoDB: {err}")
            raise

    @override
    def delete_game(self, chat_id: int) -> None:
        logger.info(f"Deleting game {chat_id} from DynamoDB...")
        try:
            self.client.delete_item(
                TableName=GAMES_TABLE_NAME,
                Key={"chat_id": dynamodb_format(chat_id)},
            )
            logger.info("Deleted game successfully!")
        except ClientError as err:
            logger.error(f"Couldn't delete game from DynamoDB: {err.response['Error']['Message']}")  # type: ignore
            raise
        except Exception as err:
            logger.error(f"Couldn't delete game from DynamoDB: {err}")
            raise
