import math
import queue
from typing import Generator

from honeycomb.engine import hive as h
from honeycomb.engine import notation
from honeycomb.engine import pieces as p


def bee_surrounded(hive: h.Hive, color: notation.PieceColor) -> bool:
    bee_piece_str = notation.PieceString.build(color, notation.BasePieces.BEE, 0)
    if bee_piece_str in hive.pieces_on_board_str(color):
        bee = hive.piece(bee_piece_str)
        positions_around = set(
            h.PositionsResolver.positions_around_clockwise(bee.position)
        )
        occupied = hive.positions()
        return len(positions_around - occupied) == 0
    return False


class MovesProvider:
    __slots__ = "_hive", "_piece_to_moves_generator"

    def __init__(self, hive: h.Hive) -> None:
        self._hive = hive
        self._piece_to_moves_generator = {
            notation.BasePieces.ANT: self.ant_move_positions,
            notation.BasePieces.BEE: self.bee_move_positions,
            notation.BasePieces.BEETLE: self.beetle_move_positions,
            notation.BasePieces.GRASSHOPPER: self.grasshopper_move_positions,
            notation.BasePieces.SPIDER: self.spider_move_positions,
        }

    @property
    def supported_expansions(self) -> set[notation.ExpansionPieces]:
        return {
            e for e in notation.ExpansionPieces
        } & self._piece_to_moves_generator.keys()

    def random_valid_move(self, turn_color: notation.PieceColor, turn_num: int) -> str:
        for piece in self._hive.pieces(turn_color):
            for pos in self.move_positions(piece):
                move_str = self._move_str(piece.piece_str, pos)
                return move_str

        adding_positions = self.adding_positions(turn_color)
        pieces_str_to_add = self.pieces_str_to_add(turn_color, turn_num)
        if adding_positions and pieces_str_to_add:
            move_str = self._move_str(pieces_str_to_add.pop(), adding_positions.pop())
            return move_str
        return "pass"

    def valid_moves(self, turn_color: notation.PieceColor, turn_num: int) -> set[str]:
        valid_moves_str = set()

        for piece in self._hive.pieces(turn_color):
            move_positions = set(self.move_positions(piece))
            for pos in move_positions:
                move_str = self._move_str(piece.piece_str, pos)
                valid_moves_str.add(move_str)

        adding_positions = self.adding_positions(turn_color)
        pieces_str_to_add = self.pieces_str_to_add(turn_color, turn_num)
        for pos in adding_positions:
            for piece_str in pieces_str_to_add:
                move_str = self._move_str(piece_str, pos)
                valid_moves_str.add(move_str)

        if not valid_moves_str:
            return {"pass"}

        return valid_moves_str

    def adding_positions(self, color: notation.PieceColor) -> set[tuple[int, int]]:
        player_pos = self._hive.positions(color)
        opponent_pos = self._hive.positions(_opponent_color(color))

        if not player_pos:
            if not opponent_pos:
                return {self._hive.start_position}

            return set(
                h.PositionsResolver.positions_around_clockwise(opponent_pos.pop())
            )

        positions_around_player = set()
        for pos in player_pos:
            positions_around_player |= set(
                h.PositionsResolver.positions_around_clockwise(pos)
            )

        positions_around_opponent = set()
        for pos in opponent_pos:
            positions_around_opponent |= set(
                h.PositionsResolver.positions_around_clockwise(pos)
            )

        return (
            positions_around_player
            - (player_pos | opponent_pos)
            - positions_around_opponent
        )

    def move_positions(self, piece: p.Piece) -> Generator[tuple[int, int], None, None]:
        color, ptype, *_ = notation.PieceString.decompose(piece.piece_str)
        if (
            piece.piece_above is not None
            or self.is_onehive_broken(piece)
            or not self._hive.is_bee_on_board(color)
        ):
            return
        occupied = set(self._hive.positions())
        occupied.remove(piece.position)
        yield from self._piece_to_moves_generator[ptype](piece.position, occupied)  # type: ignore

    def pieces_str_to_add(
        self, turn_color: notation.PieceColor, turn_num: int
    ) -> set[str]:
        if not self._hive.is_bee_on_board(turn_color) and turn_num == 4:
            bee_str = notation.PieceString.build(turn_color, notation.BasePieces.BEE, 0)
            return {bee_str}
        pieces_in_hand_str = self._hive.pieces_in_hand_str(turn_color)
        ptype_to_piece_str = {}
        for piece_str in pieces_in_hand_str:
            _, ptype, *_ = notation.PieceString.decompose(piece_str)
            if ptype not in ptype_to_piece_str:
                ptype_to_piece_str[ptype] = set()
            ptype_to_piece_str[ptype].add(piece_str)

        pieces_str_to_add = {
            piece_strs.pop() if len(piece_strs) == 1 else min(piece_strs)
            for piece_strs in ptype_to_piece_str.values()
        }
        return pieces_str_to_add

    def is_onehive_broken(self, piece: p.Piece) -> bool:
        if piece.piece_under is not None:
            return False

        occupied = self._hive.positions()
        pos_around = set(h.PositionsResolver.positions_around_clockwise(piece.position))
        neighbours = pos_around & occupied
        start = neighbours.pop()
        steps_count = 0
        frontier = queue.PriorityQueue()
        frontier.put((0, (steps_count, start)))
        visited = {piece.position}

        return not self._hive_search(
            frontier=frontier,
            visited=visited,
            occupied=occupied,
            targets=neighbours,
            heuristic_target=piece.position,
        )

    def _hive_search(
        self,
        frontier: queue.PriorityQueue,
        visited: set[tuple[int, int]],
        occupied: set[tuple[int, int]],
        targets: set[tuple[int, int]],
        heuristic_target: tuple[int, int],
    ) -> bool:
        """Returns True if found all targets or if targets where empty."""
        if frontier.empty():
            return False

        _, (steps_count, position) = frontier.get()
        visited.add(position)

        if position in targets:
            targets.remove(position)

        if not targets:
            return True

        if visited == occupied:
            return False

        pos_around = set(h.PositionsResolver.positions_around_clockwise(position))
        to_explore = (pos_around & occupied) - visited

        for pos in to_explore:
            score = self._search_heuristic(pos, heuristic_target) + steps_count + 1
            frontier.put((score, (steps_count + 1, pos)))

        return self._hive_search(frontier, visited, occupied, targets, heuristic_target)

    def _move_str(self, piece_str, target_position: tuple[int, int]) -> str:  # type: ignore
        if not self._hive.positions():
            return notation.MoveString.build(piece_str)

        positions_on_board = self._hive.positions()
        for pos_around in h.PositionsResolver.positions_around_clockwise(
            target_position
        ):
            if pos_around in positions_on_board:
                for ref_piece in self._hive.pieces():
                    if (
                        ref_piece.position == pos_around
                        and ref_piece.piece_str != piece_str
                    ):
                        relation = h.PositionsResolver.relation(
                            target_position, pos_around
                        )
                        move_str = notation.MoveString.build(
                            piece_str, relation, ref_piece.piece_str
                        )
                        return move_str

    def _search_heuristic(self, current: tuple[int, int], target: tuple[int, int]):
        return math.sqrt(sum(((t - c) ** 2 for t, c in zip(target, current))))

    def ant_move_positions(
        self,
        position: tuple[int, int],
        occupied: set[tuple[int, int]],
        explored: set[tuple[int, int]] | None = None,
    ) -> Generator[tuple[int, int], None, None]:
        if explored is None:
            explored = set()
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
    ) -> Generator[tuple[int, int], None, None]:
        around_clockwise = h.PositionsResolver.positions_around_clockwise(position)

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
    ) -> Generator[tuple[int, int], None, None]:
        height_under_beetle = self._hive.stack_height(position) - 1
        around_clockwise = h.PositionsResolver.positions_around_clockwise(position)

        prev_around = around_clockwise[-2]
        curr_around = around_clockwise[-1]
        prev_height = self._hive.stack_height(prev_around)
        curr_height = self._hive.stack_height(curr_around)
        next_height = None
        for i in range(len(around_clockwise)):
            next_around = around_clockwise[i]

            if {prev_around, curr_around, next_around} & occupied:
                next_height = self._hive.stack_height(next_around)

                if min(prev_height, next_height) <= max(
                    height_under_beetle, curr_height
                ):
                    yield curr_around
            else:
                next_height = 0

            prev_height = curr_height
            curr_height = next_height
            prev_around = curr_around
            curr_around = next_around

    def grasshopper_move_positions(
        self, position: tuple[int, int], occupied: set[tuple[int, int]]
    ):
        even_rows_offsets = h.PositionsResolver.even_offsets_clockwise()
        odd_rows_offsets = h.PositionsResolver.odd_offsets_clockwise()
        offsets = (odd_rows_offsets, even_rows_offsets)

        offsets_idx = 0
        if h.PositionsResolver.is_row_even(position):
            offsets_idx = 1

        for i in range(len(even_rows_offsets)):
            curr_offset = offsets[offsets_idx][i]
            curr_position = h.sum_tuple_elem_wise(position, curr_offset)
            if curr_position in occupied:
                curr_offsets_idx = offsets_idx
                landing_position = curr_position
                while landing_position in occupied:
                    curr_offsets_idx = (curr_offsets_idx + 1) % 2
                    curr_offset = offsets[curr_offsets_idx][i]
                    landing_position = h.sum_tuple_elem_wise(
                        landing_position, curr_offset
                    )
                yield landing_position

    def spider_move_positions(
        self,
        position: tuple[int, int],
        occupied: set[tuple[int, int]],
        explored: set[tuple[int, int]] | None = None,
        step_counter: int = 0,
    ) -> Generator[tuple[int, int], None, None]:
        if explored is None:
            explored = set()
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


def _opponent_color(color: notation.PieceColor):
    return (
        notation.PieceColor.WHITE
        if color == notation.PieceColor.BLACK
        else notation.PieceColor.BLACK
    )
