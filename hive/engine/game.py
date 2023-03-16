from dataclasses import dataclass
from enum import Enum, auto

from hive.engine import pieces
from hive.engine.hive import Hive

GAME_TYPE = "Base"
STARTING_COLOR = pieces.PieceColor.WHITE


class GameState(Enum):
    NotStarted = auto()
    InProgress = auto()
    Draw = auto()
    WhiteWins = auto()
    BlackWin = auto()


# class CommandValidator:
#     def validate(self, command):
#         pass


# @dataclass
# class CommandParser:
#     command: str
#     arguments: list[str]


# @dataclass
# class Command:
#     name: str
#     arguments: list[str]

#     def execute(self):
#         pass


class Game:
    __slots__ = "_state", "_hive", "_moves", "_turn_color", "_turn_num"

    def __init__(self):
        self.new_game()

    @property
    def status(self) -> str:
        return ";".join(
            [
                GAME_TYPE,
                self._state.name,
                pieces.get_turn_string(self._turn_num, self._turn_color),
                *self._moves,
            ]
        )

    def new_game(self):
        self._state = GameState.NotStarted
        self._hive = Hive()
        self._moves = []
        self._turn_color = STARTING_COLOR
        self._turn_num = 1

    def play(self, move_str: str):
        pass

    def pass_move(self):
        pass

    def valid_moves(self):
        pass

    def best_move(self):
        pass

    def undo(self):
        pass

    def _next_turn(self):
        # TODO: check for the game end first

        if self._turn_color == pieces.PieceColor.WHITE:
            self._turn_color = pieces.PieceColor.BLACK
        else:
            self._turn_color = pieces.PieceColor.WHITE

        if self._turn_color == STARTING_COLOR:
            self._turn_num += 1
