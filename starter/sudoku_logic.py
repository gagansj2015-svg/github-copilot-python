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

def count_solutions(puzzle, limit=2):
    """
    Count the number of solutions in a puzzle using backtracking.
    Stops early once limit is reached (optimization).
    Returns the count (0, 1, or >= limit).
    """
    solutions = [0]  # Use list to allow modification in nested function

    def is_valid_partial(board):
        """Check if current state has no obvious conflicts."""
        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] != EMPTY:
                    num = board[row][col]
                    board[row][col] = EMPTY
                    if not is_safe(board, row, col, num):
                        board[row][col] = num
                        return False
                    board[row][col] = num
        return True

    def solve(board, row=0, col=0):
        if solutions[0] >= limit:
            return False

        if row == SIZE:
            solutions[0] += 1
            return False

        next_row, next_col = (row, col + 1) if col + 1 < SIZE else (row + 1, 0)

        if board[row][col] != EMPTY:
            return solve(board, next_row, next_col)

        for num in range(1, SIZE + 1):
            if is_safe(board, row, col, num):
                board[row][col] = num
                solve(board, next_row, next_col)
                board[row][col] = EMPTY

        return False

    puzzle_copy = deep_copy(puzzle)
    
    if not is_valid_partial(puzzle_copy):
        return 0
    
    solve(puzzle_copy)
    return solutions[0]


def remove_cells(board, clues):
    """
    Remove cells from a completed board to create a puzzle with exactly one solution.
    This ensures every generated puzzle is mathematically valid.
    """
    cells_to_remove = SIZE * SIZE - clues
    removed_count = 0

    while removed_count < cells_to_remove:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)

        if board[row][col] != EMPTY:
            backup = board[row][col]
            board[row][col] = EMPTY

            puzzle_copy = deep_copy(board)
            if count_solutions(puzzle_copy, limit=2) == 1:
                removed_count += 1
            else:
                board[row][col] = backup

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
