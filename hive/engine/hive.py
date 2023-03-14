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


class HiveError(Exception):
    pass


class PositionNotEmptyError(HiveError):
    pass


class PieceNotExistsError(HiveError):
    pass


class Hive:
    __slots__ = (
        "_pieces",
        "_pieces_str",
        "_pieces_positions",
        "_even_row_relations",
    )

    def __init__(self):
        self._pieces = []
        self._pieces_str = set()
        self._pieces_positions = set()
        self._even_row_relations = (
            ("./", (1, -1)),
            (".-", (1, 0)),
            (".\\", (1, 1)),
            ("/.", (0, 1)),
            ("-.", (-1, 0)),
            ("\.", (0, -1)),
        )

    def add(self, piece_str: str):
        pass

    def remove(self, piece_str: str):
        pass

    def is_in_hive(self, piece_str: str):
        pass

    def is_position_empty(self, position: tuple[int, int, int]):
        pass
