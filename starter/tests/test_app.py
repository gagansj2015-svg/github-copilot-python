import sudoku_logic
from app import CURRENT


def test_index_route_renders_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'id="sudoku-board"' in response.data


def test_new_game_route_returns_puzzle(client):
    response = client.get('/new')

    assert response.status_code == 200
    data = response.get_json()
    puzzle = data['puzzle']

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(cell in range(sudoku_logic.SIZE + 1) for row in puzzle for cell in row)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35


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
