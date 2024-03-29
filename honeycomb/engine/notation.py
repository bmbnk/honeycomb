import re
from enum import Enum, auto

from honeycomb.engine import err

PIECE_MAX_NUM = 3


class NotationError(err.BaseEngineError):
    pass


class InvalidGameStringError(NotationError):
    def __init__(self, message):
        super().__init__(message)


class InvalidGameTypeStringError(NotationError):
    def __init__(self, message):
        super().__init__(message)


class InvalidMoveStringError(NotationError):
    def __init__(self, message):
        super().__init__(message)


class InvalidPieceStringError(NotationError):
    def __init__(self, message):
        super().__init__(message)


class InvalidTurnStringError(NotationError):
    def __init__(self, message):
        super().__init__(message)


class GameState(Enum):
    BlackWins = auto()
    Draw = auto()
    InProgress = auto()
    NotStarted = auto()
    WhiteWins = auto()


class PieceColor(Enum):
    BLACK = "b"
    WHITE = "w"


class PieceType(Enum):
    @classmethod
    def has(cls, ptype):
        return ptype in cls._value2member_map_


class BasePieces(PieceType):
    BEE = "Q"
    SPIDER = "S"
    BEETLE = "B"
    GRASSHOPPER = "G"
    ANT = "A"


class ExpansionPieces(PieceType):
    MOSQUITO = "M"
    LADYBUG = "L"
    PILLBUG = "P"


def pieces_str(color: PieceColor, expansion_pieces: set[ExpansionPieces] | None = None):
    if expansion_pieces is None:
        expansion_pieces = set()

    pieces_str = set()

    color_str = color.value
    ptype_strs = {base_piece.value for base_piece in BasePieces}
    ptype_strs |= {
        expansion_piece.value
        for expansion_piece in ExpansionPieces
        if expansion_piece in expansion_pieces
    }
    num_strs = {str(num) for num in range(1, PIECE_MAX_NUM + 1)}
    num_strs.add("")

    for ptype_str in ptype_strs:
        for num_str in num_strs:
            piece_str = color_str + ptype_str + num_str
            if PieceString.is_valid(piece_str):
                pieces_str.add(piece_str)

    return pieces_str


class MoveString:
    _relation_signs = frozenset({"/", "-", "\\"})

    @classmethod
    def build(
        cls,
        piece_str: str,
        relation: str | None = None,
        ref_piece_str: str | None = None,
    ) -> str:
        if relation is not None and ref_piece_str is not None:
            move_part = relation.replace(".", ref_piece_str)
            return f"{piece_str} {move_part}"
        return f"{piece_str}"

    @classmethod
    def decompose(
        cls, move_str: str
    ) -> tuple[None] | tuple[str] | tuple[str, str, str]:
        """
        Returns:
            (None,): If 'pass'
            (piece_str, relation_str, ref_piece_str): If there is action piece and reference piece
            (piece_str,): If there is only action piece

        Raises:
            InvalidMoveStrinError: If move_str is not a valid MoveString
        """
        if move_str == "pass":
            return (None,)
        prog = re.compile("(\\S+)(?: (\\S+))?")
        if match := prog.fullmatch(move_str):
            piece_str, moving_part = match.groups()
            if PieceString.is_valid(piece_str):
                if moving_part is None:
                    return (piece_str,)

                relation = "."
                ref_piece_str = moving_part

                if moving_part[0] in cls._relation_signs:
                    relation = moving_part[0] + relation
                    ref_piece_str = moving_part[1:]
                elif moving_part[-1] in cls._relation_signs:
                    relation = relation + moving_part[-1]
                    ref_piece_str = moving_part[:-1]

                if PieceString.is_valid(ref_piece_str):
                    return piece_str, relation, ref_piece_str

        raise InvalidMoveStringError(f"Invalid MoveString: {move_str}.")

    @classmethod
    def is_valid(cls, move_str: str) -> bool:
        if move_str == "pass":
            return True
        prog = re.compile("(\\S+)(?: (\\S+))?")
        if match := prog.fullmatch(move_str):
            piece_str, moving_part = match.groups()
            if PieceString.is_valid(piece_str):
                if moving_part is None:
                    return True

                ref_piece_str = moving_part

                if moving_part[0] in cls._relation_signs:
                    ref_piece_str = moving_part[1:]
                elif moving_part[-1] in cls._relation_signs:
                    ref_piece_str = moving_part[:-1]

                if PieceString.is_valid(ref_piece_str):
                    return True
        return False


