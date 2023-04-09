# Relative coordinates for the even rows:
#
#   /  \   /  \   /  \   /  \
# |  --  | -1,0 | -1,1 |  --  |
#   \  /   \  /   \  /   \  /   \
#     | 0,-1 | 0,0  | 0,1  |  --  |
#   /  \   /  \   /  \   /  \   /
# |  --  | 1,0  | 1,1  |  --  |
#   \  /   \  /   \  /   \  /   \
#     |  --  |  --  |  --  |  --
#   /  \   /  \   /  \   /  \   /
#
# Relative coordinates for the odd rows:
#
#   /  \   /  \   /  \   /  \
# |  --  |  --  |  --  |  --  |
#   \  /   \  /   \  /   \  /   \
#     |  --  |-1,-1 | -1,0 |  --  |
#   /  \   /  \   /  \   /  \   /
# |  --  | 0,-1 | 0,0  | 0,1  |
#   \  /   \  /   \  /   \  /   \
#     |  --  | 1,-1 | 1,0  |  --
#   /  \   /  \   /  \   /  \   /
#
# Relative odd rows coordinates can be obtained by subtracting value of 1
# from the first coordinate of positions under and below of the center point
# from the even rows relative coordinates.
#
# First piece starts on the odd row with position (0, 0).

import collections

from hive.engine import err, notation
from hive.engine import pieces as p


def sum_tuple_elem_wise(a: tuple, b: tuple):
    return tuple([a_i + b_i for a_i, b_i in zip(a, b)])


class PositionsResolver:
    _relation_to_move_offset = {
        "even": {
            "./": (-1, 1),
            ".-": (0, 1),
            ".\\": (1, 1),
            "/.": (1, 0),
            "-.": (0, -1),
            "\\.": (-1, 0),
        },
        "odd": {
            "./": (-1, 0),
            ".-": (0, 1),
            ".\\": (1, 0),
            "/.": (1, -1),
            "-.": (0, -1),
            "\\.": (-1, -1),
        },
    }
    _same_relation = "."

    @classmethod
    def destination_position(
        cls, ref_pos: tuple[int, int], relation: str
    ) -> tuple[int, int]:
        if relation == cls._same_relation:
            return ref_pos
        offset = cls._position_offset(ref_pos, relation)
        return sum_tuple_elem_wise(ref_pos, offset)

    @classmethod
    def even_offsets_clockwise(cls) -> list[tuple[int, int]]:
        return list(cls._relation_to_move_offset["even"].values())

    @classmethod
    def is_row_even(cls, position: tuple[int, int]):
        return position[0] % 2 == 1

    @classmethod
    def odd_offsets_clockwise(cls) -> list[tuple[int, int]]:
        return list(cls._relation_to_move_offset["odd"].values())

    @classmethod
    def positions_around_clockwise(
        cls, position: tuple[int, int]
    ) -> list[tuple[int, int]]:
        return list(
            (position[0] + offset[0], position[1] + offset[1])
            for offset in cls._move_offsets_clockwise(position)
        )

    @classmethod
    def relation(cls, position: tuple[int, int], ref_position: tuple[int, int]) -> str:
        ...

    @classmethod
    def _move_offsets_clockwise(
        cls, position: tuple[int, int]
    ) -> list[tuple[int, int]]:
        return list(
            cls._relation_to_move_offset[
                "even" if cls.is_row_even(position) else "odd"
            ].values()
        )

    @classmethod
    def _position_offset(
        cls, position: tuple[int, int], relation: str
    ) -> tuple[int, int]:
        return cls._relation_to_move_offset[
            "even" if cls.is_row_even(position) else "odd"
        ][relation]


class MovesStack:
    __slots__ = "_stack"

    def __init__(self):
        self._stack = collections.deque()

    def push(
        self,
        piece: p.Piece,
        start_position: tuple[int, int] | None,
        end_position: tuple[int, int],
    ):
        self._stack.append((piece, start_position, end_position))

    def pop(self):
        return self._stack.pop()


