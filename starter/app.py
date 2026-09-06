from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
    'difficulty': 'medium'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium').lower()
    
    # Map difficulty to clues count
    difficulty_clues = {
        'easy': 45,
        'medium': 35,
        'hard': 25
    }
    clues = difficulty_clues.get(difficulty, 35)
    
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    CURRENT['difficulty'] = difficulty
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

@app.route('/hint', methods=['POST'])
def hint():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None or board is None:
        return jsonify({'error': 'No game in progress'}), 400
    
    # Find the first empty cell in the CURRENT board state
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == sudoku_logic.EMPTY:
                # Found an empty cell, increment counter and return
                CURRENT['hints_used'] += 1
                return jsonify({
                    'row': i,
                    'col': j,
                    'value': solution[i][j],
                    'hints_used': CURRENT['hints_used']
                })
    
    # No empty cells found (puzzle is complete)
    return jsonify({'error': 'No empty cells available'}), 400

if __name__ == '__main__':
    app.run(debug=True)