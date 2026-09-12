// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCOREBOARD_STORAGE_KEY = 'sudokuTop10Scores';
let puzzle = [];
let lockedCells = new Set();
let timerId = null;
let elapsedSeconds = 0;
let gameCompleted = false;
let hintsUsed = 0;

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

function getScores() {
  try {
    const storedScores = JSON.parse(localStorage.getItem(SCOREBOARD_STORAGE_KEY));
    if (!Array.isArray(storedScores)) {
      return [];
    }
    return storedScores
      .filter((score) => score && typeof score.name === 'string'
        && score.name.trim() && Number.isInteger(score.time) && score.time >= 0
        && typeof score.difficulty === 'string' && score.difficulty.trim()
        && Number.isInteger(score.hints)
        && score.hints >= 0)
      .map((score) => ({
        name: score.name.trim().slice(0, 40),
        time: score.time,
        difficulty: score.difficulty.trim(),
        hints: score.hints,
      }))
      .sort((first, second) => first.time - second.time)
      .slice(0, 10);
  } catch (error) {
    return [];
  }
}

function persistScores(scores) {
  try {
    localStorage.setItem(SCOREBOARD_STORAGE_KEY, JSON.stringify(scores.slice(0, 10)));
  } catch (error) {
    // The game remains playable when storage is unavailable.
  }
}

function renderScoreboard() {
  const scoreboardBody = document.getElementById('scoreboard-body');
  scoreboardBody.innerHTML = '';
  const scores = getScores();
  persistScores(scores);
  if (scores.length === 0) {
    const row = scoreboardBody.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 5;
    cell.innerText = 'No scores yet.';
    return;
  }
  scores.forEach((score, index) => {
    const row = scoreboardBody.insertRow();
    row.insertCell().innerText = String(index + 1);
    row.insertCell().innerText = score.name;
    row.insertCell().innerText = formatTime(score.time);
    row.insertCell().innerText = score.difficulty;
    row.insertCell().innerText = String(score.hints);
  });
}

function saveScore(name) {
  const scores = getScores();
  const playerName = String(name || '').trim().slice(0, 40) || 'Anonymous';
  scores.push({
    name: playerName,
    time: elapsedSeconds,
    difficulty: getSelectedDifficulty(),
    hints: hintsUsed,
  });
  scores.sort((first, second) => first.time - second.time);
  persistScores(scores);
  renderScoreboard();
}

function updateTimer() {
  const timer = document.getElementById('timer');
  timer.innerText = `Time: ${formatTime(elapsedSeconds)}`;
}

function stopTimer() {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimer();
  timerId = setInterval(() => {
    elapsedSeconds += 1;
    updateTimer();
  }, 1000);
}

function getSelectedDifficulty() {
  const element = document.getElementById('difficulty');
  return element ? element.value : 'medium';
}

function toggleTheme() {
  const isDark = document.body.classList.toggle('dark-mode');
  const toggle = document.getElementById('theme-toggle');
  toggle.innerText = isDark ? 'Light Mode' : 'Dark Mode';
  toggle.setAttribute('aria-pressed', String(isDark));
}

function getBoardValues() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function markConflictingCells() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const conflicts = new Set();
  const groups = [];

  for (let row = 0; row < SIZE; row++) {
    groups.push(Array.from({length: SIZE}, (_, col) => row * SIZE + col));
  }
  for (let col = 0; col < SIZE; col++) {
    groups.push(Array.from({length: SIZE}, (_, row) => row * SIZE + col));
  }
  for (let boxRow = 0; boxRow < SIZE; boxRow += 3) {
    for (let boxCol = 0; boxCol < SIZE; boxCol += 3) {
      groups.push(Array.from({length: 9}, (_, index) => {
        const row = boxRow + Math.floor(index / 3);
        const col = boxCol + (index % 3);
        return row * SIZE + col;
      }));
    }
  }

  inputs.forEach((input) => input.classList.remove('invalid-entry'));
  groups.forEach((group) => {
    const cellsByValue = new Map();
    group.forEach((index) => {
      const input = inputs[index];
      if (input.classList.contains('hint')) {
        return;
      }
      const value = input.value;
      if (value) {
        if (!cellsByValue.has(value)) {
          cellsByValue.set(value, []);
        }
        cellsByValue.get(value).push(index);
      }
    });
    cellsByValue.forEach((cells) => {
      if (cells.length > 1) {
        cells.forEach((index) => conflicts.add(index));
      }
    });
  });

  conflicts.forEach((index) => inputs[index].classList.add('invalid-entry'));
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        markConflictingCells();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  lockedCells = new Set();
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
        lockedCells.add(`${i}:${j}`);
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function lockHintCell(row, col) {
  lockedCells.add(`${row}:${col}`);
  const idx = row * SIZE + col;
  const input = document.querySelector(`.sudoku-cell[data-row='${row}'][data-col='${col}']`);
  if (input) {
    input.disabled = true;
    input.className = 'sudoku-cell hint';
  }
}

async function newGame() {
  stopTimer();
  elapsedSeconds = 0;
  gameCompleted = false;
  hintsUsed = 0;
  updateTimer();
  const difficulty = getSelectedDifficulty();
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  startTimer();
}

async function applyHint() {
  const board = getBoardValues();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  if (data.row !== undefined && data.col !== undefined) {
    const idx = data.row * SIZE + data.col;
    const input = document.querySelector(`.sudoku-cell[data-row='${data.row}'][data-col='${data.col}']`);
    if (input) {
      input.value = String(data.value);
      input.disabled = true;
      input.className = 'sudoku-cell hint';
      lockedCells.add(`${data.row}:${data.col}`);
    }
    msg.style.color = '#1976d2';
    msg.innerText = `Hint used. Total hints: ${data.hints_used}.`;
    hintsUsed = data.hints_used;
    return;
  }
  msg.style.color = '#1976d2';
  msg.innerText = 'No more hints available.';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardValues();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    const isLocked = inp.disabled || lockedCells.has(`${inp.dataset.row}:${inp.dataset.col}`);
    if (isLocked && !inp.classList.contains('hint')) {
      continue;
    }
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    if (!gameCompleted) {
      stopTimer();
      gameCompleted = true;
      msg.style.color = '#388e3c';
      msg.innerText = `Congratulations! You solved it in ${formatTime(elapsedSeconds)}.`;
      const enteredName = window.prompt('Enter your name for the Top 10 scoreboard:', 'Anonymous');
      const playerName = (enteredName || 'Anonymous').trim().slice(0, 40) || 'Anonymous';
      saveScore(playerName);
    }
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  renderScoreboard();
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('get-hint').addEventListener('click', applyHint);
  // initialize
  newGame();
});