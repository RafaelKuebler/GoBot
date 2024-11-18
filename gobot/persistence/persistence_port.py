from abc import ABC, abstractmethod

from gobot.telegram.telegram_go_game import TelegramGoGame


class PersistencePort(ABC):
    @abstractmethod
    def new_game(self, game: TelegramGoGame) -> None: ...

    @abstractmethod
    def load_game(self, chat_id: int) -> TelegramGoGame | None: ...

    @abstractmethod
    def update_game(self, game: TelegramGoGame) -> None: ...

    @abstractmethod
    def delete_game(self, chat_id: int) -> None: ...
