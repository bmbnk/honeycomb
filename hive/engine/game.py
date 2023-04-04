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


class GameError(Exception):
    pass


class InvalidMove(GameError):
    pass


class InvalidAddingPositionError(InvalidMove):
    pass


class InvalidMovingPositionError(InvalidMove):
    pass


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
        self._next_turn()

    def play(self, piece_str: str, position: tuple[int, int]):
        """
        Raises:
            InvalidAddingPositionError: If adding position is not valid.
            InvalidMovingPositionError: If moving position is not valid.
        """
        # TODO: Implement better validation logic then calculating all possible moves
        color = pieces.get_piece_color(piece_str)
        if piece_str in self._hive.pieces_in_hand_str(color):
            adding_positions = self._moves_provider.adding_positions(color)
            if position in adding_positions:
                self._hive.add(piece_str, position)
            else:
                raise InvalidAddingPositionError
        else:
            piece = self._hive.piece(piece_str)
            if position in self._moves_provider.move_positions(piece):
                self._hive.move(piece_str, position)
            else:
                raise InvalidMovingPositionError

        self._next_turn()

    def undo(self, to_undo: int) -> None:
        pass

    def valid_moves(self):
        piece_str_to_positions = {}

        for piece in self._hive.pieces(self._turn_color):
            move_positions = self._moves_provider.move_positions(piece)
            piece_str = pieces.get_piece_string(piece.info)
            piece_str_to_positions[piece_str] = move_positions

        adding_positions = self._moves_provider.adding_positions(self._turn_color)
        for piece_str in self._hive.pieces_in_hand_str():
            piece_str_to_positions[piece_str] = adding_positions

        return piece_str_to_positions

    def _next_turn(self):
        # TODO: check for the game end first

        if self._turn_color == pieces.PieceColor.WHITE:
            self._turn_color = pieces.PieceColor.BLACK
        else:
            self._turn_color = pieces.PieceColor.WHITE

        if self._turn_color == _STARTING_COLOR:
            self._turn_num += 1
