// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let hintCount = 0;
let timerInterval = null;
let elapsedSeconds = 0;
let timerRunning = false;
let currentDifficulty = 'medium';
let gameCompleted = false;
let scoreRecorded = false;
const THEME_STORAGE_KEY = 'sudoku_theme';

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.body.classList.toggle('dark-mode', isDark);
  const toggle = document.getElementById('theme-toggle');
  toggle.innerText = isDark ? 'Light Mode' : 'Dark Mode';
  toggle.setAttribute('aria-pressed', String(isDark));
  toggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
}

function toggleTheme() {
  const nextTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
  localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  applyTheme(nextTheme);
}

function setMessage(text, state) {
  const message = document.getElementById('message');
  message.className = state ? `message-${state}` : '';
  message.innerText = text;
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function resetTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  elapsedSeconds = 0;
  timerRunning = false;
  document.getElementById('timer').innerText = 'Time: 00:00';
}

function startTimer() {
  if (timerRunning) return;
  timerRunning = true;
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    document.getElementById('timer').innerText = `Time: ${formatTime(elapsedSeconds)}`;
  }, 1000);
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  timerRunning = false;
}

function getLeaderboard() {
  const data = localStorage.getItem('sudoku_leaderboard');
  return data ? JSON.parse(data) : [];
}

function saveLeaderboard(leaderboard) {
  localStorage.setItem('sudoku_leaderboard', JSON.stringify(leaderboard));
}

function addScore(name, time, difficulty, hints) {
  if (scoreRecorded) return;

  let leaderboard = getLeaderboard();
  leaderboard.push({
    name: name || 'Anonymous',
    time: time,
    difficulty: difficulty,
    hints: hints,
    timestamp: new Date().getTime()
  });
  
  // Sort by time (ascending)
  leaderboard.sort((a, b) => a.time - b.time);
  
  // Keep only top 10
  leaderboard = leaderboard.slice(0, 10);
  
  saveLeaderboard(leaderboard);
  displayLeaderboard();
  scoreRecorded = true;
}

function displayLeaderboard() {
  const leaderboard = getLeaderboard();
  const tbody = document.getElementById('leaderboard-body');
  
  if (leaderboard.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">No scores yet</td></tr>';
    return;
  }
  
  tbody.innerHTML = '';
  leaderboard.forEach((entry, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${entry.name}</td>
      <td>${formatTime(entry.time)}</td>
      <td>${entry.difficulty}</td>
      <td>${entry.hints}</td>
    `;
    tbody.appendChild(row);
  });
}

function clearLeaderboard() {
  if (confirm('Are you sure you want to clear the leaderboard?')) {
    localStorage.removeItem('sudoku_leaderboard');
    displayLeaderboard();
  }
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
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
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
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  currentDifficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${currentDifficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  hintCount = 0;
  gameCompleted = false;
  scoreRecorded = false;
  document.getElementById('hint-count').innerText = 'Hints Used: 0';
  document.getElementById('message').innerText = '';
  resetTimer();
  startTimer();
}

function collectBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const input = inputs[i * SIZE + j];
      const value = input ? input.value.trim() : '';
      const parsedValue = value === '' ? 0 : Number(value);
      board[i][j] = Number.isInteger(parsedValue) ? parsedValue : 0;
    }
  }

  return board;
}

async function getHint() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = collectBoard();
  
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ board })
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  
  if (data.error) {
    setMessage(data.error, 'error');
    return;
  }
  
  const idx = data.row * SIZE + data.col;
  const inp = inputs[idx];
  
  inp.value = data.value;
  inp.disabled = true;
  inp.className = 'sudoku-cell hinted';
  
  hintCount = data.hints_used;
  document.getElementById('hint-count').innerText = `Hints Used: ${hintCount}`;
  setMessage('Hint revealed!', 'success');
}

async function checkSolution() {
  if (gameCompleted) return;

  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = collectBoard();
  
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    setMessage(data.error, 'error');
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    gameCompleted = true;
    setMessage('Congratulations! You solved it!', 'success');
    stopTimer();
    showNameModal();
  } else {
    setMessage('Some cells are incorrect.', 'error');
  }
}

function showNameModal() {
  document.getElementById('modal-time').innerText = formatTime(elapsedSeconds);
  document.getElementById('modal-hints').innerText = hintCount;
  document.getElementById('modal-difficulty').innerText = currentDifficulty;
  document.getElementById('player-name').value = '';
  document.getElementById('name-modal').style.display = 'block';
}

function hideNameModal() {
  document.getElementById('name-modal').style.display = 'none';
}

// Wire buttons
window.addEventListener('load', () => {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || 'light';
  applyTheme(savedTheme);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', getHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('submit-name').addEventListener('click', () => {
    const name = document.getElementById('player-name').value.trim();
    addScore(name, elapsedSeconds, currentDifficulty, hintCount);
    hideNameModal();
  });
  document.getElementById('skip-name').addEventListener('click', () => {
    addScore('Anonymous', elapsedSeconds, currentDifficulty, hintCount);
    hideNameModal();
  });
  document.getElementById('clear-leaderboard').addEventListener('click', clearLeaderboard);
  
  // Close modal if clicking outside
  document.getElementById('name-modal').addEventListener('click', (e) => {
    if (e.target.id === 'name-modal') {
      addScore('Anonymous', elapsedSeconds, currentDifficulty, hintCount);
      hideNameModal();
    }
  });
  
  // initialize
  displayLeaderboard();
  newGame();
});