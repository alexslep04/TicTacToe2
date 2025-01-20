class TicTacToe2:
    def __init__(self):
        self.player_pieces = {
            1: [1, 1, 2, 2, 3, 3],
            2: [1, 1, 2, 2, 3, 3]
            }
        self.board_pieces = [[0] * 3 for _ in range(3)]  # Piece sizes
        self.board_owners = [[0] * 3 for _ in range(3)]  # Player ownership
        self.current_player = 1  # 1 = player 1, 2 = player 2

    def turn(self):
        while True:
            # Display the current state of the board (optional)
            self.print_board()
            print(self.player_pieces)
    
            # Get input from the current player
            piece_size = int(input(f"Player {self.current_player}, select a piece size: "))
            x = int(input(f"Player {self.current_player}, select the row (0-2): "))
            y = int(input(f"Player {self.current_player}, select the column (0-2): "))
    
            # Validate the move
            if not self.is_valid_move(piece_size, x, y):
                print("Invalid move! Try again.")
                continue  # Skip to the next iteration
    
            # Make the move
            self.make_move(self.current_player, piece_size, x, y)
    
            # Check for a winner
            if self.check_winner():
                self.print_board()
                print(f"Player {self.current_player} wins!")
                break
    
            # Check for a draw
            if self.check_draw():
                self.print_board()
                print("It's a draw!")
                break
    
            # Alternate the player
            self.current_player = 1 if self.current_player == 2 else 2
            
    def get_current_player_pieces(self):
        """
        Returns the pieces of the current player.
        """
        return self.player_pieces[self.current_player]
            
    def is_valid_move(self, piece_size, x, y):
        """
        Validates whether the given move is valid.
        """
        # Check if the coordinates are within bounds
        if not (0 <= x < 3 and 0 <= y < 3):
            return False

        # Check if the piece_size is valid for the current player
        if piece_size not in self.get_current_player_pieces():
            return False

        # Check if the piece is larger than the current piece at the board location
        if piece_size <= self.board_pieces[x][y]:
            return False

        return True

    def make_move(self, player, piece_size, x, y):
        """
        Executes a move.
        - Updates the board_pieces and board_owners arrays.
        - Calls deincrement_piece to remove the used piece from the player's hand.
        - Checks for a winner using check_winner.
        - If no winner, calls check_draw to determine if the game is a draw.

        
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
