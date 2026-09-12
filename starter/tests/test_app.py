import pytest

from app import CURRENT, app, get_clue_count
from sudoku_logic import SIZE


@pytest.fixture
def client():
    app.config["TESTING"] = True
    CURRENT.update({
        "puzzle": None,
        "solution": None,
        "board": None,
        "hints_used": 0,
        "locked": [],
    })
    with app.test_client() as test_client:
        yield test_client


def test_index_route_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b'id="timer"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'id="scoreboard"' in response.data
    assert b'Top 10 Fastest Times' in response.data
    assert b'id="scoreboard-body"' in response.data


def test_new_game_creates_puzzle_and_stores_solution(client):
    response = client.get("/new?clues=35")
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data["puzzle"], list)
    assert len(data["puzzle"]) == SIZE
    assert all(len(row) == SIZE for row in data["puzzle"])
    assert CURRENT["puzzle"] == data["puzzle"]
    assert CURRENT["solution"] is not None
    assert len(CURRENT["solution"]) == SIZE


def test_get_clue_count_normalizes_difficulty_and_defaults_to_medium():
    assert get_clue_count("EASY") == 40
    assert get_clue_count("hard") == 26
    assert get_clue_count(None) == 32
    assert get_clue_count("unknown") == 32


def test_new_game_uses_difficulty_when_no_direct_clue_count_is_given(client):
    response = client.get("/new?difficulty=easy")
    puzzle = response.get_json()["puzzle"]

    assert response.status_code == 200
    assert sum(cell != 0 for row in puzzle for cell in row) == 40


def test_check_solution_requires_active_game(client):
    response = client.post("/check", json={"board": [[0] * SIZE for _ in range(SIZE)]})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_hint_requires_active_game(client):
    response = client.post("/hint", json={"board": [[0] * SIZE for _ in range(SIZE)]})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_routes_reject_boards_with_invalid_outer_shape(client):
    client.get("/new?clues=35")

    for route in ("/hint", "/check"):
        response = client.post(route, json={"board": []})

        assert response.status_code == 400
        assert response.get_json()["error"] == "Invalid board"


def test_check_solution_reports_correct_and_incorrect_cells(client):
    client.get("/new?clues=35")
    solution = CURRENT["solution"]

    correct_response = client.post("/check", json={"board": solution})
    assert correct_response.status_code == 200
    assert correct_response.get_json()["incorrect"] == []

    wrong_board = [row[:] for row in solution]
    wrong_board[0][0] = (wrong_board[0][0] % 9) + 1

    wrong_response = client.post("/check", json={"board": wrong_board})
    incorrect = wrong_response.get_json()["incorrect"]

    assert wrong_response.status_code == 200
    assert [0, 0] in incorrect
    assert len(incorrect) == 1


def test_hint_fills_one_empty_editable_cell_and_tracks_usage(client):
    client.get("/new?clues=35")
    board = [row[:] for row in CURRENT["puzzle"]]

    response = client.post("/hint", json={"board": board})
    data = response.get_json()

    assert response.status_code == 200
    assert data["hints_used"] == 1
    assert CURRENT["puzzle"][data["row"]][data["col"]] == 0
    assert CURRENT["board"][data["row"]][data["col"]] == CURRENT["solution"][data["row"]][data["col"]]
    assert data["value"] == CURRENT["solution"][data["row"]][data["col"]]


def test_hint_reports_when_board_has_no_empty_cells(client):
    client.get("/new?clues=35")

    response = client.post("/hint", json={"board": CURRENT["solution"]})

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "No empty editable cells available",
        "hints_used": 0,
    }