class Hive:
    __slots__ = "_pieces", "_moves_stack"

    def __init__(self):
        self._pieces = {}
        self._moves_stack = MovesStack()

        for color in notation.PieceColor:
            self._pieces[color] = {
                "hand": {
                    "str": set(notation.pieces_str(color)),
                },
                "board": {
                    "instances": set(),
                    "positions": set(),
                    "str": set(),
                },
            }

    @property
    def start_position(self):
        return (0, 0)

    def add(self, piece_str: str, position: tuple[int, int] | None = None) -> None:
        assert position not in self.positions()
        assert piece_str not in self.pieces_on_board_str()

        if position is None:
            position = self.start_position

        self._register_piece(piece_str, position)

    def is_bee_on_board(self, color: notation.PieceColor) -> bool:
        return notation.PieceString.build(
            color, notation.PieceType.BEE, 0
        ) in self.pieces_on_board_str(color)

    def is_position_empty(self, position: tuple[int, int]) -> bool:
        return position in self.positions(
            notation.PieceColor.BLACK
        ) or position in self.positions(notation.PieceColor.WHITE)

    def pieces_on_board_str(self, color: notation.PieceColor | None = None) -> set[str]:
        if color is None:
            return self.pieces_on_board_str(
                notation.PieceColor.BLACK
            ) | self.pieces_on_board_str(notation.PieceColor.WHITE)
        pieces_str = self._pieces[color]["board"]["str"]
        return pieces_str

    def piece(self, piece_str: str) -> p.Piece | None:
        assert piece_str in self.pieces_on_board_str()

        color, *_ = notation.PieceString.decompose(piece_str)
        for piece in self.pieces(color):
            p_str = notation.PieceString.build(
                piece.info.color, piece.info.ptype, piece.info.num
            )
            if p_str == piece_str:
                return piece

    def pieces(self, color: notation.PieceColor | None = None) -> set[p.Piece]:
        if color is None:
            return self.pieces(notation.PieceColor.BLACK) | self.pieces(
                notation.PieceColor.WHITE
            )
        pieces = self._pieces[color]["board"]["instances"]
        return pieces

    def pieces_in_hand_str(self, color: notation.PieceColor | None = None) -> set[str]:
        if color is None:
            return self.pieces_in_hand_str(
                notation.PieceColor.BLACK
            ) | self.pieces_in_hand_str(notation.PieceColor.WHITE)
        pieces_str = self._pieces[color]["hand"]["str"]
        return pieces_str

    def positions(
        self, color: notation.PieceColor | None = None
    ) -> set[tuple[int, int]]:
        if color is None:
            return self.positions(notation.PieceColor.BLACK) | self.positions(
                notation.PieceColor.WHITE
            )

        pieces = self._pieces[color]["board"]["positions"]
        return pieces

    def stack_height(self, position: tuple[int, int]) -> int:
        pieces = self.pieces()

        for piece in pieces:
            if piece.position == position:
                height = 1

                p = piece
                while (p := p.piece_under) is not None:
                    height += 1

                p = piece
                while (p := p.piece_above) is not None:
                    height += 1

                return height

        return 0

    def move(self, piece_str: str, position: tuple[int, int]) -> None:
        assert piece_str in self.pieces_on_board_str()
        color, *_ = notation.PieceString.decompose(piece_str)

        for piece in self.pieces(color):
            p_str = notation.PieceString.build(
                piece.info.color, piece.info.ptype, piece.info.num
            )
            if p_str == piece_str:
                self._transfer_piece(piece, position)
                break

    def undo(self, moves_num: int):
        for _ in range(moves_num):
            if not self._moves_stack:
                break

            piece, start_position, end_position = self._moves_stack.pop()
            if start_position is None:
                piece_str = notation.PieceString.build(
                    piece.info.color, piece.info.ptype, piece.info.num
                )
                piece_color = piece.info.color

                self.pieces_on_board_str(piece_color).remove(piece_str)
                self.positions(piece_color).remove(end_position)
                self.pieces(piece_color).remove(piece)
                self.pieces_in_hand_str(piece_color).add(piece_str)
            else:
                self._transfer_piece(piece, start_position)

    def _get_top_piece_on_position(self, position: tuple[int, int]) -> p.Piece | None:
        assert position in self.positions()

        pieces = self.pieces()

        for piece in pieces:
            if piece.position == position:
                while piece.piece_above is not None:
                    piece = piece.piece_above
                return piece

    def _register_piece(self, piece_str: str, position: tuple[int, int]) -> None:
        new_piece = p.Piece(
            info=p.get_piece_info(piece_str),
            position=position,
            piece_under=None,
            piece_above=None,
        )

        self.pieces_in_hand_str(new_piece.info.color).remove(piece_str)

        self.pieces(new_piece.info.color).add(new_piece)
        self.pieces_on_board_str(new_piece.info.color).add(piece_str)
        self.positions(new_piece.info.color).add(position)

        self._moves_stack.push(new_piece, None, position)

    def _transfer_piece(self, piece: p.Piece, position: tuple[int, int]) -> None:
        if piece.piece_under is not None:
            piece.piece_under.piece_above = piece.piece_above

        if piece.piece_above is not None:
            piece.piece_above.piece_under = piece.piece_under

        start_position = piece.position

        self.positions(piece.info.color).remove(start_position)

        if not self.is_position_empty(position):
            top_piece_on_position = self._get_top_piece_on_position(position)
            assert top_piece_on_position is not None
            piece.piece_under = top_piece_on_position
            top_piece_on_position.piece_above = piece

        piece.position = position
        self.positions(piece.info.color).add(piece.position)

        self._moves_stack.push(piece, start_position, position)
