from typing import NamedTuple

from hive.engine import notation


class Piece:
    slots = "piece_str", "position", "piece_under", "piece_above"

    def __init__(
        self,
        piece_str: str,
        position: tuple[int, int],
        piece_under: "Piece | None",
        piece_above: "Piece | None",
    ):
        assert notation.PieceString.is_valid(piece_str)
        self.piece_str = piece_str
        self.position = position
        self.piece_under = piece_under
        self.piece_above = piece_above
