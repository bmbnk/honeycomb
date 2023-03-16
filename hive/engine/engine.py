from dataclasses import dataclass
from enum import Enum, auto

from hive.engine.hive import Hive

COMPLETION_STR = "ok"
GAME_TYPE = "Base"
ENGINE_NAME = "EngineName"
VERSION = "1.0"


def get_engine_info() -> str:
    return f"id {ENGINE_NAME} v{VERSION}"


class EngineError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"err {self.message}"


class InvalidCommand(EngineError):
    def __init__(self, cmd):
        self.message = f"Command : '{cmd}' is not valid."


class GameState(Enum):
    NotStarted = auto()
    InProgress = auto()
    Draw = auto()
    WhiteWins = auto()
    BlackWin = auto()


class CommandValidator:
    def validate(self, command):
        pass


@dataclass
class CommandParser:
    command: str
    arguments: list[str]


@dataclass
class Command:
    name: str
    arguments: list[str]

    def execute(self):
        pass


class Engine:
    __slots__ = "_hive", "_cmd_to_method", "_cmd_completion_str"

    def __init__(self):
        self._hive = Hive()
        self._cmd_to_method = {
            "info": "engine_info",
            "newgame": "new_game",
            "play": "play",
            "pass": "pass_move",
            "validmoves": "valid_moves",
            "bestmove": "best_move",
            "undo": "undo",
            "options": "options",
        }
        self._cmd_completion_str = "ok"

    def execute(self, command):
        return self._get_response(command)

    def engine_info(self):
        return "returning info"

    def new_game(self):
        return "starting new game..."

    def play(self, move):
        # move_str = move.split(" ")
        # if len(move_parts) == 2:

        # return ""
        pass

    def pass_move(self):
        pass

    def valid_moves(self):
        pass

    def best_move(self):
        pass

    def undo(self):
        pass

    def options(self):
        pass

    def _get_response(self, command) -> str:
        try:
            result = self._get_cmd_result(command)
        except EngineError as e:
            result = str(e)

        return f"{result}\n{self._cmd_completion_str}"

    def _get_cmd_result(self, command) -> str:
        try:
            engine_method = self._get_method_name(command)
            return getattr(self, engine_method)()
        except EngineError as e:
            return str(e)

    def _get_method_name(self, command: str) -> str:
        if command not in self._cmd_to_method:
            raise InvalidCommand(command)

        return self._cmd_to_method[command]
