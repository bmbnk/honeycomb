from typing import NamedTuple

from hive.engine import notation


class PieceInfo(NamedTuple):
    color: notation.PieceColor
    ptype: notation.PieceType
    num: int


class Piece:
    slots = "info", "position", "piece_under", "piece_above"

    def __init__(
        self,
        info: PieceInfo,
        position: tuple[int, int],
        piece_under: "Piece | None",
        piece_above: "Piece | None",
    ):
        self.info = info
        self.position = position
        self.piece_under = piece_under
        self.piece_above = piece_above


def get_piece_info(piece_str: str) -> PieceInfo:
    color, ptype, num = piece_str

    color = notation.PieceColor(color)
    ptype = notation.PieceType(ptype)
    num = int(num)

    return PieceInfo(color=color, ptype=ptype, num=num)
