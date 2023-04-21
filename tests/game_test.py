import re

import pytest

from hive.engine.game import (
    Game,
    GameNotPossibleError,
    GameTerminatedError,
    InvalidAddingPositionError,
    InvalidExpansionPieceError,
    InvalidMove,
    InvalidMovingPositionError,
    InvalidPieceColor,
    NotSupportedExpansionPieceError,
    PassMoveNotAllowedError,
)
from hive.engine.notation import InvalidMoveStringError


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

    gamestate = _gamestate(game.status)
    assert gamestate == "NotStarted"


def test_new_game_creates_base_game(game: Game):
    game.new_game()

    assert game.status == "Base;NotStarted;White[1]"


def test_new_game_creates_correct_game(game: Game):
    gametype = "Base"

    game.new_game(gametype)

    assert game.status == "Base;NotStarted;White[1]"


@pytest.mark.parametrize(
    "gametype",
    ["Base+M", "Base+L", "Base+P", "Base+ML", "Base+MP", "Base+LP", "Base+MLP"],
)
def test_new_game_with_unsupported_expansions_raises_error(game: Game, gametype: str):
    with pytest.raises(NotSupportedExpansionPieceError):
        game.new_game(gametype)


def test_play_pass_move_changes_turn(game: Game):
    gamestring = "Base;InProgress;Black[12];wQ;bQ -wQ;wG1 wQ-;bG1 -bQ;wG2 wG1-;bG2 -bG1;wG3 wG2-;bG3 -bG2;wS1 wG3-;bS1 -bG3;wS2 wS1-;bS2 -bS1;wB1 wS2-;bB1 -bS2;wB2 wB1-;bB2 -bB1;wA1 wB2-;bA1 -bB2;wA2 wA1-;bA2 -bA1;wA3 wA2-;bA3 -bA2;wA3 -bA3"

    game.load_game(gamestring)
    game.play("pass")

    turn_color, turn_num = _turn_color_and_num(game.status)
    assert turn_color == "White"
    assert turn_num == 13


@pytest.mark.parametrize(
    "start_moves",
    [
        pytest.param([], id="first_move"),
        pytest.param(["wS1", "bG1 -wS1", "wA1 wS1/"], id="after_three_moves"),
    ],
)
def test_play_pass_move_while_having_moves_raises_error(
    game: Game, start_moves: list[str]
):
    game.new_game()
    for move in start_moves:
        game.play(move)

    with pytest.raises(PassMoveNotAllowedError):
        game.play("pass")


@pytest.mark.parametrize(
    ("gamestring", "move"),
    [
        pytest.param(
            "Base;Draw;White[7];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            "wA1 wS1-",
            id="draw",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            "wG2 /bA1",
            id="black_wins",
        ),
        pytest.param(
            "Base;WhiteWins;Black[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/;wA1 \\bQ",
            "wA2 /wQ",
            id="white_wins",
        ),
    ],
)
def test_play_after_game_end_raises_error(game: Game, gamestring: str, move: str):
    game.load_game(gamestring)
    with pytest.raises(GameTerminatedError):
        game.play(move)


@pytest.mark.parametrize(
    ("gamestring", "move"),
    [
        pytest.param("Base;NotStarted;White[1]", "wG1", id="not_started"),
        pytest.param(
            "Base;InProgress;Black[2];wS1;bG1 -wS1;wA1 wS1/",
            "bG2 /bG1",
            id="in_progress",
        ),
        pytest.param(
            "Base;InProgress;Black[6];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/",
            "bA1 /wQ",
            id="draw",
        ),
        pytest.param(
            "Base;InProgress;Black[5];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/",
            "bA1 /wQ",
            id="black_wins",
        ),
        pytest.param(
            "Base;InProgress;White[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/",
            "wA1 \\bQ",
            id="white_wins",
        ),
    ],
)
def test_play_move_appears_in_status_as_last(game: Game, gamestring: str, move: str):
    game.load_game(gamestring)
    game.play(move)

    last_move = game.status.split(";")[-1]
    assert last_move == move


