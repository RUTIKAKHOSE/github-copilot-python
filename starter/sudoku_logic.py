import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def _count_solutions(board, limit=2):
    """Count valid completions for a Sudoku board, stopping early if more than one exists."""
    def count():
        best_cell = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] != EMPTY:
                    continue

                candidates = [
                    num for num in range(1, SIZE + 1)
                    if is_safe(board, row, col, num)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates
                    if len(candidates) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_cell is None:
            return 1

        row, col = best_cell
        total = 0
        for candidate in best_candidates:
            board[row][col] = candidate
            total += count()
            board[row][col] = EMPTY
            if total >= limit:
                return total
        return total

    return count()


def remove_cells(board, clues):
    """Remove cells only when the reduced board still has exactly one valid solution."""
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    clues_remaining = SIZE * SIZE

    for row, col in cells:
        if clues_remaining <= clues:
            break
        if board[row][col] == EMPTY:
            continue

        original = board[row][col]
        board[row][col] = EMPTY
        if _count_solutions(board, limit=2) != 1:
            board[row][col] = original
        else:
            clues_remaining -= 1


def generate_puzzle(clues=35):
    while True:
        board = create_empty_board()
        if not fill_board(board):
            raise RuntimeError("Unable to generate a complete Sudoku board")
        solution = deep_copy(board)
        remove_cells(board, clues)
        if _count_solutions(board, limit=2) == 1:
            return deep_copy(board), solution
