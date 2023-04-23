from honeycomb.engine import Engine


class EngineCLI:
    def __init__(self) -> None:
        self.engine = Engine()

    def run(self) -> None:
        command = "info"
        while command != "q":
            result = self.engine.execute(command)
            print(result)
            command = input()

        self.stop()

    def stop(self) -> None:
        print("Engine stopped.")
        raise SystemExit