@pytest.mark.parametrize(
    ("gamestring", "move", "next_turn_color", "next_turn_num"),
    [
        pytest.param("Base;NotStarted;White[1]", "wG1", "Black", 1, id="not_started"),
        pytest.param(
            "Base;InProgress;Black[2];wS1;bG1 -wS1;wA1 wS1/",
            "bG2 /bG1",
            "White",
            3,
            id="in_progress_add_piece",
        ),
        pytest.param(
            "Base;InProgress;White[3];wQ;bQ -wQ;wA1 wQ/;bA1 /bQ",
            "wA1 wQ-",
            "Black",
            3,
            id="in_progress_move_piece",
        ),
    ],
)
def test_play_changes_turn(
    game: Game, gamestring: str, move: str, next_turn_color: str, next_turn_num: int
):
    game.load_game(gamestring)
    game.play(move)

    turn_color, turn_num = _turn_color_and_num(game.status)
    assert turn_color == next_turn_color
    assert turn_num == next_turn_num


@pytest.mark.parametrize(
    ("gamestring", "move", "next_state"),
    [
        pytest.param("Base;NotStarted;White[1]", "wG1", "InProgress", id="in_progress"),
        pytest.param(
            "Base;InProgress;Black[6];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/",
            "bA1 /wQ",
            "Draw",
            id="draw",
        ),
        pytest.param(
            "Base;InProgress;Black[5];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/",
            "bA1 /wQ",
            "BlackWins",
            id="black_wins",
        ),
        pytest.param(
            "Base;InProgress;White[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/",
            "wA1 \\bQ",
            "WhiteWins",
            id="white_wins",
        ),
    ],
)
def test_play_changes_state(game: Game, gamestring: str, move: str, next_state: str):
    game.load_game(gamestring)
    game.play(move)

    gamestate = _gamestate(game.status)
    assert gamestate == next_state


@pytest.mark.parametrize(
    ("gamestring", "move"),
    [
        pytest.param(
            "Base;NotStarted;White[1]",
            "wG1 -wA1",
            id="add_next_to_not_existing_on_first_move",
        ),
        pytest.param(
            "Base;InProgress;Black[2];wS1;bG1 -wS1;wA1 wS1/",
            "bS1 -wG1",
            id="add_next_to_not_existing",
        ),
        pytest.param(
            "Base;InProgress;Black[2];wS1;bG1 -wS1;wA1 wS1/",
            "bG2 wA1-",
            id="add_explicitly_next_to_opponent",
        ),
        pytest.param(
            "Base;InProgress;Black[2];wS1;bG1 -wS1;wA1 wS1/",
            "bG2 bG1/",
            id="add_implicitly_next_to_opponent",
        ),
    ],
)
def test_play_invalid_adding_position_raises_error(
    game: Game, gamestring: str, move: str
):
    game.load_game(gamestring)
    with pytest.raises(InvalidAddingPositionError):
        game.play(move)


# @pytest.mark.parametrize(
#     ("gamestring", "move"),
#     [
#         pytest.param(
#             "Base;InProgress;Black[4];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1;wG1 wS1-;bG3 -bG1;wQ wG1-",
#             "bS1 -bG3",
#             id="fourth_move_not_adding_bee",
#         ),
#         pytest.param(
#             "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
#             "wG2 wS1-",
#             id="adding_with_too_big_piece_number",
#         ),
#     ],
# )
# def test_play__raises_error(game: Game, gamestring: str, move: str):
#     game.load_game(gamestring)
#     with pytest.raises(InvalidAddingPositionError):
#         game.play(move)


@pytest.mark.parametrize(
    ("gamestring", "move"),
    [
        pytest.param(
            "Base;NotStarted;White[1]",
            "wM",
            id="Base_M",
        ),
        pytest.param(
            "Base;NotStarted;White[1]",
            "wL",
            id="Base_L",
        ),
        pytest.param(
            "Base;NotStarted;White[1]",
            "wP",
            id="Base_P",
        ),
    ],
)
def test_play_not_supported_piece_raises_error(game: Game, gamestring: str, move: str):
    game.load_game(gamestring)
    with pytest.raises(InvalidExpansionPieceError):
        game.play(move)


