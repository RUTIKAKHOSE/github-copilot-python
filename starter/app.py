import copy

from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Difficulty setting controls how many clues are left on the board.
# Easy = most clues, Hard = fewest clues.
DIFFICULTY_TO_CLUES = {
    'easy': 40,
    'medium': 32,
    'hard': 26,
}


def get_clue_count(difficulty):
    """Return the clue count for the requested difficulty."""
    normalized = (difficulty or 'medium').lower()
    return DIFFICULTY_TO_CLUES.get(normalized, DIFFICULTY_TO_CLUES['medium'])


def _reset_current_game(puzzle, solution):
    """Reset the in-memory game state for a newly generated puzzle."""
    CURRENT['puzzle'] = copy.deepcopy(puzzle)
    CURRENT['solution'] = copy.deepcopy(solution)
    CURRENT['board'] = copy.deepcopy(puzzle)
    CURRENT['hints_used'] = 0
    CURRENT['locked'] = [
        (row, col) for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] != sudoku_logic.EMPTY
    ]


def _find_next_hint(board, locked):
    """Return the first empty editable cell available for a hint."""
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] != sudoku_logic.EMPTY:
                continue
            if (row, col) in locked:
                continue
            return row, col
    return None, None


# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'board': None,
    'hints_used': 0,
    'locked': []
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    clues = request.args.get('clues')

    # Preserve backward compatibility with any older client that still sends a direct clue count.
    if clues is not None:
        clues = int(clues)
    else:
        clues = get_clue_count(difficulty)

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    _reset_current_game(puzzle, solution)
    return jsonify({'puzzle': puzzle, 'hints_used': CURRENT['hints_used']})


@app.route('/hint', methods=['POST'])
def give_hint():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board'}), 400

    CURRENT['board'] = [list(map(int, row)) for row in board]
    locked = set(CURRENT.get('locked', []))
    row, col = _find_next_hint(CURRENT['board'], locked)

    if row is None or col is None:
        return jsonify({
            'message': 'No empty editable cells available',
            'hints_used': CURRENT['hints_used'],
        })

    CURRENT['board'][row][col] = solution[row][col]
    CURRENT['hints_used'] += 1
    locked.add((row, col))
    CURRENT['locked'] = sorted(locked)
    return jsonify({
        'row': row,
        'col': col,
        'value': solution[row][col],
        'hints_used': CURRENT['hints_used'],
    })


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board'}), 400

    CURRENT['board'] = [list(map(int, row)) for row in board]
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)