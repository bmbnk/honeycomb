class Engine:
    def start(self) -> None:
        print("Starting engine.")
        while True:
            command = input()
            if command == "q":
                raise SystemExit

    def execute(self, inp: str) -> str:
        return "ok"

    def end(self) -> None:
        print("Engine stopped.")
