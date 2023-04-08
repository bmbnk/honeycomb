from hive import engine


class App:
    __slots__ = "_cmd_executor"

    def __init__(self) -> None:
        self._cmd_executor = engine.EngineCommandExecutor()

    def run(self) -> None:
        command = "info"
        while command != "q":
            result = self._cmd_executor.execute(command)
            print(result)
            command = input()

        self.stop()

    def stop(self) -> None:
        print("Engine stopped.")
        raise SystemExit
