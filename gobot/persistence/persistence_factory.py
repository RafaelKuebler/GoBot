from enum import StrEnum

from gobot import settings
from gobot.persistence.persistence_port import PersistencePort


class DBs(StrEnum):
    DYNAMODB = "DYNAMODB"


def get_db_adapter() -> PersistencePort:
    match settings.get_settings().DB_TYPE:
        case DBs.DYNAMODB:
            from gobot.persistence.dynamodb import DynamoDBAdapter

            return DynamoDBAdapter()
