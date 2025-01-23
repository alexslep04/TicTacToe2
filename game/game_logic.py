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
            piece_size = int(input(f"Player {self.current_player}, select a piece size (1-3): "))
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

    def make_move(self, piece_size, x, y):
        """
        Executes a move.
        - Updates the board_pieces and board_owners arrays.
        - Calls deincrement_piece to remove the used piece from the player's hand.
        """
        self.board_pieces[x][y] = piece_size
        self.board_owners[x][y] = self.current_player
        self.decrement_piece(self.current_player, piece_size)
    
    def check_winner(self, x, y):
        """
        Checks if there is a winner after a move at (x, y).
        - Evaluates the row, column, and diagonals intersecting (x, y).
        - Returns True if the current_player has three in a row, False otherwise.
        """
        player = self.current_player

        # Check row
        if self.board_owners[x][0] == self.board_owners[x][1] == self.board_owners[x][2] == player:
            return True

        # Check column
        if self.board_owners[0][y] == self.board_owners[1][y] == self.board_owners[2][y] == player:
            return True

        # Check diagonals (only if (x, y) is on a diagonal)
        if x == y and self.board_owners[0][0] == self.board_owners[1][1] == self.board_owners[2][2] == player:
            return True
        if x + y == 2 and self.board_owners[0][2] == self.board_owners[1][1] == self.board_owners[2][0] == player:
            return True

        return False

    def check_draw(self):
        """
        Calls the possiblemoves method.
        - Returns True if method returns 0/null/none.
        - Returns False otherwise.
        """
        possible_moves = self.get_possible_moves()
        return len(possible_moves) == 0

    def reset_board(self):
        """
        Resets the game board for a new game.
        - Reinitializes player pieces, board_pieces, and board_owners.
        - Sets current_player to Player 1.
        """
        self.__init__()

    def decrement_piece(self, piece_size):
        """
        Removes a used piece from the player's available pieces.
        """
        if piece_size in self.player_pieces[self.current_player]:
            self.player_pieces[self.current_player].remove(piece_size)

    def get_possible_moves(self):
        """
        Returns all valid moves for the current player.
        - Generates a list of tuples (piece_size, x, y) representing possible moves.
        """
        possible_moves = []
        
        # Get the pieces available to the current player
        player_pieces = self.get_current_player_pieces()

        # Traverse the board
        for x in range(3):
            for y in range(3):
                # Get the piece currently on the board
                current_board_piece = self.board_pieces[x][y]

                # Check each unique piece size the player has
                for piece_size in set(player_pieces):
                    # If the player's piece is larger than the board piece, add it as a valid move
                    if piece_size > current_board_piece:
                        possible_moves.append((piece_size, x, y))

        return possible_moves

    def print_board(self):
        """
        Prints the current state of the board for debugging.
        - Displays piece sizes and ownership in a readable format.
        """
        print("Board Pieces:")
        for row in self.board_pieces:
            print(row)
        print("\nBoard Owners:")
        for row in self.board_owners:
            print(row)
