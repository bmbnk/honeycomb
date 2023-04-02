from typing import Generator

from hive.engine import hive as h
from hive.engine import pieces as p


class MovesProvider:
    __slots__ = "_hive", "_piece_to_moves_generator"

    def __init__(self, hive: h.Hive) -> None:
        self._hive = hive
        self._piece_to_moves_generator = {
            p.PieceType.ANT: self.ant_move_positions,
            p.PieceType.BEE: self.bee_move_positions,
            p.PieceType.BEETLE: self.beetle_move_positions,
            p.PieceType.GRASSHOPPER: self.grasshopper_move_positions,
            p.PieceType.SPIDER: self.spider_move_positions,
        }

    def adding_positions(self, color: p.PieceColor) -> set[tuple[int, int]]:
        player_pos = self._hive.positions(color)
        opponent_pos = self._hive.positions(
            p.PieceColor.WHITE if color == p.PieceColor.BLACK else p.PieceColor.BLACK
        )

        if not player_pos:
            if not opponent_pos:
                return {(0, 0)}

            return set(self.positions_around_clockwise(opponent_pos.pop()))

        positions_around_player_positions = set()
        for pos in player_pos:
            positions_around_player_positions |= set(
                self.positions_around_clockwise(pos)
            )

        positions_around_opponent_positions = set()
        for pos in opponent_pos:
            positions_around_opponent_positions |= set(
                self.positions_around_clockwise(pos)
            )

        return (
            positions_around_player_positions
            - (player_pos | opponent_pos)
            - positions_around_opponent_positions
        )

    def move_positions(self, piece: p.Piece):
        if piece.piece_under is not None or self.is_onehive_broken(piece.position):
            return
        yield from self._piece_to_moves_generator[piece.info.ptype](
            piece.position, self._hive.positions()
        )

    def is_onehive_broken(self, position: tuple[int, int]) -> bool:
        ...

    def ant_move_positions(
        self,
        position: tuple[int, int],
        occupied: set[tuple[int, int]],
        explored: set[tuple[int, int]] = set(),
    ) -> Generator:
        explored.add(position)

        next_steps = self.bee_move_positions(position, occupied)
        to_explore = (pos for pos in next_steps if pos not in explored)
        next_position = None

        for pos in to_explore:
            yield pos
            next_position = pos

        if next_position is not None:
            yield from self.ant_move_positions(next_position, occupied, explored)

    def bee_move_positions(
        self, position: tuple[int, int], occupied: set[tuple[int, int]]
    ) -> Generator:
        around_clockwise = self.positions_around_clockwise(position)

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

    def beetle_move_positions(
        self, position: tuple[int, int], occupied: set[tuple[int, int]]
    ):
        ...

    def grasshopper_move_positions(
        self, position: tuple[int, int], occupied: set[tuple[int, int]]
    ):
        ...

    def spider_move_positions(
        self,
        position: tuple[int, int],
        occupied: set[tuple[int, int]],
        explored: set = set(),
        step_counter: int = 0,
    ) -> Generator:
        explored.add(position)

        next_steps = self.bee_move_positions(position, occupied)
        to_explore = (pos for pos in next_steps if pos not in explored)

        for pos in to_explore:
            if step_counter < 2:
                yield from self.spider_move_positions(
                    pos, occupied, explored, step_counter + 1
                )
            else:
                yield pos

    def positions_around_clockwise(
        self, position: tuple[int, int]
    ) -> list[tuple[int, int]]:
        return list(
            (position[0] + offset[0], position[1] + offset[1])
            for offset in h.PositionsResolver.move_offsets_clockwise(position)
        )
