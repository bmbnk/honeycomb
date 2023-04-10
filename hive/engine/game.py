from hive.engine import err, logic, notation, pieces
from hive.engine.hive import Hive, PositionsResolver

_STARTING_COLOR = notation.PieceColor.WHITE


class GameError(err.BaseEngineError):
    pass


class InvalidMove(GameError):
    pass


class InvalidPieceColor(InvalidMove):
    def __init__(self, turn_color):
        self.message = (
            f"Invalid piece color. Now it's {turn_color.name.lower()}'s turn."
        )


class InvalidAddingPositionError(InvalidMove):
    def __init__(self, position):
        self.message = f"Invalid adding position: {position}."


class InvalidMovingPositionError(InvalidMove):
    def __init__(self, position):
        self.message = f"Invalid moving position: {position}."


class NotSupportedExpansionPieceError(GameError):
    def __init__(self, expansions):
        self.message = f"Not supported expansion pieces: {', '.join([e.name for e in expansions])}."


class Game:
    __slots__ = (
        "_hive",
        "_moves",
        "_moves_provider",
        "_state",
        "_turn_color",
        "_turn_num",
    )

    def __init__(self):
        self.new_game()

    @property
    def status(self) -> str:
        return notation.GameString.build(
            expansions=set(),
            gamestate=self._state,
            turn_num=self._turn_num,
            turn_color=self._turn_color,
            moves=self._moves,
        )

    def best_move(self):
        pass

    def new_game(self, gametype_str: str = "Base"):
        expansions = notation.GameTypeString.decompose(gametype_str)
        if expansions:
            raise NotSupportedExpansionPieceError(expansions)
        self._state = notation.GameState.NotStarted
        self._moves = []
        self._turn_color = _STARTING_COLOR
        self._turn_num = 1
        self._hive = Hive()
        self._moves_provider = logic.MovesProvider(self._hive)

    def load_game(self, game_str: str) -> None:
        (
            expansions,
            gamestate,
            turn_color,
            turn_num,
            moves,
        ) = notation.GameString.decompose(game_str)
        if expansions:
            raise NotSupportedExpansionPieceError(expansions)
        self._state = notation.GameState.NotStarted
        self._moves = []
        self._turn_color = _STARTING_COLOR
        self._turn_num = 1
        self._hive = Hive()
        self._moves_provider = logic.MovesProvider(self._hive)

    def pass_move(self):
        if self.valid_moves():
            raise InvalidMove(
                "The pass move is not a valid move if there are possible moves available."
            )
        self._next_turn()

    def play(self, move_str: str):
        """
        Raises:
            InvalidAddingPositionError: If adding position is not valid.
            InvalidMovingPositionError: If moving position is not valid.
        """
        # TODO: Implement better validation logic then calculating all possible moves

        piece_str, relation, ref_piece_str = notation.MoveString.decompose(move_str)

        if piece_str is not None:
            color, *_ = notation.PieceString.decompose(piece_str)
            if color != self._turn_color:
                raise InvalidPieceColor(self._turn_color)

        if piece_str is None:
            self.pass_move()
        elif piece_str in self._hive.pieces_in_hand_str():
            self._add(piece_str, relation, ref_piece_str)
        else:
            self._move(piece_str, relation, ref_piece_str)

        self._moves.append(move_str)

    def _add(self, piece_str: str, relation: str | None, ref_piece_str: str | None):
        if relation is None and not self._hive.pieces_on_board_str():
            self._hive.add(piece_str)
            self._next_turn()
            return

        color, *_ = notation.PieceString.decompose(piece_str)
        opponent_color = (
            notation.PieceColor.BLACK
            if color == notation.PieceColor.WHITE
            else notation.PieceColor.WHITE
        )

        if (
            relation is not None
            and ref_piece_str is not None
            and ref_piece_str in self._hive.pieces_on_board_str(opponent_color)
        ):
            ref_piece = self._hive.piece(ref_piece_str)
            destination = PositionsResolver.destination_position(
                ref_piece.position, relation
            )
            adding_positions = self._moves_provider.adding_positions(color)
            if destination in adding_positions:
                self._hive.add(piece_str, destination)
                self._next_turn()
                return

        raise InvalidAddingPositionError(
            notation.MoveString.build(piece_str, relation, ref_piece_str)
        )

    def _move(self, piece_str: str, relation: str, ref_piece_str: str | None):
        if ref_piece_str is not None:
            piece = self._hive.piece(piece_str)
            ref_piece = self._hive.piece(ref_piece_str)
            destination = PositionsResolver.destination_position(
                ref_piece.position, relation
            )
            if destination in self._moves_provider.move_positions(piece):
                self._hive.move(piece_str, destination)
                self._next_turn()
                return
            raise InvalidMovingPositionError(relation.replace(".", ref_piece_str))
        raise InvalidMovingPositionError(piece_str)

    def undo(self, to_undo: int) -> None:
        if self._state == notation.GameState.NotStarted or to_undo < 1:
            return

        self._turn_num -= to_undo // 2

        if to_undo % 2 == 1:
            if self._turn_color == _STARTING_COLOR:
                self._turn_num -= 1
            self._change_turn_color()

        if self._turn_num < 1:
            self.new_game()
            return

        self._hive.undo(to_undo)
        self._moves = self._moves[:-to_undo]
        self._state = notation.GameState.InProgress

    def valid_moves(self) -> set[str]:
        valid_moves_str = set()

        if not self._hive.is_bee_on_board(self._turn_color) and self._turn_num == 4:
            adding_positions = self._moves_provider.adding_positions(self._turn_color)
            bee_str = notation.PieceString.build(
                self._turn_color, notation.PieceType.BEE, 0
            )
            for pos in adding_positions:
                move_str = self._move_str(bee_str, pos)
                valid_moves_str.add(move_str)
            return valid_moves_str

        for piece in self._hive.pieces(self._turn_color):
            move_positions = set(self._moves_provider.move_positions(piece))
            piece_str = notation.PieceString.build(
                piece.info.color, piece.info.ptype, piece.info.num
            )
            for pos in move_positions:
                move_str = self._move_str(piece_str, pos)
                valid_moves_str.add(move_str)

        adding_positions = self._moves_provider.adding_positions(self._turn_color)
        for pos in adding_positions:
            for piece_str in self._hive.pieces_in_hand_str(self._turn_color):
                move_str = self._move_str(piece_str, pos)
                valid_moves_str.add(move_str)

        return valid_moves_str

    def _move_str(self, piece_str, target_position: tuple[int, int]) -> str:  # type: ignore
        if target_position == self._hive.start_position:
            return notation.MoveString.build(piece_str)

        positions_on_board = self._hive.positions()
        for pos_around in PositionsResolver.positions_around_clockwise(target_position):
            if pos_around in positions_on_board:
                for piece in self._hive.pieces():
                    if piece.position == pos_around:
                        relation = PositionsResolver.relation(
                            target_position, pos_around
                        )
                        ref_piece_str = notation.PieceString.build(
                            piece.info.color, piece.info.ptype, piece.info.num
                        )
                        move_str = notation.MoveString.build(
                            piece_str, relation, ref_piece_str
                        )
                        return move_str

    def _change_turn_color(self):
        if self._turn_color == notation.PieceColor.WHITE:
            self._turn_color = notation.PieceColor.BLACK
        else:
            self._turn_color = notation.PieceColor.WHITE

    def _next_turn(self):
        # TODO: check for the game end first
        if self._state == notation.GameState.NotStarted:
            self._state = notation.GameState.InProgress

        self._change_turn_color()
        if self._turn_color == _STARTING_COLOR:
            self._turn_num += 1
