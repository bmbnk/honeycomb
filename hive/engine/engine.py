import time
from typing import Callable

from hive.engine.game import Game

_MAX_TIME_FORMAT = "%H:%M:%S"
_ENGINE_NAME = "EngineName"
_VERSION = "1.0"


class EngineError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"err {self.message}"


class InvalidCommand(EngineError):
    def __init__(self, cmd):
        self.message = f"Command: '{cmd}' is not valid."


class InvalidCommandParameters(EngineError):
    def __init__(self, arguments):
        self.message = f"Invalid command arguments: '{arguments}'."


class EngineCommandExecutor:
    """Provides UHP engine command responses."""

    __slots__ = "_cmd_completion_str", "_cmd_to_method", "_engine"

    def __init__(self) -> None:
        self._cmd_completion_str = "ok"
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
        self._engine = Engine()

    def execute(self, inp) -> str:
        return self._response(inp)

    def _response(self, inp) -> str:
        try:
            result = self._cmd_result(inp)
        except EngineError as e:
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

    def bestmove(self, limit_type: str, limit_value: str) -> str:
        if limit_type == "depth":
            if not limit_value.isdigit():
                raise InvalidCommandParameters(limit_value)
            return self._bestmove_in_depth(int(limit_value))
        elif limit_type == "time":
            try:
                time_info = time.strptime(limit_value, self._max_time_format)
            except ValueError:
                raise InvalidCommandParameters((limit_value))
            return self._bestmove_in_time(
                time_info.tm_hour, time_info.tm_min, time_info.tm_sec
            )
        else:
            raise InvalidCommandParameters(limit_type)

    def info(self) -> str:
        return f"id {self._name} v{self._version}"

    def newgame(self, game_info: str = "") -> str:
        self._game.new_game()
        return self._game.status

    def options(self):
        return ""

    def pass_(self) -> str:
        self._game.pass_move()
        return self._game.status

    def play(self, move_str: str) -> str:
        if 0 < len(move_str.split()) < 3:
            # self._game.play(move_str)
            return self._game.status
        else:
            raise InvalidCommandParameters(move_str.split())

    def undo(self, to_undo: int = 1) -> str:
        self._game.undo(to_undo)
        return self._game.status

    def validmoves(self):
        pass

    def _bestmove_in_depth(self, depth: int) -> str:
        return ""

    def _bestmove_in_time(self, hour: int, min: int, sec: int):
        return ""
