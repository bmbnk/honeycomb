from typing import Generator
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

        return set(positions_around_clockwise(opponent_pos.pop()))

    positions_around_player_positions = set()
    for pos in player_pos:
        positions_around_player_positions |= set(positions_around_clockwise(pos))

    positions_around_opponent_positions = set()
    for pos in opponent_pos:
        positions_around_opponent_positions |= set(positions_around_clockwise(pos))

    return (
        positions_around_player_positions
        - (player_pos | opponent_pos)
        - positions_around_opponent_positions
    )


def move_positions(position: tuple[int, int], hive: h.Hive, piece_type: p.PieceType):
    return PIECE_TO_MOVE[piece_type](position, hive.positions())


def ant_move_positions(
    position: tuple[int, int],
    occupied: set[tuple[int, int]],
    explored: set[tuple[int, int]] = set(),
) -> Generator:
    explored.add(position)

    next_steps = bee_move_positions(position, occupied)
    to_explore = (pos for pos in next_steps if pos not in explored)
    next_position = None

    for pos in to_explore:
        yield pos
        next_position = pos

    if next_position is not None:
        yield from ant_move_positions(next_position, occupied, explored)


def bee_move_positions(
    position: tuple[int, int], occupied: set[tuple[int, int]]
) -> Generator:
    around_clockwise = positions_around_clockwise(position)

    prev_around = around_clockwise[-2]
    for i in range(len(around_clockwise)):
        curr_around = around_clockwise[i - 1]

        if curr_around not in occupied:
            next_around = around_clockwise[i]
            if (prev_around in occupied and next_around not in occupied) or (
                prev_around not in occupied and next_around in occupied
            ):
                yield curr_around

        prev_around = curr_around


def beetle_move_positions(position: tuple[int, int], occupied: set[tuple[int, int]]):
    ...


def grasshopper_move_positions(
    position: tuple[int, int], occupied: set[tuple[int, int]]
):
    ...


def spider_move_positions(
    position: tuple[int, int],
    occupied: set[tuple[int, int]],
    explored: set = set(),
    step_counter: int = 0,
) -> Generator:
    explored.add(position)

    next_steps = bee_move_positions(position, occupied)
    to_explore = (pos for pos in next_steps if pos not in explored)

    for pos in to_explore:
        if step_counter < 2:
            yield from spider_move_positions(pos, occupied, explored, step_counter + 1)
        else:
            yield pos


def positions_around_clockwise(position: tuple[int, int]) -> list[tuple[int, int]]:
    return list(
        (position[0] + offset[0], position[1] + offset[1])
        for offset in h.PositionsResolver.move_offsets_clockwise(position)
    )


PIECE_TO_MOVE = {
    p.PieceType.ANT: ant_move_positions,
    p.PieceType.BEE: bee_move_positions,
    p.PieceType.BEETLE: beetle_move_positions,
    p.PieceType.GRASSHOPPER: grasshopper_move_positions,
    p.PieceType.SPIDER: spider_move_positions,
}