@pytest.mark.parametrize(
    ("gamestring", "move"),
    [
        pytest.param(
            "Base;NotStarted;White[1]",
            "wG4",
            id="wrong_piece_number",
        ),
        pytest.param(
            "Base;NotStarted;White[1]",
            "wg1",
            id="low_letter_piece_type",
        ),
        pytest.param(
            "Base;NotStarted;White[1]",
            "WG1",
            id="upper_letter_piece_color",
        ),
        pytest.param(
            "Base;NotStarted;White[1]",
            "G1",
            id="no_piece_color",
        ),
        pytest.param(
            "Base;NotStarted;White[1]",
            "wG",
            id="no_mandatory_piece_number",
        ),
        pytest.param(
            "Base;InProgress;Black[1];wS1",
            "bA1 .wS1",
            id="invalid_direction",
        ),
        pytest.param(
            "Base;InProgress;Black[1];wS1",
            "bA1/wS1",
            id="no_space",
        ),
    ],
)
def test_play_invalid_move_string_raises_error(game: Game, gamestring: str, move: str):
    game.load_game(gamestring)
    with pytest.raises(InvalidMoveStringError):
        game.play(move)


@pytest.mark.parametrize(
    ("gamestring", "move"),
    [
        pytest.param(
            "Base;InProgress;Black[2];wS1;bG1 -wS1;wQ wS1/",
            "bG1 wQ/",
            id="move_before_adding_bee",
        ),
        pytest.param(
            "Base;InProgress;White[3];wQ;bS1 -wQ;wS1 wQ/;bG1 -bS1",
            "wS1",
            id="no_destination",
        ),
    ],
)
def test_play_invalid_moving_position_raises_error(
    game: Game, gamestring: str, move: str
):
    game.load_game(gamestring)
    with pytest.raises(InvalidMovingPositionError):
        game.play(move)


def test_play_invalid_piece_color_raises_error(game: Game):
    gamestring = "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1"
    move = "bS1 -wS1"

    game.load_game(gamestring)
    with pytest.raises(InvalidPieceColor):
        game.play(move)


def test_play_pass_changes_turn(game: Game):
    gamestring = "Base;InProgress;Black[12];wQ;bQ -wQ;wG1 wQ-;bG1 -bQ;wG2 wG1-;bG2 -bG1;wG3 wG2-;bG3 -bG2;wS1 wG3-;bS1 -bG3;wS2 wS1-;bS2 -bS1;wB1 wS2-;bB1 -bS2;wB2 wB1-;bB2 -bB1;wA1 wB2-;bA1 -bB2;wA2 wA1-;bA2 -bA1;wA3 wA2-;bA3 -bA2;wA3 -bA3"

    game.load_game(gamestring)
    game.play("pass")

    turn_color, turn_num = _turn_color_and_num(game.status)
    assert turn_color == "White"
    assert turn_num == 13


@pytest.mark.parametrize(
    "start_moves",
    [
        pytest.param([], id="first_move"),
        pytest.param(["wS1", "bG1 -wS1", "wA1 wS1/"], id="after_three_moves"),
    ],
)
def test_play_pass_while_having_moves_raises_invalidmove(
    game: Game, start_moves: list[str]
):
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

    assert _is_valid_gamestring(game.status)


@pytest.mark.parametrize(
    ("gamestring", "to_undo", "result_gamestate"),
    [
        pytest.param("Base;NotStarted;White[1]", 1, "NotStarted", id="NotStarted"),
        pytest.param(
            "Base;InProgress;Black[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1;wQ wS1-",
            10,
            "NotStarted",
            id="InProgress_to_NotStarted",
        ),
        pytest.param(
            "Base;Draw;White[7];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            5,
            "InProgress",
            id="Draw_to_InProgress",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            1,
            "InProgress",
            id="BlackWins_to_InProgress",
        ),
        pytest.param(
            "Base;WhiteWins;Black[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/;wA1 \\bQ",
            4,
            "InProgress",
            id="WhiteWins_to_InProgress",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            100,
            "NotStarted",
            id="terminated_to_not_started",
        ),
    ],
)
def test_undo_correctly_changes_gamestate(
    game: Game, gamestring: str, to_undo: int, result_gamestate: str
):
    game.load_game(gamestring)

    game.undo(to_undo)

    gamestate = _gamestate(game.status)
    assert gamestate == result_gamestate


