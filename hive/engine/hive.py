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


class _MoveStringsDecoder:
    _relation_signs = ("/", "-", "\\")
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
    def get_piece_to_move(cls, move_str: str) -> str:
        return move_str.split()[0]

    @classmethod
    def get_ref_piece(cls, move_str: str) -> str:
        pos_str = cls._get_position_str(move_str)
        return pos_str.strip("/-\\")

    @classmethod
    def get_destination_position_2d(
        cls, ref_pos_2d: tuple[int, int], move_str: str
    ) -> tuple[int, int]:
        relation = cls._get_relation(move_str)
        position_2d_offset = cls._get_position_2d_offset(ref_pos_2d, relation)
        return sum_tuple_elem_wise(ref_pos_2d, position_2d_offset)

    @classmethod
    def _get_relation(cls, move_str: str) -> str:
        position_str = cls._get_position_str(move_str)

        for sign in cls._relation_signs:
            if position_str.startswith(sign):
                return f"{sign}."
            elif position_str.endswith(sign):
                return f".{sign}"

        return "."

    @classmethod
    def _get_position_str(cls, move_str: str) -> str:
        str_parts = move_str.split()

        if len(str_parts) == 1:
            return move_str
        return str_parts[1]

    @classmethod
    def _get_position_2d_offset(
        cls, position_2d: tuple[int, int], relation: str
    ) -> tuple[int, int]:
        position_2d_offset = cls._even_row_relations_to_offset[relation]

        if position_2d[1] % 2 == 0 and position_2d_offset[1] != 0:
            position_2d_offset += cls._odd_row_offset

        return position_2d_offset


class Hive:
    __slots__ = ("_pieces", "_pieces_str", "_pieces_positions", "_move_str_decoder")

    def __init__(self):
        self._pieces = []
        self._pieces_str = set()
        self._pieces_positions = set()
        self._move_str_decoder = _MoveStringsDecoder()

    def add(self, move_str: str) -> None:
        piece_to_add = self._move_str_decoder.get_piece_to_move(move_str)

        if not pieces.is_piece_str_valid(piece_to_add):
            raise NotValidPieceError
        if piece_to_add in self._pieces_str:
            raise PieceAlreadyExistsError

        self._register_piece(move_str)

    def remove(self, piece_str: str):
        pass

    def is_in_hive(self, piece_str: str) -> bool:
        return piece_str in self._pieces_str

    def is_position_empty(self, move_str: str) -> bool:
        piece_str = self._move_str_decoder.get_ref_piece(move_str)

        try:
            self._get_piece_position(piece_str)
        except InvalidPositionError:
            return True
        return False

    def _register_piece(self, move_str: str) -> None:
        piece_str = self._move_str_decoder.get_piece_to_move(move_str)
        position = self._get_adding_position(move_str)
        new_piece = pieces.Piece(
            info=pieces.get_piece_info(piece_str), position=position
        )

        self._pieces.append(new_piece)
        self._pieces_str.add(piece_str)
        self._pieces_positions.add(position)

    def _get_adding_position(self, move_str: str) -> tuple[int, int, int]:
        ref_piece_str = self._move_str_decoder.get_ref_piece(move_str)
        piece_str = self._move_str_decoder.get_piece_to_move(move_str)

        try:
            ref_piece_position = self._get_piece_position(ref_piece_str)
            pos_2d = self._move_str_decoder.get_destination_position_2d(
                ref_piece_position[:2], move_str
            )
            position = pos_2d[0], pos_2d[1], self._get_position_height(pos_2d)
            return position
        except InvalidPositionError:
            if ref_piece_str == piece_str and not self._pieces:
                return (0, 0, 0)
            else:
                raise InvalidPositionError

    def _get_piece_position(self, piece_str: str) -> tuple[int, int, int]:
        for piece in self._pieces:
            if pieces.get_piece_string(piece.info) == piece_str:
                return piece.position

        raise InvalidPositionError

    def _get_position_height(self, position_2d: tuple[int, int]) -> int:
        max_height = 0
        for pos in self._pieces_positions:
            if pos[:2] == position_2d and pos[2] >= max_height:
                max_height = pos[2] + 1
        return max_height
