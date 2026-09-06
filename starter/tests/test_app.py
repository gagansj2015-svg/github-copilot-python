import sudoku_logic
from app import CURRENT


def test_index_route_renders_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'id="sudoku-board"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'Dark Mode' in response.data


def test_new_game_route_returns_puzzle(client):
    response = client.get('/new')

    assert response.status_code == 200
    data = response.get_json()
    puzzle = data['puzzle']

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(cell in range(sudoku_logic.SIZE + 1) for row in puzzle for cell in row)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35


def test_new_game_with_difficulty_easy(client):
    response = client.get('/new?difficulty=easy')

    assert response.status_code == 200
    data = response.get_json()
    puzzle = data['puzzle']
    clue_count = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)

    assert clue_count == 45
    assert data['difficulty'] == 'easy'


def test_new_game_with_difficulty_medium(client):
    response = client.get('/new?difficulty=medium')

    assert response.status_code == 200
    data = response.get_json()
    puzzle = data['puzzle']
    clue_count = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)

    assert clue_count == 35
    assert data['difficulty'] == 'medium'


def test_new_game_with_difficulty_hard(client):
    response = client.get('/new?difficulty=hard')

    assert response.status_code == 200
    data = response.get_json()
    puzzle = data['puzzle']
    clue_count = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)

    assert clue_count == 25
    assert data['difficulty'] == 'hard'


def test_check_route_requires_game_in_progress(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_route_accepts_correct_solution(client):
    client.get('/new')
    solution = sudoku_logic.deep_copy(CURRENT['solution'])

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_route_reports_incorrect_cells(client):
    client.get('/new')
    board = sudoku_logic.deep_copy(CURRENT['solution'])
    board[0][0] = board[0][0] % sudoku_logic.SIZE + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert [0, 0] in response.get_json()['incorrect']


def test_hint_route_requires_game_in_progress(client):
    response = client.post('/hint', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_hint_route_returns_empty_cell_with_solution_value(client):
    client.get('/new')
    puzzle = CURRENT['puzzle']
    
    # Create a board from the puzzle (all clues present, empties as 0)
    board = sudoku_logic.deep_copy(puzzle)

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    data = response.get_json()
    assert 'row' in data
    assert 'col' in data
    assert 'value' in data
    assert 'hints_used' in data
    assert data['value'] in range(1, sudoku_logic.SIZE + 1)
    assert board[data['row']][data['col']] == sudoku_logic.EMPTY


def test_hint_route_fills_first_empty_cell(client):
    client.get('/new')
    puzzle = CURRENT['puzzle']
    board = sudoku_logic.deep_copy(puzzle)
    
    response = client.post('/hint', json={'board': board})
    data = response.get_json()
    
    first_empty_row = None
    first_empty_col = None
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == sudoku_logic.EMPTY:
                first_empty_row = i
                first_empty_col = j
                break
        if first_empty_row is not None:
            break
    
    assert data['row'] == first_empty_row
    assert data['col'] == first_empty_col


def test_hint_route_increments_hints_used_counter(client):
    client.get('/new')
    puzzle = CURRENT['puzzle']
    board = sudoku_logic.deep_copy(puzzle)
    
    response1 = client.post('/hint', json={'board': board})
    hints_used_1 = response1.get_json()['hints_used']
    data1 = response1.get_json()
    
    # Fill the first hinted cell in the board
    board[data1['row']][data1['col']] = data1['value']
    
    response2 = client.post('/hint', json={'board': board})
    hints_used_2 = response2.get_json()['hints_used']
    
    assert hints_used_1 == 1
    assert hints_used_2 == 2


def test_new_game_resets_hints_used_counter(client):
    client.get('/new')
    puzzle = CURRENT['puzzle']
    board = sudoku_logic.deep_copy(puzzle)
    client.post('/hint', json={'board': board})
    
    response = client.get('/new')
    assert CURRENT['hints_used'] == 0
