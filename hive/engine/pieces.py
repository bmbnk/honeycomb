from dataclasses import dataclass
from typing import NamedTuple

from hive.engine import notation


class PieceInfo(NamedTuple):
    color: notation.PieceColor
    ptype: notation.PieceType
    num: int


@dataclass
class Piece:
    info: PieceInfo
    position: tuple[int, int]
    piece_under: "Piece | None"
    piece_above: "Piece | None"


def get_piece_info(piece_str: str) -> PieceInfo:
    color, ptype, num = piece_str

    color = notation.PieceColor(color)
    ptype = notation.PieceType(ptype)
    num = int(num)

    return PieceInfo(color=color, ptype=ptype, num=num)