@pytest.mark.parametrize(
    ("gamestring", "to_undo", "result_turn_color"),
    [
        pytest.param("Base;NotStarted;White[1]", 1, "White", id="not_started"),
        pytest.param(
            "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
            1,
            "Black",
            id="undo_one",
        ),
        pytest.param(
            "Base;InProgress;Black[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1;wQ wS1-",
            2,
            "Black",
            id="undo_two",
        ),
        pytest.param(
            "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
            3,
            "Black",
            id="undo_three",
        ),
        pytest.param(
            "Base;Draw;White[7];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            1,
            "Black",
            id="draw",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            1,
            "Black",
            id="black_wins",
        ),
        pytest.param(
            "Base;WhiteWins;Black[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/;wA1 \\bQ",
            1,
            "White",
            id="white_wins",
        ),
    ],
)
def test_undo_correctly_changes_turn_color(
    game: Game, gamestring: str, to_undo: int, result_turn_color: str
):
    game.load_game(gamestring)

    game.undo(to_undo)

    turn_color, _ = _turn_color_and_num(game.status)
    assert turn_color == result_turn_color


@pytest.mark.parametrize(
    ("gamestring", "to_undo", "result_turn_num"),
    [
        pytest.param("Base;NotStarted;White[1]", 1, 1, id="not_started"),
        pytest.param(
            "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
            1,
            2,
            id="undo_one_with_change",
        ),
        pytest.param(
            "Base;InProgress;Black[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1;wQ wS1-",
            1,
            3,
            id="undo_one_no_change",
        ),
        pytest.param(
            "Base;InProgress;Black[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1;wQ wS1-",
            2,
            2,
            id="undo_two",
        ),
        pytest.param(
            "Base;InProgress;White[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1",
            3,
            1,
            id="undo_three",
        ),
        pytest.param(
            "Base;Draw;White[7];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            1,
            6,
            id="draw",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            1,
            5,
            id="black_wins",
        ),
        pytest.param(
            "Base;WhiteWins;Black[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/;wA1 \\bQ",
            2,
            4,
            id="white_wins",
        ),
    ],
)
def test_undo_correctly_changes_turn_num(
    game: Game, gamestring: str, to_undo: int, result_turn_num: int
):
    game.load_game(gamestring)

    game.undo(to_undo)

    _, turn_num = _turn_color_and_num(game.status)
    assert turn_num == result_turn_num


@pytest.mark.parametrize(
    ("gamestring", "to_undo", "result_moves"),
    [
        pytest.param(
            "Base;InProgress;Black[3];wS1;bG1 -wS1;wA1 wS1/;bG2 /bG1;wQ wS1-",
            3,
            ["wS1", "bG1 -wS1"],
            id="three_moves",
        ),
        pytest.param(
            "Base;Draw;White[7];wQ;bQ -wQ;wS1 wQ-;bS1 -bQ;wS2 wQ/;bS2 \\bQ;wG1 wQ\\;bG1 /bQ;wA1 wS1-;bA1 -bS1;wA1 bQ/;bA1 /wQ",
            7,
            ["wQ", "bQ -wQ", "wS1 wQ-", "bS1 -bQ", "wS2 wQ/"],
            id="Draw",
        ),
        pytest.param(
            "Base;BlackWins;White[6];wQ;bG1 wQ-;wG1 -wQ;bQ bG1\\;wG2 /wQ;bA1 bG1-;wA1 \\wQ;bQ wQ\\;wG2 wQ/;bA1 /wQ",
            4,
            ["wQ", "bG1 wQ-", "wG1 -wQ", "bQ bG1\\", "wG2 /wQ", "bA1 bG1-"],
            id="BlackWins",
        ),
        pytest.param(
            "Base;WhiteWins;Black[5];wG1;bQ wG1-;wQ /wG1;bG1 bQ-;wA1 -wG1;bG2 bQ\\;wQ /bQ;bA1 bQ/;wA1 \\bQ",
            3,
            ["wG1", "bQ wG1-", "wQ /wG1", "bG1 bQ-", "wA1 -wG1", "bG2 bQ\\"],
            id="WhiteWins",
        ),
    ],
)
def test_undo_correctly_removes_moves(
    game: Game, gamestring: str, to_undo: int, result_moves: list[str]
):
    game.load_game(gamestring)

    game.undo(to_undo)

    moves = _moves(game.status)
    print(moves)
    assert moves == result_moves


@pytest.mark.parametrize(
    ("depth", "expected_leaf_nodes"),
    [
        # Precalculated PERFT values
        (1, 5),
        (2, 150),
        (3, 2162),
        # TODO: Add (4, 27676) later as nodes in this depth where harder to compute by hand and there could be some miscalculations
    ],
)
def test_validmoves_with_perft(game: Game, depth: int, expected_leaf_nodes: int):
    game.new_game("Base")

    leaf_nodes = _perft(game, depth)

    assert leaf_nodes == expected_leaf_nodes


