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
        self.message = f"Command : '{cmd}' is not valid."


class Engine:
    __slots__ = "_game", "_cmd_to_method", "_cmd_completion_str"

    def __init__(self):
        self._game = Game()
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
        return self._response(command)

    def engine_info(self):
        return f"id {ENGINE_NAME} v{VERSION}"

    def new_game(self) -> str:
        self._game.new_game()
        return self._game.status

    def play(self, move_str: str) -> str:
        self._game.play(move_str)
        return self._game.status

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

    def _response(self, command) -> str:
        try:
            result = self._cmd_result(command)
        except EngineError as e:
            result = str(e)

        return f"{result}\n{self._cmd_completion_str}"

    def _cmd_result(self, command) -> str:
        method_name = self._method_name(command)
        return getattr(self, method_name)()

    def _method_name(self, command: str) -> str:
        if command not in self._cmd_to_method:
            raise InvalidCommand(command)

        return self._cmd_to_method[command]
