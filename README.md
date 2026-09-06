# Flask Sudoku

A Flask Sudoku game with unique-solution puzzle generation, easy/medium/hard
difficulty levels, hints, a timer, completion validation, a local leaderboard,
and persisted Dark/Light Mode selection.

## Requirements

- Python 3.10 or newer
- A modern web browser such as Chrome, Firefox, or Edge

## Setup

From the repository root, open a terminal and enter the application directory:

```powershell
cd starter
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

For Windows Command Prompt, use:

```bat
.venv\Scripts\activate.bat
```

Install the project requirements:

```powershell
python -m pip install -r requirements.txt
```

## Run the application

Start Flask from the `starter` directory:

```powershell
python app.py
```

Open the application at <http://127.0.0.1:5000> in your browser.

## Run the tests

With the virtual environment activated and the terminal in the `starter`
directory, run the complete pytest suite:

```powershell
python -m pytest -q
```

The tests cover puzzle generation and uniqueness, difficulty routes, solution
checking, hints, and game-state behavior. Browser features such as the timer,
theme persistence, and localStorage leaderboard are implemented in the client
and can be exercised from the running application.

## Project Instructions

Use GitHub Copilot to refactor the code for this game to add more advanced features. The goal is to create a more modern and maintainable codebase and add additional functionality to the final product. You can use any combination of code completion and chat features, like Ask, Edit, or Agent modes.

- Errors should be handled gracefully with appropriate messages to the user.
- Implement a Sudoku board generator that creates a valid Sudoku puzzle with a unique solution.
- Add a timer to track how long it takes to solve the puzzle.
- Implement a solution checker that verifies if the user's solution is correct using event delegation.
- Add a difficulty selector to allow users to choose between easy, medium, and hard puzzles.
- Add a hint feature that provides clues for the user that are noted with unique colors.
- Add a check puzzle button that checks the current state of the board against the solution.
- User should get immediate feedback on their input, such as highlighting invalid entries.
- Top 10 scores should be saved in local storage and displayed on the page with the user's name, time taken, hints used, and difficulty level.
- The game should be responsive and work well on both desktop and mobile devices.
- UI colors should be visually appealing and accessible.
- Completed and correct puzzles should display a congratulatory message with the time taken and hints used and ask for the user's name for Top 10 times.
