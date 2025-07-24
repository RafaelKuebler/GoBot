from dataclasses import dataclass

from gobot.telegram.player_color import PlayerColor


@dataclass
class Player:
    id_: int
    name: str
    color: PlayerColor
    did_pass: bool = False
