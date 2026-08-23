from sudoku_logic import (
    SIZE,
    EMPTY,
    _count_solutions,
    create_empty_board,
    fill_board,
    generate_puzzle,
    is_safe,
)


def board_is_valid(board):
    expected = set(range(1, SIZE + 1))

    for row in board:
        if set(row) != expected:
            return False

    for col in range(SIZE):
        values = {board[row][col] for row in range(SIZE)}
        if values != expected:
            return False

    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = {
                board[r][c]
                for r in range(start_row, start_row + 3)
                for c in range(start_col, start_col + 3)
            }
            if values != expected:
                return False

    return True


def test_create_empty_board_returns_9x9_grid_of_zeroes():
    board = create_empty_board()

    assert len(board) == SIZE
    assert all(len(row) == SIZE for row in board)
    assert all(cell == EMPTY for row in board for cell in row)


def test_is_safe_rejects_conflicts_in_row_column_and_box():
    board = create_empty_board()
    board[0][0] = 5
    board[0][1] = 8
    board[1][0] = 7
    board[1][1] = 5

    assert is_safe(board, 0, 2, 5) is False
    assert is_safe(board, 2, 0, 5) is False
    assert is_safe(board, 0, 1, 5) is False


def test_fill_board_completes_empty_board():
    board = create_empty_board()

    assert fill_board(board) is True
    assert board_is_valid(board)


def test_generate_puzzle_returns_a_reduced_board_and_complete_solution():
    puzzle, solution = generate_puzzle(35)

    assert len(puzzle) == SIZE
    assert len(solution) == SIZE
    assert all(len(row) == SIZE for row in puzzle)
    assert all(len(row) == SIZE for row in solution)
    assert puzzle != solution
    assert board_is_valid(solution)
    assert sum(cell != EMPTY for row in puzzle for cell in row) < 81


def test_generate_puzzle_has_exactly_one_solution():
    puzzle, _ = generate_puzzle(35)

    assert _count_solutions(puzzle, limit=2) == 1
