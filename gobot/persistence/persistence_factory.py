from enum import StrEnum

from gobot import settings
from gobot.persistence.dynamodb import DynamoDBAdapter
from gobot.persistence.persistence_port import PersistencePort
from gobot.persistence.postgres import PostgresAdapter


class DBs(StrEnum):
    DYNAMODB = "DYNAMODB"
    POSTGRESQL = "POSTGRESQL"


def get_db_adapter() -> PersistencePort:
    match settings.get_settings().DB_TYPE:
        case DBs.DYNAMODB:
            return DynamoDBAdapter()
        case DBs.POSTGRESQL:
            return PostgresAdapter()
