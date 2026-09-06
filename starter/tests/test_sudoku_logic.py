import sudoku_logic


def is_valid_solution(board):
    expected_values = set(range(1, sudoku_logic.SIZE + 1))
    rows_valid = all(set(row) == expected_values for row in board)
    columns_valid = all(
        {board[row][column] for row in range(sudoku_logic.SIZE)} == expected_values
        for column in range(sudoku_logic.SIZE)
    )
    boxes_valid = all(
        {
            board[row][column]
            for row in range(box_row, box_row + 3)
            for column in range(box_column, box_column + 3)
        }
        == expected_values
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    )
    return rows_valid and columns_valid and boxes_valid


def test_create_empty_board_returns_empty_9_by_9_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_does_not_share_nested_rows():
    original = [[1, 2], [3, 4]]
    copied = sudoku_logic.deep_copy(original)
    copied[0][0] = 9

    assert original[0][0] == 1
    assert copied[0][0] == 9


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 1, 1, 6)


def test_fill_board_creates_valid_solution():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert is_valid_solution(board)


def test_count_solutions_returns_zero_for_invalid_puzzle():
    board = sudoku_logic.create_empty_board()
    # Fill a 3x3 box with all 1s - impossible to solve
    for i in range(3):
        for j in range(3):
            board[i][j] = 1

    count = sudoku_logic.count_solutions(board, limit=2)
    assert count == 0


def test_count_solutions_returns_one_for_valid_unique_puzzle():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    count = sudoku_logic.count_solutions(puzzle, limit=2)
    assert count == 1


def test_complete_board_has_exactly_one_solution():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    count = sudoku_logic.count_solutions(board, limit=2)
    assert count == 1


def test_count_solutions_stops_early_at_limit():
    puzzle, _ = sudoku_logic.generate_puzzle(clues=35)

    count = sudoku_logic.count_solutions(puzzle, limit=1)
    assert count == 1


def test_generated_puzzle_has_exactly_one_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert is_valid_solution(solution)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert all(
        puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_many_generated_puzzles_have_unique_solutions():
    for _ in range(10):
        puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
        solution_count = sudoku_logic.count_solutions(puzzle, limit=2)
        assert solution_count == 1, f"Generated puzzle does not have unique solution: {solution_count} solutions found"
