class TicTacToe2:
    def __init__(self):
        self.player1_pieces = [1, 1, 2, 2, 3, 3]
        self.player2_pieces = [1, 1, 2, 2, 3, 3]
        self.board_pieces = [[0] * 3 for _ in range(3)]  # Piece sizes
        self.board_owners = [[0] * 3 for _ in range(3)]  # Player ownership
        self.current_player = 1  # 1 = player 1, 2 = player 2

    def turn(self):
        """Alternates turns and handles player moves."""
        pass

    def is_valid_move(self, player, piece_size, x, y):
        """Validates the player's move."""
        pass

    def make_move(self, player, piece_size, x, y):
        """Executes a move."""
        pass

    def check_winner(self):
        """Checks if there is a winner."""
        pass

    def reset_board(self):
        """Resets the game board for a new game."""
        self.__init__()

    def get_possible_moves(self, player):
        """Returns all valid moves for the given player.
        this will be for ai later you can ignore it for now
        """
        pass

    def print_board(self):
        """Prints the current state of the board for debugging."""
        pass
