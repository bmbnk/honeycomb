from hive.engine import err, logic, notation
from hive.engine.hive import Hive, PositionsResolver

_STARTING_COLOR = notation.PieceColor.WHITE


class GameError(err.BaseEngineError):
    pass


class InvalidMove(GameError):
    pass


class InvalidPieceColor(InvalidMove):
    def __init__(self, turn_color: notation.PieceColor):
        self.message = (
            f"Invalid piece color. Now it's {turn_color.name.lower()}'s turn."
        )


class InvalidExpansionPieceError(GameError):
    def __init__(self, piece_str: str, gametype: str):
        self.message = (
            f"Not valid expansion piece: {piece_str} for the game of type: {gametype}."
        )


class InvalidAddingPieceError(InvalidMove):
    def __init__(self, piece_str: str, pieces_to_add: set[str]):
        self.message = f"Invalid piece to add: {piece_str}. List of pieces that can be added: {', '.join([piece_str for piece_str in pieces_to_add])}."


class InvalidAddingPositionError(InvalidMove):
    def __init__(self, move_str: str):
        self.message = f"Invalid adding position: {move_str}."


class InvalidMovingPieceError(InvalidMove):
    def __init__(self, piece_str: str, pieces_on_board_str: set[str]):
        self.message = f"Invalid piece to move: {piece_str}. List of pieces that can be moved: {', '.join([piece_str for piece_str in pieces_on_board_str])}."


class InvalidMovingPositionError(InvalidMove):
    def __init__(self, move_str: str):
        self.message = f"Invalid moving position: {move_str}."


class NotSupportedExpansionPieceError(GameError):
    def __init__(self, expansions: set[notation.ExpansionPieces]):
        self.message = f"Not supported expansion pieces: {', '.join([e.name for e in expansions])}."


class GameNotPossibleError(GameError):
    def __init__(self, reason: str):
        self.message = f"Not valid game entry. {reason}"


class GameTerminatedError(GameError):
    def __init__(self):
        self.message = (
            'The game has terminated. Use the "newgame" command to start a new game.'
        )


class PassMoveNotAllowedError(InvalidMove):
    def __init__(self, validmoves):
        self.message = f"The pass move is not a valid move if there are possible moves available: {', '.join(validmoves)}."


