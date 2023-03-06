import sys

from hive import cli


def main() -> None:
    cli.App().run()


if __name__ == "__main__":
    sys.exit(main())
