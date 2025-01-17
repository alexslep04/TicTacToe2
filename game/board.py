class Board:
    def __init__(self):
        """Initialize a 3x3 grid for the board."""
        self.grid = [[None for _ in range(3)] for _ in range(3)]
        self.size_priority = {'S': 1, 'M': 2, 'L': 3}

    def is_valid_move(self, x, y, piece):
        """Check if a move is valid."""
        current_cell = self.grid[x][y]
        if current_cell is None:
            return True  # Empty cell
        return self.size_priority[piece] > self.size_priority[current_cell[0]]


    def place_piece(self, x, y, piece, player, player_pieces):
        """Place a piece on the board if valid, then check for a winner or a draw."""
        if self.is_valid_move(x, y, piece):
            self.grid[x][y] = (piece, player)
            # Remove the placed piece from the player's available pieces
            player_pieces[player].remove(piece)
            # Check for a winner
            if self.check_winner(player, x, y):
                return "Winner"
            # Check for a draw
            if self.is_draw(player_pieces):
                return "Draw"
            return True  # Piece placed, no winner or draw
        return False  # Invalid move

    def is_draw(self, player_pieces):
        """
        Check if the game is a draw.
        :param player_pieces: A dictionary of player pieces, e.g., {1: ['S', 'M', 'L'], 2: ['S', 'M']}
        :return: True if the game is a draw, False otherwise.
        """
        # Check for empty cells
        for row in self.grid:
            if any(cell is None for cell in row):
                return False  # Early exit: Empty cell found, not a draw

        # Check if any player has a piece that can overwrite an existing one
        for x in range(3):
            for y in range(3):
                current_cell = self.grid[x][y]
                if current_cell is not None:
                    current_piece_size = self.size_priority[current_cell[0]]
                    for player, pieces in player_pieces.items():
                        for piece in pieces:
                            if self.size_priority[piece] > current_piece_size:
                                return False  # Early exit: Valid move found, not a draw

        # No empty cells and no valid moves possible
        return True

    def get_cell(self, x, y):
        """Return the content of a specific cell."""
        return self.grid[x][y]

    def reset(self):
        """Reset the board to its initial empty state."""
        self.grid = [[None for _ in range(3)] for _ in range(3)]

    def check_winner(self, player, x, y):
        """Check if the player has won based on their latest move."""
        
        def is_winning_line(cells):
            """Check if all cells in a line belong to the player."""
            return all(cell is not None and cell[1] == player for cell in cells)

        # Check the row
        if is_winning_line(self.grid[x]):
            return True

        # Check the column
        column = [self.grid[row][y] for row in range(3)]
        if is_winning_line(column):
            return True

        # Check main diagonal (if the move is on it)
        if x == y:
            main_diagonal = [self.grid[i][i] for i in range(3)]
            if is_winning_line(main_diagonal):
                return True

        # Check anti-diagonal (if the move is on it)
        if x + y == 2:
            anti_diagonal = [self.grid[i][2 - i] for i in range(3)]
            if is_winning_line(anti_diagonal):
                return True

        # No winning line found
        return False
