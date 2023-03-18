# Relative coordinates for the even rows:
#
#   /  \   /  \   /  \   /  \
# |  --  | 0,-1 | 1,-1 |  --  |
#   \  /   \  /   \  /   \  /   \
#     | -1,0 | 0,0  | 1,0  |  --  |
#   /  \   /  \   /  \   /  \   /
# |  --  | 0,1  | 1,1  |  --  |
#   \  /   \  /   \  /   \  /   \
#     |  --  |  --  |  --  |  --
#   /  \   /  \   /  \   /  \   /
#
# Relative coordinates for the odd rows:
#
#   /  \   /  \   /  \   /  \
# |  --  |  --  |  --  |  --  |
#   \  /   \  /   \  /   \  /   \
#     |  --  |-1,-1 | 0,-1 |  --  |
#   /  \   /  \   /  \   /  \   /
# |  --  | -1,0 | 0,0  | 1,0  |
#   \  /   \  /   \  /   \  /   \
#     |  --  | -1,1 | 0,1  |  --
#   /  \   /  \   /  \   /  \   /
#
# Relative odd rows coordinates can be obtained by subtracting value of 1
# from the first coordinate of positions under and below of the center point
# from the even rows relative coordinates.
#
# First piece starts on the odd row.


from hive.engine import pieces


class HiveError(Exception):
    pass


class InvalidPositionError(HiveError):
    pass


class PieceAlreadyExistsError(HiveError):
    pass


class PieceNotExistsError(HiveError):
    pass


class NotValidPieceError(HiveError):
    pass


def sum_tuple_elem_wise(a: tuple, b: tuple):
    return tuple([a_i + b_i for a_i, b_i in zip(a, b)])


class PositionsResolver:
    _even_row_relations_to_offset = {
        "./": (1, -1),
        ".-": (1, 0),
        ".\\": (1, 1),
        "/.": (0, 1),
        "-.": (-1, 0),
        "\\.": (0, -1),
        ".": (0, 0),
    }
    _odd_row_offset = (-1, 0)

    @classmethod
    def get_destination_position(
        cls, ref_pos: tuple[int, int], move_str: str
    ) -> tuple[int, int]:
        relation = cls._get_relation(move_str)
        position_offset = cls._get_position_offset(ref_pos, relation)
        return sum_tuple_elem_wise(ref_pos, position_offset)

    @classmethod
    def _get_position_offset(
        cls, position: tuple[int, int], relation: str
    ) -> tuple[int, int]:
        position_offset = cls._even_row_relations_to_offset[relation]

        if position[1] % 2 == 0 and position_offset[1] != 0:
            position_offset += cls._odd_row_offset

        return position_offset

    @classmethod
    def _get_relation(cls, move_str: str) -> str:
        position_str = MoveStringsDecoder._get_position_str(move_str)

        for sign in MoveStringsDecoder.relation_signs:
            if position_str.startswith(sign):
                return f"{sign}."
            elif position_str.endswith(sign):
                return f".{sign}"

        return "."


class MoveStringsDecoder:
    _relation_signs = frozenset({"/", "-", "\\"})

    @property
    @classmethod
    def relation_signs(cls) -> frozenset:
        return cls._relation_signs

    @classmethod
    def get_piece_to_move(cls, move_str: str) -> str:
        return move_str.split()[0]

    @classmethod
    def get_ref_piece(cls, move_str: str) -> str:
        pos_str = cls._get_position_str(move_str)
        if pos_str == move_str and any(sign in pos_str for sign in cls._relation_signs):
            return ""
        return pos_str.strip("".join(cls._relation_signs))

    @classmethod
    def _get_position_str(cls, move_str: str) -> str:
        str_parts = move_str.split()

        if len(str_parts) == 1:
            return move_str
        return str_parts[1]


class Hive:
    __slots__ = ("_pieces", "_pieces_str", "_pieces_positions")

    def __init__(self):
        self._pieces = []
        self._pieces_str = set()
        self._pieces_positions = set()

    def add(self, move_str: str) -> None:
        """
        Raises:
            NotValidPieceError: If piece to add from move_str is not a valid piece.
            PieceAlreadyExistsError: If piece to add from move_str is already in the hive.
        """
        piece_str = MoveStringsDecoder.get_piece_to_move(move_str)
        ref_piece_str = MoveStringsDecoder.get_ref_piece(move_str)

        if not self.is_in_hive(ref_piece_str):
            raise PieceNotExistsError
        if not pieces.is_piece_str_valid(piece_str):
            raise NotValidPieceError
        if piece_str in self._pieces_str:
            raise PieceAlreadyExistsError

        self._register_piece(move_str)

    def remove(self, piece_str: str) -> None:
        """
        Raises:
            PieceNotExistsError: If there is no piece in the hive with provided piece_str.
        """
        if not self.is_in_hive(piece_str):
            raise PieceNotExistsError

        for piece in self._pieces:
            if pieces.get_piece_string(piece.info) == piece_str:
                self._unregister_piece(piece)
                break

    def is_in_hive(self, piece_str: str) -> bool:
        return piece_str in self._pieces_str

    def is_position_empty(self, move_str: str) -> bool:
        ref_piece_str = MoveStringsDecoder.get_ref_piece(move_str)
        ref_position = self._get_piece_position(ref_piece_str)
        destination = PositionsResolver.get_destination_position(
            ref_pos=ref_position, move_str=move_str
        )

        return destination in self._pieces_positions

    def _unregister_piece(self, piece: pieces.Piece) -> None:
        if piece.piece_under is not None:
            piece.piece_under.piece_above = piece.piece_above

        if piece.piece_above is not None:
            piece.piece_above.piece_under = piece.piece_under

        self._pieces.remove(piece)
        self._pieces_str.remove(pieces.get_piece_string(piece.info))
        self._pieces_positions.remove(piece.position)

    def _register_piece(self, move_str: str) -> None:
        piece_str = MoveStringsDecoder.get_piece_to_move(move_str)
        position = self._get_adding_position(move_str)

        new_piece = pieces.Piece(
            info=pieces.get_piece_info(piece_str),
            position=position,
            piece_under=None,
            piece_above=None,
        )

        if not self.is_position_empty(move_str):
            top_piece_on_position = self._get_top_piece_on_position(position)

            new_piece.piece_under = top_piece_on_position
            top_piece_on_position.piece_above = new_piece

        self._pieces.append(new_piece)
        self._pieces_str.add(piece_str)
        self._pieces_positions.add(position)

    def _get_adding_position(self, move_str: str) -> tuple[int, int]:
        ref_piece_str = MoveStringsDecoder.get_ref_piece(move_str)
        piece_str = MoveStringsDecoder.get_piece_to_move(move_str)

        if not self._pieces and ref_piece_str == piece_str:
            return (0, 0)

        ref_piece_position = self._get_piece_position(ref_piece_str)
        position = PositionsResolver.get_destination_position(
            ref_piece_position, move_str
        )
        return position

    def _get_piece_position(self, piece_str: str) -> tuple[int, int]:
        """
        Raises:
            PieceNotExistsError: If there is no piece in the hive with provided piece_str.
        """
        for piece in self._pieces:
            if pieces.get_piece_string(piece.info) == piece_str:
                return piece.position

        raise PieceNotExistsError

    def _get_top_piece_on_position(self, position: tuple[int, int]) -> pieces.Piece:
        """
        Raises:
            InvalidPositionError: If there is no piece on the position.
        """
        for piece in self._pieces:
            if piece.position == position:
                while piece.piece_above is not None:
                    piece = piece.piece_above
                return piece

        raise InvalidPositionError
