import re

import pytest

from hive.engine.game import (
    Game,
    GameNotPossibleError,
    InvalidMove,
    NotSupportedExpansionPieceError,
)


@pytest.fixture
def game() -> Game:
    return Game()


@pytest.mark.parametrize(
    "gamestring",
    [
        pytest.param("Base;NotStarted;White[1]", id="not_started"),
        pytest.param(
            "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1", id="in_progress"
        ),
        pytest.param(
            "Base;Draw;White[7];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            id="draw",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            id="black_wins",
        ),
        pytest.param(
            "Base;WhiteWins;Black[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/;wA1 \\bQ",
            id="white_wins",
        ),
    ],
)
def test_load_game_state_equals_gamestring(game: Game, gamestring: str):
    game.load_game(gamestring)

    assert game.status == gamestring


@pytest.mark.parametrize(
    "gamestring",
    [
        pytest.param("Base;InProgress;White[1]", id="InProgress_while_NotStarted"),
        pytest.param(
            "Base;NotStarted;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
            id="NotStarted_while_InProgress",
        ),
        pytest.param(
            "Base;Draw;White[3];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            id="turn_num_3_while_7",
        ),
        pytest.param(
            "Base;BlackWins;Black[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            id="turn_color_black_while_white",
        ),
    ],
)
def test_load_game_with_not_correct_game_state_raises_error(
    game: Game, gamestring: str
):
    with pytest.raises(GameNotPossibleError):
        game.load_game(gamestring)


@pytest.mark.parametrize(
    "gamestring",
    [
        "Base+M;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
        "Base+L;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
        "Base+P;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
        "Base+ML;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
        "Base+MP;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
        "Base+LP;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
        "Base+MLP;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
    ],
)
def test_load_game_with_unsupported_expansions_raises_error(
    game: Game, gamestring: str
):
    with pytest.raises(NotSupportedExpansionPieceError):
        game.load_game(gamestring)


def test_new_game_not_started_game_state(game: Game):
    game.new_game()

    gamestring_parts = game.status.split(";")
    gamestate = gamestring_parts[1]
    assert gamestate == "NotStarted"


def test_new_game_creates_base_game(game: Game):
    game.new_game()

    assert game.status == "Base;NotStarted;White[1]"


def test_new_game_creates_correct_game(game: Game):
    game.new_game("Base")

    assert game.status == "Base;NotStarted;White[1]"


@pytest.mark.parametrize(
    "gametype",
    ["Base+M", "Base+L", "Base+P", "Base+ML", "Base+MP", "Base+LP", "Base+MLP"],
)
def test_new_game_with_unsupported_expansions_raises_error(game: Game, gametype: str):
    with pytest.raises(NotSupportedExpansionPieceError):
        game.new_game(gametype)


def test_pass_move_changes_turn(game: Game):
    game.load_game(
        "Base;InProgress;Black[12];wQ;bQ -wQ;wG1 wQ-;bG1 -bQ;wG2 wG1-;bG2 -bG1;wG3 wG2-;bG3 -bG2;wS1 wG3-;bS1 -bG3;wS2 wS1-;bS2 -bS1;wB1 wS2-;bB1 -bS2;wB2 wB1-;bB2 -bB1;wA1 wB2-;bA1 -bB2;wA2 wA1-;bA2 -bA1;wA3 wA2-;bA3 -bA2;wA3 -bA3"
    )

    game.pass_move()

    match = re.search("(?:;(?:(Black|White)\\[(\\d*)\\]);)", game.status)
    assert match is not None
    turn_color, turn_num = match.groups()
    assert turn_color == "White"
    assert turn_num == 13


@pytest.mark.parametrize(
    "start_moves",
    [
        pytest.param([], id="first_move"),
        pytest.param(["wS1", "bG1 -wS1", "wA1 wS1/"], id="after_three_moves"),
    ],
)
def test_pass_move_while_having_moves_raises_invalidmove(game: Game, start_moves):
    game.new_game()

    for move in start_moves:
        game.play(move)

    with pytest.raises(InvalidMove):
        game.pass_move()


@pytest.mark.parametrize(
    ("gamestring", "move", "next_turn_color", "next_turn_num"),
    [
        pytest.param("Base;NotStarted;White[1]", "wG1", "Black", 1, id="not_started"),
        pytest.param(
            "Base;InProgress;Black[2];wS1;bG1 -wS1;wA1 wS1/",
            "bG2 /bG1",
            "White",
            3,
            id="in_progress",
        ),
    ],
)
def test_play_changes_turn(
    game: Game, gamestring: str, move: str, next_turn_color: str, next_turn_num: int
):
    game.load_game(gamestring)

    game.play(move)

    match = re.search("(?:;(?:(Black|White)\\[(\\d*)\\]);)", game.status)
    assert match is not None
    turn_color, turn_num = match.groups()
    assert turn_color == next_turn_color
    assert int(turn_num) == next_turn_num


def test_play_pass_changes_turn(game: Game):
    game.load_game(
        "Base;InProgress;Black[12];wQ;bQ -wQ;wG1 wQ-;bG1 -bQ;wG2 wG1-;bG2 -bG1;wG3 wG2-;bG3 -bG2;wS1 wG3-;bS1 -bG3;wS2 wS1-;bS2 -bS1;wB1 wS2-;bB1 -bS2;wB2 wB1-;bB2 -bB1;wA1 wB2-;bA1 -bB2;wA2 wA1-;bA2 -bA1;wA3 wA2-;bA3 -bA2;wA3 -bA3"
    )

    game.play("pass")

    match = re.search("(?:;(?:(Black|White)\\[(\\d*)\\]);)", game.status)
    assert match is not None
    turn_color, turn_num = match.groups()
    assert turn_color == "White"
    assert turn_num == 13


@pytest.mark.parametrize(
    "start_moves",
    [
        pytest.param([], id="first_move"),
        pytest.param(["wS1", "bG1 -wS1", "wA1 wS1/"], id="after_three_moves"),
    ],
)
def test_play_pass_while_having_moves_raises_invalidmove(game: Game, start_moves):
    game.new_game()

    for move in start_moves:
        game.play(move)

    with pytest.raises(InvalidMove):
        game.play("pass")


@pytest.mark.parametrize(
    "gamestring",
    [
        pytest.param("Base;NotStarted;White[1]", id="not_started"),
        pytest.param(
            "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1", id="in_progress"
        ),
        pytest.param(
            "Base;Draw;White[7];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            id="draw",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            id="black_wins",
        ),
        pytest.param(
            "Base;WhiteWins;Black[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/;wA1 \\bQ",
            id="white_wins",
        ),
    ],
)
def test_status_is_valid_gamestring(game: Game, gamestring: str):
    game.load_game(gamestring)

    match = re.fullmatch("([^;]*);([^;]*);([^;]*)(?:(;.*)*)", game.status)

    assert match is not None
