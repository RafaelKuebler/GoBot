import logging
from typing import Any, override

import boto3
from botocore.client import ClientError

import gobot.settings as settings
from gobot.persistence.persistence_port import PersistencePort, TelegramGoGame

logger = logging.getLogger(__name__)

GAMES_TABLE_NAME = "gobot_games"


def to_db_format(game: TelegramGoGame):
    # map board to dict
    db_board = {}
    for x in range(len(game.board)):
        for y in range(len(game.board[x])):
            if not game.board[x][y].free:
                db_board[f"{x},{y}"] = game.board[x][y].color
    return {
        "chat_id": dynamodb_format(game.chat_id),
        "size_x": dynamodb_format(game.size_x),
        "size_y": dynamodb_format(game.size_y),
        "player1_id": dynamodb_format(game.player_ids[0]),
        "player1_name": dynamodb_format(game.player_names[0]),
        "player2_id": dynamodb_format(game.player_ids[1]),
        "player2_name": dynamodb_format(game.player_names[1]),
        "turn_player_id": dynamodb_format(game.cur_player_id),
        "last_stone": dynamodb_format(f"{game.last_stone_placed[0]},{game.last_stone_placed[1]}" if game.last_stone_placed else None),
        "last_capt_stone": dynamodb_format(
            f"{game.last_captured_single_stone[0]},{game.last_captured_single_stone[1]}" if game.last_captured_single_stone else None
        ),
        "player1_passed": dynamodb_format(game.player_passed[0]),
        "player2_passed": dynamodb_format(game.player_passed[1]),
        "board": dynamodb_format(db_board),
        "turn_color": dynamodb_format(game.cur_player_color),
    }


def to_domain(game_state: dict[str, Any]) -> TelegramGoGame:
    chat_id = int(game_state["chat_id"]["N"])
    size_x = int(game_state["size_x"]["N"])
    size_y = int(game_state["size_y"]["N"])
    player1_id = int(game_state["player1_id"]["N"]) if "N" in game_state["player1_id"] else None
    player1_name = game_state["player1_name"]["S"] if "S" in game_state["player1_name"] else None
    player2_id = int(game_state["player2_id"]["N"]) if "N" in game_state["player2_id"] else None
    player2_name = game_state["player2_name"]["S"] if "S" in game_state["player2_name"] else None
    last_stone = game_state["last_stone"]["S"] if "S" in game_state["last_stone"] else None
    last_capt_stone = game_state["last_capt_stone"]["S"] if "S" in game_state["last_capt_stone"] else None
    player1_passed = game_state["player1_passed"]["BOOL"]
    player2_passed = game_state["player2_passed"]["BOOL"]

    game = TelegramGoGame(chat_id, size_x, size_y)
    game.player_ids = [player1_id, player2_id]
    game.player_names = [player1_name, player2_name]
    game.cur_player_id = int(game_state["turn_player_id"]["N"]) if "N" in game_state["turn_player_id"] else None
    game.cur_player_color = game_state["turn_color"]["S"]
    game.player_passed = [player1_passed, player2_passed]
    game.last_stone_placed = tuple(int(x) for x in last_stone.split(",")) if last_stone else None  # type:ignore
    game.last_captured_single_stone = tuple(int(x) for x in last_capt_stone.split(",")) if last_capt_stone else None  # type:ignore

    board = game_state["board"]["M"]
    for coord in board:
        x, y = [int(val) for val in coord.split(",")]
        color = board[coord]["S"]
        game.place_stone(x, y, color)

    return game


def dynamodb_format(value):
    """Converts a Python value to the appropriate DynamoDB type."""
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
        self.update_game(game)

    @override
    def load_game(self, chat_id: int) -> TelegramGoGame | None:
        logger.info(f"Loading game {chat_id} from DynamoDB")
        try:
            response = self.client.get_item(TableName=GAMES_TABLE_NAME, Key={"chat_id": dynamodb_format(chat_id)})
            game_state = response.get("Item")
            if game_state is None:
                return None
        except ClientError as err:
            logger.error(f"Couldn't read game {chat_id} from DynamoDB: {err.response['Error']['Message']}")  # type: ignore
            raise

        return to_domain(game_state)

    @override
    def update_game(self, game: TelegramGoGame) -> None:
        logger.info(f"Upserting game {game.chat_id} in DynamoDB")
        try:
            self.client.put_item(
                TableName=GAMES_TABLE_NAME,
                Item=to_db_format(game),
            )
        except ClientError as err:
            logger.error(f"Couldn't create game in DynamoDB: {err.response['Error']['Message']}")  # type: ignore
            raise

    @override
    def delete_game(self, chat_id: int) -> None:
        logger.info(f"Deleting game {chat_id} in DynamoDB")
        try:
            self.client.delete_item(
                TableName=GAMES_TABLE_NAME,
                Key={"chat_id": dynamodb_format(chat_id)},
            )
        except ClientError as err:
            logger.error(f"Couldn't create game in DynamoDB: {err.response['Error']['Message']}")  # type: ignore
            raise


if __name__ == "__main__":
    client = boto3.client(
        "dynamodb",
        endpoint_url=settings.get_settings().DYNAMODB_ENDPOINT,
        region_name="eu-west-1",
    )
    response = client.get_item(TableName=GAMES_TABLE_NAME, Key={"chat_id": dynamodb_format(549765073)})
    print(response)
