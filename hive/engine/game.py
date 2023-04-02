from enum import Enum, auto

from hive.engine import logic, pieces
from hive.engine.hive import Hive

_GAME_TYPE = "Base"
_STARTING_COLOR = pieces.PieceColor.WHITE


class GameState(Enum):
    BlackWin = auto()
    Draw = auto()
    InProgress = auto()
    NotStarted = auto()
    WhiteWins = auto()


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
    __slots__ = (
        "_hive",
        "_moves",
        "_moves_provider",
        "_state",
        "_turn_color",
        "_turn_num",
    )

    def __init__(self):
        self.new_game()

    @property
    def status(self) -> str:
        return ";".join(
            [
                _GAME_TYPE,
                self._state.name,
                pieces.get_turn_string(self._turn_num, self._turn_color),
                *self._moves,
            ]
        )

    def best_move(self):
        pass

    def new_game(self, game_info: str = "") -> None:
        self._state = GameState.NotStarted
        self._moves = []
        self._turn_color = _STARTING_COLOR
        self._turn_num = 1
        self._hive = Hive()
        self._moves_provider = logic.MovesProvider(self._hive)

    def pass_move(self):
        pass

    def play(self, piece_str: str, position: tuple[int, int]):
        pass

    def undo(self, to_undo: int) -> None:
        pass

    def valid_moves(self):
        pass

    def _next_turn(self):
        # TODO: check for the game end first

        if self._turn_color == pieces.PieceColor.WHITE:
            self._turn_color = pieces.PieceColor.BLACK
        else:
            self._turn_color = pieces.PieceColor.WHITE

        if self._turn_color == _STARTING_COLOR:
            self._turn_num += 1