class Game:
    __slots__ = (
        "_expansions",
        "_hive",
        "_moves_provider",
        "_moves",
        "_state",
        "_turn_color",
        "_turn_num",
    )

    def __init__(self):
        self._init_new_game()

    @property
    def status(self) -> str:
        return notation.GameString.build(
            expansions=self._expansions,
            gamestate=self._state,
            turn_num=self._turn_num,
            turn_color=self._turn_color,
            moves=self._moves,
        )

    def best_move(self):
        pass

    def load_game(self, game_str: str) -> None:
        (
            expansions,
            gamestate,
            turn_color,
            turn_num,
            moves,
        ) = notation.GameString.decompose(game_str)

        self._init_new_game(expansions)
        for move in moves:
            self.play(move)

        err_msg = None
        if gamestate != self._state:
            err_msg = f"Provided game state: '{gamestate.name}' is not correct for moves: {'; '.join(moves)}. It should be: '{self._state.name}'"
        if turn_color != self._turn_color:
            err_msg = f"Provided turn color: '{turn_color.name.capitalize()}' is not correct for moves: {'; '.join(moves)}. It should be: '{self._turn_color.name.capitalize()}'"
        if turn_num != self._turn_num:
            err_msg = f"Provided turn number: '{turn_num}' is not correct for moves: {'; '.join(moves)}. It should be: '{self._turn_num}'"

        if err_msg is not None:
            self._init_new_game()
            raise GameNotPossibleError(err_msg)

    def new_game(self, gametype_str: str = "Base"):
        expansions = notation.GameTypeString.decompose(gametype_str)
        self._init_new_game(expansions)

    def play(self, move_str: str):
        """
        Raises:
            GameTerminatedError: If the game is over.
            InvalidAddingPositionError: If adding position is not valid.
            InvalidMovingPositionError: If moving position is not valid.
            InvalidPieceColor: If the color of action piece is different then turn color.
            InvalidMoveStringError: If move string is not valid
            PassMoveNotAllowedError: If pass has played while valid moves existing.
        """
        # TODO: Implement better validation logic then calculating all possible moves

        if self._state not in [
            notation.GameState.NotStarted,
            notation.GameState.InProgress,
        ]:
            raise GameTerminatedError

        move_str_parts = notation.MoveString.decompose(move_str)
        piece_str = move_str_parts[0]

        if piece_str is None:
            self._pass_move()
        else:
            color, *_ = notation.PieceString.decompose(piece_str)
            if piece_str in self._hive.pieces_in_hand_str(
                color
            ) and piece_str in self._moves_provider.pieces_str_to_add(
                self._turn_color, self._turn_num
            ):
                self._add(move_str)
            elif piece_str in self._hive.pieces_on_board_str(color):
                self._move(move_str)
            else:
                self._raise_invalid_add_piece_error(piece_str)

        self._moves.append(move_str)
        self._next_turn()

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
        self._state = (
            notation.GameState.InProgress
            if self._moves
            else notation.GameState.NotStarted
        )

    def valid_moves(self) -> set[str]:
        return self._moves_provider.valid_moves(self._turn_color, self._turn_num)

    def _add(self, move_str: str):
        move_str_parts = notation.MoveString.decompose(move_str)

        assert move_str_parts[0] is not None

        if len(move_str_parts) == 1 and not self._hive.pieces_on_board_str():
            piece_str = move_str_parts[0]
            self._hive.add(piece_str)
            return

        assert len(move_str_parts) == 3

        piece_str, relation, ref_piece_str = move_str_parts
        color, *_ = notation.PieceString.decompose(piece_str)
        if ref_piece_str in self._hive.pieces_on_board_str():
            destination = self._destination(ref_piece_str, relation)
            adding_positions = self._moves_provider.adding_positions(color)
            if destination in adding_positions:
                self._hive.add(piece_str, destination)
                return

        raise InvalidAddingPositionError(
            notation.MoveString.build(piece_str, relation, ref_piece_str)
        )

    def _change_turn_color(self):
        if self._turn_color == notation.PieceColor.WHITE:
            self._turn_color = notation.PieceColor.BLACK
        else:
            self._turn_color = notation.PieceColor.WHITE

    def _destination(self, ref_piece_str: str, relation: str):
        ref_piece = self._hive.piece(ref_piece_str)
        destination = PositionsResolver.destination_position(
            ref_piece.position, relation
        )
        return destination

    def _init_new_game(self, expansions: set[notation.ExpansionPieces] | None = None):
        if expansions is None:
            expansions = set()
        self._state = notation.GameState.NotStarted
        self._moves = []
        self._turn_color = _STARTING_COLOR
        self._turn_num = 1
        self._expansions = expansions
        self._hive = Hive(self._expansions)
        self._moves_provider = logic.MovesProvider(self._hive)

        if not expansions.issubset(self._moves_provider.supported_expansions):
            self._hive = Hive()
            self._moves_provider = logic.MovesProvider(self._hive)
            raise NotSupportedExpansionPieceError(expansions)

    def _raise_invalid_add_piece_error(self, piece_str: str):
        color, ptype, *_ = notation.PieceString.decompose(piece_str)
        if (
            isinstance(ptype, notation.ExpansionPieces)
            and ptype not in self._expansions
        ):
            raise InvalidExpansionPieceError(
                piece_str, notation.GameTypeString.build(self._expansions)
            )
        if color != self._turn_color:
            raise InvalidPieceColor(self._turn_color)
        if piece_str not in self._hive.pieces_in_hand_str(color):
            raise InvalidAddingPieceError(
                piece_str,
                self._moves_provider.pieces_str_to_add(
                    self._turn_color, self._turn_num
                ),
            )

    def _move(self, move_str: str):
        move_str_parts = notation.MoveString.decompose(move_str)
        assert len(move_str_parts) == 3

        piece_str, relation, ref_piece_str = move_str_parts

        if relation is None:
            raise InvalidMovingPositionError(piece_str)

        if ref_piece_str is not None:
            piece = self._hive.piece(piece_str)
            ref_piece = self._hive.piece(ref_piece_str)
            destination = PositionsResolver.destination_position(
                ref_piece.position, relation
            )
            if destination in self._moves_provider.move_positions(piece):
                self._hive.move(piece_str, destination)
                return
            raise InvalidMovingPositionError(relation.replace(".", ref_piece_str))
        raise InvalidMovingPositionError(piece_str)

    def _next_turn(self):
        self._update_gamestate()
        self._change_turn_color()
        if self._turn_color == _STARTING_COLOR:
            self._turn_num += 1

    def _pass_move(self):
        validmoves = self.valid_moves()
        if validmoves:
            raise PassMoveNotAllowedError(validmoves)

    def _update_gamestate(self):
        black_bee_surrounded = logic.bee_surrounded(
            self._hive, notation.PieceColor.BLACK
        )
        white_bee_surrounded = logic.bee_surrounded(
            self._hive, notation.PieceColor.WHITE
        )

        if black_bee_surrounded and white_bee_surrounded:
            self._state = notation.GameState.Draw
        elif white_bee_surrounded:
            self._state = notation.GameState.BlackWins
        elif black_bee_surrounded:
            self._state = notation.GameState.WhiteWins
        elif self._moves:
            self._state = notation.GameState.InProgress
