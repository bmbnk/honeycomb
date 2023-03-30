from hive.engine import hive as h
from hive.engine import pieces as p


def adding_positions(hive: h.Hive, color: p.PieceColor) -> set[tuple[int, int]]:
    player_pos = hive.positions(color)
    opponent_pos = hive.positions(
        p.PieceColor.WHITE if color == p.PieceColor.BLACK else p.PieceColor.BLACK
    )

    if not player_pos:
        if not opponent_pos:
            return {(0, 0)}

        return positions_around(opponent_pos.pop())

    positions_around_player_positions = set()
    for pos in player_pos:
        positions_around_player_positions |= positions_around(pos)

    positions_around_opponent_positions = set()
    for pos in opponent_pos:
        positions_around_opponent_positions |= positions_around(pos)

    return (
        positions_around_player_positions
        - (player_pos | opponent_pos)
        - positions_around_opponent_positions
    )


def positions_around(position: tuple[int, int]) -> set[tuple[int, int]]:
    return set(
        h.sum_tuple_elem_wise(position, offset)
        for offset in h.PositionsResolver.move_offsets(position)
    )
