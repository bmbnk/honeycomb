from hive import engine


class App:
    def __init__(self) -> None:
        self.engine = engine.Engine()

    def run(self) -> None:
        self.engine.start()
