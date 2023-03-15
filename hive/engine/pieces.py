from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

PIECE_STR_LEN = 3

_PIECES = frozenset(
    [
        "wQ",
        "bQ",
        "wS1",
        "bS1",
        "wS2",
        "bS2",
        "wB1",
        "bB1",
        "wB2",
        "bB2",
        "wG1",
        "bG1",
        "wG2",
        "bG2",
        "wG3",
        "bG3",
        "wA1",
        "bA1",
        "wA2",
        "bA2",
        "wA3",
        "bA3",
    ]
)


class PieceColor(Enum):
    BLACK = "b"
    WHITE = "w"


class PieceType(Enum):
    BEE = "Q"
    SPIDER = "S"
    BEETLE = "B"
    GRASSHOPPER = "G"
    ANT = "A"


class PieceInfo(NamedTuple):
    color: PieceColor
    ptype: PieceType
    num: int


@dataclass
class Piece:
    info: PieceInfo
    position: tuple[int, int, int]


def get_piece_info(piece_str: str) -> PieceInfo:
    color, ptype, num = piece_str

    color = PieceColor(color)
    ptype = PieceType(ptype)
    num = int(num)

    return PieceInfo(color=color, ptype=ptype, num=num)


def get_piece_string(piece_info: PieceInfo) -> str:
    return "".join(
        [piece_info.color.value, piece_info.ptype.value, str(piece_info.num)]
    )


def get_turn_string(turn_num: int, piece_color: PieceColor) -> str:
    return f"{piece_color.name.capitalize()}[{turn_num}]"


def is_piece_str_valid(piece_str: str) -> bool:
    return piece_str in _PIECES
