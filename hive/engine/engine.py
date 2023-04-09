import time
from typing import Callable

from hive.engine import err, notation
from hive.engine.game import Game

_MAX_TIME_FORMAT = "%H:%M:%S"
_ENGINE_NAME = "EngineName"
_VERSION = "1.0"


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


class EngineCommandExecutor:
    """Provides UHP engine command responses."""

    __slots__ = "_cmd_completion_str", "_cmd_to_method", "_engine"

    def __init__(self) -> None:
        self._cmd_completion_str = "ok"
        self._engine = Engine()
        self._cmd_to_method = {
            "bestmove": self._engine.bestmove,
            "info": self._engine.info,
            "newgame": self._engine.newgame,
            "options": self._engine.options,
            "pass": self._engine.pass_,
            "play": self._engine.play,
            "undo": self._engine.undo,
            "validmoves": self._engine.validmoves,
        }

    def execute(self, inp) -> str:
        return self._response(inp)

    def _response(self, inp) -> str:
        try:
            result = self._cmd_result(inp)
        except err.BaseEngineError as e:
            result = str(e)

        return f"{result}\n{self._cmd_completion_str}"

    def _cmd_result(self, inp) -> str:
        command, *params = inp.split()
        method = self._method(command)
        if params:
            params_str = " ".join(params)
            return method(params_str)
        else:
            return method()

    def _method(self, command: str) -> Callable[..., str]:
        if command not in self._cmd_to_method:
            raise InvalidCommand(command)

        return self._cmd_to_method[command]


class Engine:
    """Executes UHP engine commands."""

    __slots__ = "_game", "_max_time_format", "_name", "_version"

    def __init__(self) -> None:
        self._game = Game()
        self._max_time_format = _MAX_TIME_FORMAT
        self._name = _ENGINE_NAME
        self._version = _VERSION

    def bestmove(self, params: str) -> str:
        param_list = params.split()
        if len(param_list) != 2:
            raise InvalidCommandParametersNumber(len(param_list), 2)

        limit_type, limit_value = param_list

        if limit_type == "depth":
            if not limit_value.isdigit():
                raise InvalidCommandParameters(limit_value)
            return self._bestmove_in_depth(int(limit_value))
        elif limit_type == "time":
            try:
                time_info = time.strptime(limit_value, self._max_time_format)
            except ValueError:
                raise InvalidCommandParameters(limit_value)
            return self._bestmove_in_time(
                time_info.tm_hour, time_info.tm_min, time_info.tm_sec
            )
        raise InvalidCommandParameters(limit_type)

    def info(self, params: str = "") -> str:
        return f"id {self._name} v{self._version}"

    def newgame(self, params: str) -> str:
        if not params:
            self._game.new_game()
        elif notation.GameString.is_valid(params):
            self._game.load_game(params)
        elif notation.GameTypeString.is_valid(params):
            self._game.new_game(params)
        else:
            raise InvalidCommandParameters(params)

        return self._game.status

    def options(self, params: str = ""):
        # TODO: It could be a good option to turn off move validation when training with AI for example
        return ""

    def pass_(self, params: str = "") -> str:
        self.play("pass")
        return self._game.status

    def play(self, params: str) -> str:
        if notation.MoveString.is_valid(params):
            self._game.play(params)
            return self._game.status
        raise InvalidCommandParameters(params)

    def undo(self, params: str) -> str:
        if params.isdigit():
            to_undo = int(params)
            self._game.undo(to_undo)
            return self._game.status
        raise InvalidCommandParameters(params.split())

    def validmoves(self, params: str = ""):
        valid_moves_str = self._game.valid_moves()
        return ";".join(valid_moves_str)

    def _bestmove_in_depth(self, depth: int) -> str:
        return ""

    def _bestmove_in_time(self, hour: int, min: int, sec: int):
        return ""
