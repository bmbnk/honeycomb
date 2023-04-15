import pytest

from hive.engine.game import Game, InvalidMove, NotSupportedExpansionPieceError
from hive.engine.notation import GameState, GameString


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

    properties = GameString.decompose(game.status)
    gamestate = None
    for property in properties:
        if isinstance(property, GameState):
            gamestate = property

    assert gamestate == GameState.NotStarted


def test_new_game_creates_base_game(game: Game):
    game.new_game()

    assert game.status == "Base;NotStarted;White[1]"


@pytest.mark.parametrize(
    "gametype",
    ["Base+M", "Base+L", "Base+P", "Base+ML", "Base+MP", "Base+LP", "Base+MLP"],
)
def test_new_game_with_unsupported_expansions_raises_error(game: Game, gametype: str):
    with pytest.raises(NotSupportedExpansionPieceError):
        game.new_game(gametype)


@pytest.mark.parametrize(
    "start_moves",
    [
        pytest.param([], id="first_move"),
        pytest.param(["wS1", "bG1 -wS1", "wA1 wS1/"], id="after_three_moves"),
    ],
)
def test_pass_move_while_having_moves_raises_invalidmove(
    game: Game, start_moves: list[str]
):
    game.new_game()

    for move in start_moves:
        game.play(move)

    with pytest.raises(InvalidMove):
        game.pass_move()


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

    assert GameString.is_valid(game.status)