class GameTypeString:
    _base_game_name = "Base"

    @classmethod
    def build(cls, expansions: set[ExpansionPieces]) -> str:
        if expansions:
            return f"{cls._base_game_name}+{''.join([e.name for e in expansions])}"
        return cls._base_game_name

    @classmethod
    def decompose(cls, gametype: str) -> set[ExpansionPieces]:
        prog = re.compile("Base(?:\\+(M|L|P)(M|L|P)?(M|L|P)?)?")
        if match := prog.fullmatch(gametype):
            return set(
                [
                    ExpansionPieces(group)
                    for group in match.groups()
                    if group is not None
                ]
            )
        raise InvalidGameTypeStringError(f"Invalid GameTypeString: {gametype}.")

    @classmethod
    def is_valid(cls, gametype: str) -> bool:
        prog = re.compile("Base(?:\\+(M|L|P)(M|L|P)?(M|L|P)?)?")
        return prog.fullmatch(gametype) is not None


class TurnString:
    @classmethod
    def build(cls, piece_color: PieceColor, turn_num: int) -> str:
        return f"{piece_color.name.capitalize()}[{turn_num}]"

    @classmethod
    def decompose(cls, turn_str: str) -> tuple[PieceColor, int]:
        prog = re.compile("(White|Black)\\[([1-9]\\d*)\\]")
        if match := prog.fullmatch(turn_str):
            turn_color, turn_num = match.groups()
            return PieceColor[turn_color.upper()], int(turn_num)

        raise InvalidTurnStringError(f"Invalid TurnString: {turn_str}.")


class GameString:
    @classmethod
    def build(
        cls,
        expansions: set[ExpansionPieces],
        gamestate: GameState,
        turn_num: int,
        turn_color: PieceColor,
        moves: list[str],
    ):
        return ";".join(
            [
                GameTypeString.build(expansions),
                gamestate.name,
                TurnString.build(turn_color, turn_num),
                *moves,
            ]
        )

    @classmethod
    def decompose(
        cls, game_str: str
    ) -> tuple[set[ExpansionPieces], GameState, PieceColor, int, list[str]]:
        # TODO: Refactor all string building, decomposing and validating classes so that there is only one regex compilation per runtime
        prog = re.compile("([^;]*);([^;]*);([^;]*)(?:;(.*))?")
        if match := prog.fullmatch(game_str):
            gametype_str, gamestate_str, turn_str, moves_part = match.groups()
            expansion_pieces = GameTypeString.decompose(gametype_str)
            gamestate = GameState[gamestate_str]
            turn_color, turn_num = TurnString.decompose(turn_str)

            moves = []
            if moves_part is not None:
                for move in moves_part.split(";"):
                    if not MoveString.is_valid(move):
                        raise InvalidMoveStringError(f"Invalid MoveString: {move}.")
                    moves.append(move)

            return expansion_pieces, gamestate, turn_color, turn_num, moves

        raise InvalidGameStringError(f"Invalid GameString: {game_str}.")

    @classmethod
    def is_valid(cls, game_str: str) -> bool:
        prog = re.compile("([^;]*);([^;]*);([^;]*)(?:(;.*)*)")
        return prog.fullmatch(game_str) is not None


class PieceString:
    @classmethod
    def build(
        cls,
        piece_color: PieceColor,
        piece_type: PieceType,
        piece_num: int,
    ) -> str:
        if piece_type == BasePieces.BEE:
            return "".join([piece_color.value, piece_type.value])
        return "".join([piece_color.value, piece_type.value, str(piece_num)])

    @classmethod
    def decompose(
        cls, piece_str: str
    ) -> tuple[PieceColor, PieceType] | tuple[PieceColor, PieceType, int]:
        prog = re.compile(
            "([bw])(?:(?:(Q))|(?:([SB])([12]))|(?:([AG])([1-3]))|(?:(M))|(?:(L))|(?:(P)))"
        )
        if match := prog.fullmatch(piece_str):
            color_str, type_str, *num = [
                group for group in match.groups() if group is not None
            ]
            color = PieceColor(color_str)
            if ExpansionPieces.has(type_str):
                type_ = ExpansionPieces(type_str)
            else:
                type_ = BasePieces(type_str)

            if num:
                return color, type_, int(num[0])
            return color, type_

        raise InvalidPieceStringError(f"Invalid PieceString: {piece_str}.")

    @classmethod
    def is_valid(cls, piece_str: str) -> bool:
        prog = re.compile(
            "([bw])(?:(?:(Q))|(?:([SB])([12]))|(?:([AG])([1-3]))|(?:(M))|(?:(L))|(?:(P)))"
        )
        return prog.fullmatch(piece_str) is not None
