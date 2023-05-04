import time
from typing import Callable

from honeycomb import _version
from honeycomb.engine import err, notation
from honeycomb.engine.game import Game

MAX_TIME_FORMAT = "%H:%M:%S"
ENGINE_NAME = "honeycomb"


class EngineError(err.BaseEngineError):
    pass


class InvalidCommand(EngineError):
    def __init__(self, cmd):
        self.message = f"Command: '{cmd}' is not valid."


class InvalidCommandParameters(EngineError):
    def __init__(self, parameters):
        self.message = f"Invalid command parameters: '{parameters}'."


class InvalidCommandParametersNumber(EngineError):
    def __init__(self, actual, valid):
        self.message = (
            f"Invalid number of command parameters: '{actual}'. Shuold be: {valid}."
        )


class Engine:
    """Provides UHP engine API."""

    __slots__ = "_cmd_completion_str", "_game", "_cmd_func_mapper"

    def __init__(self) -> None:
        self._cmd_completion_str = "ok"
        self._cmd_func_mapper = CommandFunctionMapper()
        self._game = Game()

    def execute(self, inp) -> str:
        """Executes UHP commands and outputs response"""
        return self._response(inp)

    def _response(self, inp) -> str:
        try:
            result = self._cmd_result(inp)
        except err.BaseEngineError as e:
            result = str(e)

        return f"{result}\n{self._cmd_completion_str}"

    def _cmd_result(self, inp) -> str:
        command, *params = inp.split()
        cmd_func = self._cmd_func_mapper[command]
        params_str = " ".join(params)
        return cmd_func(self._game, params_str)


class CommandFunctionMapper:
    def __init__(self) -> None:
        self._cmd_to_method = {
            "bestmove": _bestmove,
            "info": _info,
            "newgame": _newgame,
            "options": _options,
            "pass": _pass,
            "play": _play,
            "undo": _undo,
            "validmoves": _validmoves,
        }
        self._game_dependent_methods = {
            _bestmove,
            _newgame,
            _pass,
            _play,
            _undo,
            _validmoves,
        }
        self._params_dependent_methods = {
            _bestmove,
            _newgame,
            _options,
            _play,
            _undo,
        }

    def __getitem__(self, command) -> Callable[[Game, str], str]:
        method = self._method(command)

        def cmd_func(game: Game, params: str):
            args = []
            if method in self._game_dependent_methods:
                args.append(game)
            if method in self._params_dependent_methods:
                args.append(params)
            elif params:
                raise InvalidCommandParameters(params)

            return method(*args)

        return cmd_func

    def _method(self, command: str) -> Callable[..., str]:
        if command not in self._cmd_to_method:
            raise InvalidCommand(command)

        return self._cmd_to_method[command]


def _bestmove(game: Game, params: str) -> str:
    param_list = params.split()
    if len(param_list) != 2:
        raise InvalidCommandParametersNumber(len(param_list), 2)

    limit_type, limit_value = param_list

    if limit_type == "depth":
        if not limit_value.isdigit():
            raise InvalidCommandParameters(limit_value)
        return _bestmove_in_depth(game, int(limit_value))
    elif limit_type == "time":
        try:
            time_info = time.strptime(limit_value, MAX_TIME_FORMAT)
        except ValueError:
            raise InvalidCommandParameters(limit_value)
        return _bestmove_in_time(
            game, time_info.tm_hour, time_info.tm_min, time_info.tm_sec
        )
    raise InvalidCommandParameters(limit_type)


def _info() -> str:
    return f"id {ENGINE_NAME} v{_version.__version__}"


def _newgame(game: Game, params: str) -> str:
    if not params:
        game.new_game()
    elif notation.GameString.is_valid(params):
        game.load_game(params)
    elif notation.GameTypeString.is_valid(params):
        game.new_game(params)
    else:
        raise InvalidCommandParameters(params)

    return game.status


def _options(params: str):
    # TODO: It could be a good option to turn off move validation when training with AI for example
    return ""


def _pass(game: Game) -> str:
    _play(game, "pass")
    return game.status


def _play(game: Game, params: str) -> str:
    if notation.MoveString.is_valid(params):
        game.play(params)
        return game.status
    raise InvalidCommandParameters(params)


def _undo(game: Game, params: str) -> str:
    if not params:
        params = "1"

    if params.isdigit():
        to_undo = int(params)
        game.undo(to_undo)
        return game.status
    raise InvalidCommandParameters(params.split())


def _validmoves(game: Game):
    valid_moves_str = game.valid_moves()
    return ";".join(valid_moves_str)


def _bestmove_in_depth(game: Game, depth: int) -> str:
    return game.best_move()


def _bestmove_in_time(game: Game, hour: int, min: int, sec: int):
    return game.best_move()