@pytest.mark.parametrize(
    # One move can have multiple move_str representations so moves_str is a list of sets with all possible representations of the move
    ("gamestring", "piece_str", "moves_str"),
    [
        pytest.param(
            "Base;InProgress;Black[3];wQ;bS1 -wQ;wG1 wQ-;bA1 -bS1;wG1 -bA1",
            "bA1",
            [],
            id="one_hive",
        ),
        pytest.param(
            "Base;InProgress;White[5];wG1;bQ -wG1;wG2 wG1\\;bS1 -bQ;wQ /wG2;bS1 -wQ;wA1 wG1-;bA1 \\bQ",
            "wA1",
            [
                {"wA1 wG1/"},
                {"wA1 bA1-", "wA1 bQ/", "wA1 \\wG1"},
                {"wA1 bA1/"},
                {"wA1 \\bA1"},
                {"wA1 -bA1"},
                {"wA1 /bA1", "wA1 -bQ"},
                {"wA1 /bQ", "wA1 \\bS1"},
                {"wA1 -bS1"},
                {"wA1 /bS1"},
                {"wA1 bS1\\", "wA1 /wQ"},
                {"wA1 wQ\\"},
                {"wA1 wQ-", "wA1 wG2\\"},
                {"wA1 wG2-"},
            ],
            id="freedom_to_move",
        ),
    ],
)
def test_validmoves_return_proper_moving_ant_positions(
    game: Game, gamestring: str, piece_str: str, moves_str: list[set[str]]
):
    _test_validmoves_return_proper_moving_piece_positions(
        game, gamestring, piece_str, moves_str
    )


@pytest.mark.parametrize(
    # One move can have multiple move_str representations so moves_str is a list of sets with all possible representations of the move
    ("gamestring", "piece_str", "moves_str"),
    [
        pytest.param(
            "Base;InProgress;White[4];wS1;bQ -wS1;wQ wS1\\;bA1 \\bQ;wQ wS1-;bA1 wQ-",
            "wQ",
            [],
            id="one_hive",
        ),
        pytest.param(
            "Base;InProgress;White[6];wQ;bQ -wQ;wA1 wQ-;bS1 -bQ;wA1 bS1/;bS1 wA1/;wB1 wQ-;bG1 bS1-;wB1 wQ/;bG2 /bQ",
            "wQ",
            [{"wQ bQ\\", "wQ bG2-"}, {"wQ wB1\\"}],
            id="freedom_to_move",
        ),
    ],
)
def test_validmoves_return_proper_moving_bee_positions(
    game: Game, gamestring: str, piece_str: str, moves_str: list[set[str]]
):
    _test_validmoves_return_proper_moving_piece_positions(
        game, gamestring, piece_str, moves_str
    )


def _gamestate(gamestring: str):
    gamestring_parts = gamestring.split(";")
    gamestate = gamestring_parts[1]
    return gamestate


def _is_valid_gamestring(gamestring: str):
    match = re.fullmatch("([^;]*);([^;]*);([^;]*)(?:(;.*)*)", gamestring)
    return match is not None


def _moves(gamestring: str) -> list[str]:
    gamestring_parts = gamestring.split(";")
    moves = gamestring_parts[3:]
    return moves


def _perft(game: Game, depth: int) -> int:
    if depth == 0:
        return 1

    leaf_nodes = 0

    validmoves = game.valid_moves()
    for move in validmoves:
        game.play(move)
        leaf_nodes += _perft(game, depth - 1)
        game.undo(to_undo=1)

    if validmoves:
        return leaf_nodes
    return 1  # pass move


def _test_validmoves_return_proper_moving_piece_positions(
    game: Game, gamestring: str, piece_str: str, moves_str: list[set[str]]
):
    game.load_game(gamestring)

    moves = game.valid_moves()
    piece_moves = {move for move in moves if move.startswith(piece_str)}

    for move_representations in moves_str:
        assert piece_moves & move_representations
        piece_moves -= move_representations

    assert not piece_moves


def _turn_color_and_num(gamestatus: str) -> tuple[str, int]:
    match = re.search("(?:;(?:(Black|White)\\[(\\d*)\\]))", gamestatus)
    assert match is not None
    turn_color, turn_num = match.groups()
    return turn_color, int(turn_num)
