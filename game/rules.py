class Rules:
    @staticmethod
    def is_valid_move(board, x, y, piece):
        """
        Check if placing a piece at (x, y) is valid.
        """
        current_cell = board.get_cell(x, y)
        if current_cell is None:
            return True  # Cell is empty
        current_piece, _ = current_cell  # Unpack the piece and player
        size_priority = board.size_priority
        return size_priority[piece] > size_priority[current_piece]  # New piece must be larger

    @staticmethod
    def check_winner(board):
        """
        Check if there's a winner on the board.
        """
        grid = board.grid
        # Check rows and columns
        for i in range(3):
            # Check row
            if grid[i][0] and grid[i][0] == grid[i][1] == grid[i][2]:
                return grid[i][0][1]  # Return the player
            # Check column
            if grid[0][i] and grid[0][i] == grid[1][i] == grid[2][i]:
                return grid[0][i][1]  # Return the player

        # Check diagonals
        if grid[0][0] and grid[0][0] == grid[1][1] == grid[2][2]:
            return grid[0][0][1]  # Return the player
        if grid[0][2] and grid[0][2] == grid[1][1] == grid[2][0]:
            return grid[0][2][1]  # Return the player

        # No winner
        return None

    @staticmethod
    def is_draw(board):
        """
        Check if the game is a draw.
        """
        for row in board.grid:
            for cell in row:
                if cell is None:
                    return False  # At least one empty cell, not a draw
        # If all cells are filled and there's no winner, it's a draw
        return Rules.check_winner(board) is None

            