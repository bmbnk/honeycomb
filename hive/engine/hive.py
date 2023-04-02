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


from hive.engine import gamestrings as gs
from hive.engine import pieces as p


class HiveError(Exception):
    pass


class NotEmptyPositionError(HiveError):
    pass


class NotValidPieceError(HiveError):
    pass


class PieceAlreadyExistsError(HiveError):
    pass


class PieceNotInGameError(HiveError):
    pass


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
    def even_offsets_clockwise(cls) -> list[tuple[int, int]]:
        return list(cls._relation_to_move_offset["even"].values())

    @classmethod
    def is_row_even(cls, position: tuple[int, int]):
        return position[0] % 2 == 1

    @classmethod
    def move_offsets_clockwise(cls, position: tuple[int, int]) -> list[tuple[int, int]]:
        return list(
            cls._relation_to_move_offset[
                "even" if cls.is_row_even(position) else "odd"
            ].values()
        )

    @classmethod
    def odd_offsets_clockwise(cls) -> list[tuple[int, int]]:
        return list(cls._relation_to_move_offset["odd"].values())

    @classmethod
    def destination_position(
        cls, ref_pos: tuple[int, int], move_str: str
    ) -> tuple[int, int]:
        relation = cls._relation(move_str)
        if relation == cls._same_relation:
            return ref_pos
        offset = cls.position_offset(ref_pos, relation)
        return sum_tuple_elem_wise(ref_pos, offset)

    @classmethod
    def position_offset(
        cls, position: tuple[int, int], relation: str
    ) -> tuple[int, int]:
        return cls._relation_to_move_offset[
            "even" if cls.is_row_even(position) else "odd"
        ][relation]

    @classmethod
    def _relation(cls, move_str: str) -> str:
        position_str = gs.MoveStringsDecoder._get_position_str(move_str)

        for sign in gs.MoveStringsDecoder.relation_signs:
            if position_str.startswith(sign):
                return f"{sign}."
            elif position_str.endswith(sign):
                return f".{sign}"

        return cls._same_relation


class Hive:
    __slots__ = "_pieces"

    def __init__(self):
        self._pieces = {}

        for color in p.PieceColor:
            self._pieces[color] = {
                "hand": {
                    "str": set(p.pieces_str(color)),
                },
                "board": {
                    "instances": set(),
                    "positions": set(),
                    "str": set(),
                },
            }

    def add(self, piece_str: str, position: tuple[int, int] = (0, 0)) -> None:
        """
        Raises:
            PieceAlreadyExistsError: If piece_str is already in the hive.
            NotEmptyPositionError: If there is already a piece on position
        """
        assert p.is_piece_str_valid(piece_str)

        if piece_str in self.pieces_on_board_str(p.get_piece_color(piece_str)):
            raise PieceAlreadyExistsError
        if position in self.positions(p.PieceColor.BLACK) or position in self.positions(
            p.PieceColor.WHITE
        ):
            raise NotEmptyPositionError

        self._register_piece(piece_str, position)

    def is_position_empty(self, position: tuple[int, int]) -> bool:
        return position in self.positions(
            p.PieceColor.BLACK
        ) or position in self.positions(p.PieceColor.WHITE)

    def pieces_on_board_str(self, color: p.PieceColor | None = None) -> set[str]:
        if color is None:
            return self.pieces_on_board_str(
                p.PieceColor.BLACK
            ) | self.pieces_on_board_str(p.PieceColor.WHITE)
        pieces_str = self._pieces[color]["board"]["str"]
        return pieces_str

    def pieces_on_board(self, color: p.PieceColor | None = None) -> set[p.Piece]:
        if color is None:
            return self.pieces_on_board(p.PieceColor.BLACK) | self.pieces_on_board(
                p.PieceColor.WHITE
            )
        pieces = self._pieces[color]["board"]["instances"]
        return pieces

    def pieces_in_hand_str(self, color: p.PieceColor | None = None) -> set[str]:
        if color is None:
            return self.pieces_in_hand_str(
                p.PieceColor.BLACK
            ) | self.pieces_in_hand_str(p.PieceColor.WHITE)
        pieces_str = self._pieces[color]["hand"]["str"]
        return pieces_str

    def positions(self, color: p.PieceColor | None = None) -> set[tuple[int, int]]:
        if color is None:
            return self.positions(p.PieceColor.BLACK) | self.positions(
                p.PieceColor.WHITE
            )

        pieces = self._pieces[color]["board"]["positions"]
        return pieces

    def stack_height(self, position: tuple[int, int]) -> int:
        pieces = self.pieces_on_board()

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
        """
        Raises:
            PieceNotInGameError: If there is no piece in the hive with provided piece_str.
        """
        color = p.get_piece_color(piece_str)

        if piece_str not in self.pieces_on_board_str(color):
            raise PieceNotInGameError

        for piece in self.pieces_on_board(color):
            if p.get_piece_string(piece.info) == piece_str:
                self._transfer_piece(piece, position)
                break

    def _get_top_piece_on_position(self, position: tuple[int, int]) -> p.Piece | None:
        assert position in self.positions()

        pieces = self.pieces_on_board()

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

        self.pieces_on_board(new_piece.info.color).add(new_piece)
        self.pieces_on_board_str(new_piece.info.color).add(piece_str)
        self.positions(new_piece.info.color).add(position)

    def _transfer_piece(self, piece: p.Piece, position: tuple[int, int]) -> None:
        if piece.piece_under is not None:
            piece.piece_under.piece_above = piece.piece_above

        if piece.piece_above is not None:
            piece.piece_above.piece_under = piece.piece_under

        self.positions(piece.info.color).remove(piece.position)

        if not self.is_position_empty(position):
            top_piece_on_position = self._get_top_piece_on_position(position)
            assert top_piece_on_position is not None
            piece.piece_under = top_piece_on_position
            top_piece_on_position.piece_above = piece

        piece.position = position
        self.positions(piece.info.color).add(piece.position)
