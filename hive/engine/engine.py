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


class Engine:
    __slots__ = "_game", "_cmd_to_method", "_cmd_completion_str"

    def __init__(self) -> None:
        self._game = Game()
        self._cmd_to_method = {
            "info": self.engine_info,
            "newgame": self.new_game,
            "play": self.play,
            "pass": self.pass_move,
            "validmoves": self.valid_moves,
            "bestmove": self.best_move,
            "undo": self.undo,
            "options": self.options,
        }
        self._cmd_completion_str = "ok"

    def execute(self, inp) -> str:
        return self._response(inp)

    def engine_info(self) -> str:
        return f"id {ENGINE_NAME} v{VERSION}"

    def new_game(self) -> str:
        self._game.new_game()
        return self._game.status

    def play(self, params_str: str) -> str:
        if 0 < len(params_str.split()) < 3:
            self._game.play(params_str)
            return self._game.status
        else:
            raise InvalidCommandParameters(params_str.split())

    def pass_move(self) -> str:
        self._game.pass_move()
        return self._game.status

    def valid_moves(self):
        pass

    def best_move(self):
        pass

    def undo(self) -> str:
        self._game.undo()
        return self._game.status

    def options(self):
        pass

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
