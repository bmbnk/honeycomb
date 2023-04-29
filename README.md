# honeycomb

![Tests](https://github.com/bmbnk/honeycomb/actions/workflows/tests.yml/badge.svg)

honeycomb is a [Hive](https://gen42.com/games/hive) board game engine focused on reliability and ease of use. The goal of this project was to help with AI research. It implements the [Universal Hive Protocol](https://github.com/jonthysell/Mzinga/wiki/UniversalHiveProtocol) (UHP). 

## Features

- Fully compliant with the UHP protocol
- CLI interface
- Python API for easy integration with Python AI tools
- Detailed feedback for an invalid input
- Tested

## Installation

To install honeycomb, simply run:

```bash
pip install .
```


## Usage

### CLI

To run honeycomb as a command-line interface, simply run:
```bash
honeycomb
```

This will launch the engine, provide you with the game info and prepare a new game.

### Python API

To use honeycomb in your own Python code, simply import it as a module:

```python
import honeycomb
```
You can then create a new instance of the engine and start using it by executing the commands given as an string argument:

```python
engine = honeycomb.Engine()
engine.execute('newgame')
engine.execute('play wS1')
engine.execute('validmoves')
```
