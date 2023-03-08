from enum import Enum, auto

import pieces

COMPLETION_STR = "ok"
GAME_TYPE = "Base"
ENGINE_NAME = "EngineName"
VERSION = "1.0"


def get_engine_info() -> str:
    return f"id {ENGINE_NAME} v{VERSION}"


class GameState(Enum):
    NotStarted = auto()
    InProgress = auto()
    Draw = auto()
    WhiteWins = auto()
    BlackWin = auto()


class Hive:
    __slots__ = "__pieces", "__pieces_str", "__pieces_positions"

    def __init__(self):
        self.__pieces = []
        self.__pieces_str = set()
        self.__pieces_positions = set()

    def add(self, piece_str: str):
        pass

    def remove(self, piece_str: str):
        pass

    def is_in_hive(self, piece_str: str):
        pass

    def is_position_empty(self, position: tuple[int, int, int]):
        pass
