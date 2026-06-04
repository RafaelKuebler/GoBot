import logging
from typing import TYPE_CHECKING, Any, override

import boto3
from botocore.exceptions import ClientError

import gobot.settings as settings

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from gobot.persistence.persistence_port import PersistencePort, TelegramGoGame
from gobot.telegram.player import Player
from gobot.telegram.player_color import PlayerColor

logger = logging.getLogger(__name__)

GAMES_TABLE_NAME = "gobot_games"


def to_db_format(game: TelegramGoGame) -> dict[str, Any]:
    """Convert a TelegramGoGame to dict format for DynamoDB"""
    db_board = {}
    for x in range(len(game.board)):
        for y in range(len(game.board[x])):
            if not game.board[x][y].is_free:
                db_board[f"{x},{y}"] = game.board[x][y].color

    player1 = game.players[0]
    db_format = {
        "chat_id": game.chat_id,
        "size_x": game.size_x,
        "size_y": game.size_y,
        "player1_id": player1.id_,
        "player1_name": player1.name,
        "player1_passed": player1.did_pass,
        "player2_id": None,
        "player2_name": None,
        "player2_passed": False,
        "turn_player_index": game.current_player_index,
        "last_stone": f"{game.last_stone_placed[0]},{game.last_stone_placed[1]}" if game.last_stone_placed else None,
        "last_capt_stone": f"{game.last_captured_single_stone[0]},{game.last_captured_single_stone[1]}" if game.last_captured_single_stone else None,
        "board": db_board,
    }
    if len(game.players) > 1:
        player2 = game.players[1]
        db_format.update(
            {
                "player2_id": player2.id_,
                "player2_name": player2.name,
                "player2_passed": player2.did_pass,
            }
        )
    return db_format


def to_domain(game_state: dict[str, Any]) -> TelegramGoGame:
    """Convert a DynamoDB item to a TelegramGoGame"""
    # DynamoDB resource returns Decimal objects, convert to int
    chat_id = int(game_state["chat_id"])
    size_x = int(game_state["size_x"])
    size_y = int(game_state["size_y"])
    player1_id = int(game_state["player1_id"])
    player1_name = game_state["player1_name"]
    player1_passed = game_state["player1_passed"]
    player2_id = int(game_state["player2_id"]) if game_state["player2_id"] else None
    player2_name = game_state["player2_name"]
    player2_passed = game_state["player2_passed"]
    last_stone = game_state["last_stone"]
    last_capt_stone = game_state["last_capt_stone"]

    game = TelegramGoGame(chat_id, size_x, size_y)
    game.players = [Player(player1_id, player1_name, PlayerColor.WHITE, player1_passed)]
    if player2_id and player2_name:
        game.players.append(Player(player2_id, player2_name, PlayerColor.BLACK, player2_passed))
    game.current_player_index = int(game_state["turn_player_index"])
    game.last_stone_placed = tuple(int(x) for x in last_stone.split(",")) if last_stone else None  # type:ignore

    board = game_state["board"]
    for coord in board:
        x, y = [int(val) for val in coord.split(",")]
        color = board[coord]
        game.place_stone(x, y, color)
    # this has to be set last to not be overwritten by the stone placements
    game.last_captured_single_stone = tuple(int(x) for x in last_capt_stone.split(",")) if last_capt_stone else None  # type:ignore

    return game


class DynamoDBAdapter(PersistencePort):
    def __init__(self):
        settings_ = settings.get_settings()
        if settings_.USE_LOCAL_DB:
            dynamodb: "DynamoDBServiceResource" = boto3.resource(
                "dynamodb",
                endpoint_url=settings_.DYNAMODB_ENDPOINT,
                region_name="eu-west-1",
            )
            self.table: "Table" = dynamodb.Table(GAMES_TABLE_NAME)
            self._ensure_table_exists(dynamodb)
        else:
            dynamodb: "DynamoDBServiceResource" = boto3.resource("dynamodb")
            self.table: "Table" = dynamodb.Table(GAMES_TABLE_NAME)

    def _ensure_table_exists(self, dynamodb: "DynamoDBServiceResource") -> None:
        existing_tables = [table.name for table in dynamodb.tables.all()]
        if GAMES_TABLE_NAME not in existing_tables:
            table = dynamodb.create_table(
                TableName=GAMES_TABLE_NAME,
                KeySchema=[{"AttributeName": "chat_id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "chat_id", "AttributeType": "N"}],
                ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            )
            table.wait_until_exists()

    @override
    def new_game(self, game: TelegramGoGame) -> None:
        self.delete_game(game.chat_id)
        self.update_game(game)

    @override
    def load_game(self, chat_id: int) -> TelegramGoGame | None:
        logger.info(f"Loading game {chat_id} from DynamoDB...")
        try:
            response = self.table.get_item(Key={"chat_id": chat_id})
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
            self.table.put_item(Item=to_db_format(game))
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
            self.table.delete_item(Key={"chat_id": chat_id})
            logger.info("Deleted game successfully!")
        except ClientError as err:
            logger.error(f"Couldn't delete game from DynamoDB: {err.response['Error']['Message']}")  # type: ignore
            raise
        except Exception as err:
            logger.error(f"Couldn't delete game from DynamoDB: {err}")
            raise
