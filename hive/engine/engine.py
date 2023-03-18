import time
from typing import Callable

from hive.engine.game import Game

COMPLETION_STR = "ok"
ENGINE_NAME = "EngineName"
VERSION = "1.0"


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
    __slots__ = "_engine", "_cmd_to_method", "_cmd_completion_str"

    def __init__(self) -> None:
        self._engine = Engine()
        self._cmd_to_method = {
            "info": self._engine.info,
            "newgame": self._engine.newgame,
            "play": self._engine.play,
            "pass": self._engine.pass_,
            "validmoves": self._engine.validmoves,
            "bestmove": self._engine.bestmove,
            "undo": self._engine.undo,  
            "options": self._engine.options,
        }
        self._cmd_completion_str = "ok"

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
    __slots__ = "_game", "_max_time_format"

    def __init__(self) -> None:
        self._game = Game()
        self._max_time_format = "%H:%M:%S"

    def info(self) -> str:
        return f"id {ENGINE_NAME} v{VERSION}"

    def newgame(self, game_info: str = "") -> str:
        self._game.new_game()
        return self._game.status

    def play(self, move_str: str) -> str:
        if 0 < len(move_str.split()) < 3:
            self._game.play(move_str)
            return self._game.status
        else:
            raise InvalidCommandParameters(move_str.split())

    def pass_(self) -> str:
        self._game.pass_move()
        return self._game.status

    def validmoves(self):
        pass

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
            return self._bestmove_in_time(time_info.tm_hour, time_info.tm_min, time_info.tm_sec)
        else:
            raise InvalidCommandParameters(limit_type)


    def _bestmove_in_depth(self, depth: int) -> str:
        return ""

    def _bestmove_in_time(self, hour: int, min: int, sec: int):
        return ""


    def undo(self, to_undo: int = 1) -> str:
        self._game.undo(to_undo)
        return self._game.status

    def options(self):
        return ""

