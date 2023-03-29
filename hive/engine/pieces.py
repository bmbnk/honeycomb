from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class PieceColor(Enum):
    BLACK = "b"
    WHITE = "w"


def pieces_str(color: PieceColor):
    return {
        PieceColor.BLACK: frozenset(
            (
                "bA1",
                "bA2",
                "bA3",
                "bB1",
                "bB2",
                "bG1",
                "bG2",
                "bG3",
                "bQ",
                "bS1",
                "bS2",
            )
        ),
        PieceColor.WHITE: frozenset(
            (
                "wA1",
                "wA2",
                "wA3",
                "wB1",
                "wB2",
                "wG1",
                "wG2",
                "wG3",
                "wQ",
                "wS1",
                "wS2",
            )
        ),
    }[color]


PIECE_STR_LEN = 3


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
    position: tuple[int, int]
    piece_under: "Piece | None"
    piece_above: "Piece | None"


def get_piece_info(piece_str: str) -> PieceInfo:
    color, ptype, num = piece_str

    color = PieceColor(color)
    ptype = PieceType(ptype)
    num = int(num)

    return PieceInfo(color=color, ptype=ptype, num=num)


def get_piece_color(piece_str: str) -> PieceColor:
    return PieceColor(piece_str[0])


def get_piece_string(piece_info: PieceInfo) -> str:
    return "".join(
        [piece_info.color.value, piece_info.ptype.value, str(piece_info.num)]
    )


def get_piece_type(piece_str: str) -> PieceType:
    return PieceType(piece_str[0])


def get_turn_string(turn_num: int, piece_color: PieceColor) -> str:
    return f"{piece_color.name.capitalize()}[{turn_num}]"


def is_piece_str_valid(piece_str: str) -> bool:
    return piece_str in pieces_str(PieceColor.BLACK) or piece_str in pieces_str(
        PieceColor.WHITE
    )
