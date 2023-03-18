from hive import engine


class App:
    __slots__ = "_engine"

    def __init__(self) -> None:
        self._engine = engine.EngineCommandExecutor()

    def run(self) -> None:
        command = "info"
        while command != "q":
            result = self._engine.execute(command)
            print(result)
            command = input()

        self.stop()

    def stop(self) -> None:
        print("Engine stopped.")
        raise SystemExit
