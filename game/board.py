class Board:
    def __init__(self):
        """Initialize a 3x3 grid for the board."""
        self.size_priority = {'S': 1, 'M': 2, 'L': 3}
        self.BOARD_SIZE = 3  # Allows scalability to larger grids
        self._initialize_board()

    def _initialize_board(self):
        """Helper to initialize the board."""
        self.grid = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]

    def is_valid_move(self, x, y, piece):
        """Check if a move is valid."""
        # Ensure x and y are within bounds
        if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
            return False

        current_cell = self.grid[x][y]
        # Check if cell is empty or the piece has a higher priority
        if current_cell is None:
            return True
        if isinstance(current_cell, tuple) and len(current_cell) == 2:
            return self.size_priority[piece] > self.size_priority[current_cell[0]]
        return False  # Invalid cell format

    def place_piece(self, x, y, piece, player, player_pieces):
        """Place a piece on the board if valid, then check for a winner or a draw."""
        # Input validation
        if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
            raise ValueError(f"Invalid move: Coordinates out of bounds. Received x={x}, y={y}.")
        if piece not in self.size_priority:
            raise ValueError(f"Invalid piece: {piece}")
        if piece not in player_pieces.get(player, []):
            raise ValueError(f"Invalid move: Player {player} does not own this piece.")

        # Place the piece if valid
        if self.is_valid_move(x, y, piece):
            self.grid[x][y] = (piece, player)
            player_pieces[player].remove(piece)
            if self.check_winner(player, x, y):
                return "Winner"
            if self.is_draw(player_pieces):
                return "Draw"
            return True  # Move successfully placed
        return False  # Invalid move

    def is_draw(self, player_pieces):
        """Check if the game is a draw."""
        # Check for empty cells
        for row in self.grid:
            if any(cell is None for cell in row):
                return False

        # Check if any valid moves are still possible
        for x in range(self.BOARD_SIZE):
            for y in range(self.BOARD_SIZE):
                current_cell = self.grid[x][y]
                if current_cell:
                    current_piece_size = self.size_priority[current_cell[0]]
                    for pieces in player_pieces.values():
                        if any(self.size_priority[piece] > current_piece_size for piece in pieces):
                            return False
        return True  # No empty cells and no valid moves

    def get_cell(self, x, y):
        """Return the content of a specific cell."""
        if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
            raise ValueError(f"Coordinates out of bounds. Received x={x}, y={y}.")
        return self.grid[x][y]

    def reset(self):
        """Reset the board to its initial empty state."""
        self._initialize_board()

    def check_winner(self, player, x, y):
        """Check if the player has won based on their latest move."""
        def is_winning_line(cells):
            """Check if all cells in a line belong to the player."""
            return all(cell is not None and cell[1] == player for cell in cells)

        lines_to_check = [
            self.grid[x],  # Row
            [self.grid[row][y] for row in range(self.BOARD_SIZE)],  # Column
        ]
        # Check diagonals if necessary
        if x == y:
            lines_to_check.append([self.grid[i][i] for i in range(self.BOARD_SIZE)])
        if x + y == self.BOARD_SIZE - 1:
            lines_to_check.append([self.grid[i][self.BOARD_SIZE - 1 - i] for i in range(self.BOARD_SIZE)])

        return any(is_winning_line(line) for line in lines_to_check)
# hi