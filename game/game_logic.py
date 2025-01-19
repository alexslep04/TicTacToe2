class TicTacToe2:
    def __init__(self):
        self.player1_pieces = [1, 1, 2, 2, 3, 3]
        self.player2_pieces = [1, 1, 2, 2, 3, 3]
        self.board_pieces = [[0] * 3 for _ in range(3)]  # Piece sizes
        self.board_owners = [[0] * 3 for _ in range(3)]  # Player ownership
        self.current_player = 1  # 1 = player 1, 2 = player 2

    def turn(self):
        """
        Alternates turns and handles player moves.
        - Gets player input for piece size and position.
        - Validates the move using is_valid_move.
        - If valid, calls make_move.
        - Checks for a winner or draw after the move.
        - Alternates the current player if no winner or draw.
        """
        pass

    def is_valid_move(self, player, piece_size, x, y):
        """
        Validates the player's move.
        - Ensures the move is within board bounds.
        - Checks that the piece size is larger than the current piece on the board.
        - Verifies the player has the selected piece available.
        """
        pass

    def make_move(self, player, piece_size, x, y):
        """
        Executes a move.
        - Updates the board_pieces and board_owners arrays.
        - Calls deincrement_piece to remove the used piece from the player's hand.
        - Checks for a winner using check_winner.
        - If no winner, calls check_draw to determine if the game is a draw.

        # checks if move is valid
        # if true -> update both boards and remove piece from players hand
        # else -> check for draw
        # if true -> give end of game message and reset board 
        # else -> give invalid move message
        
        """
        pass

    def check_winner(self):
        """
        Checks if there is a winner.
        - Evaluates rows, columns, and diagonals for three consecutive pieces owned by the same player.
        - Returns True if a winner is found, False otherwise.
        """
        pass

    def check_draw(self):
        """
        Calls the possiblemoves method.
        - Returns True if method returns 0/null/none.
        - Returns False otherwise.
        """
        pass

    def reset_board(self):
        """
        Resets the game board for a new game.
        - Reinitializes player pieces, board_pieces, and board_owners.
        - Sets current_player to Player 1.
        """
        self.__init__()

    def deincrement_piece(self, player, piece_size):
        """
        Removes a used piece from the player's available pieces.
        - Modifies player1_pieces or player2_pieces based on the player.
        """
        pass

    def get_possible_moves(self, player):
        """
        Returns all valid moves for the given player.
        - Generates a list of tuples (piece_size, x, y) representing possible moves.
        - This will be used for AI implementation later.
        """
        pass

    def print_board(self):
        """
        Prints the current state of the board for debugging.
        - Displays piece sizes and ownership in a readable format.
        """
        pass
