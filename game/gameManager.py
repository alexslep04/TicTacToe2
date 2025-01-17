from board import Board

class GameManager:
    def __init__(self, player1, player2):
        """Initialize the Game Manager with two players and a board."""
        self.board = Board()
        self.players = {1: player1, 2: player2}
        self.current_player = 1  # Player 1 starts
        self.game_state = "ongoing"  # States: "ongoing", "win", "draw"

    def start_game(self):
        """Start the game by resetting the board and pieces."""
        print("Starting a new game!")
        self.board.reset()
        for player in self.players.values():
            player.reset_pieces()
        self.game_state = "ongoing"
        self.play_game()

    def play_game(self):
        """Main game loop to alternate turns until there's a winner or draw."""
        while self.game_state == "ongoing":
            self.play_turn()

    def play_turn(self):
        """Handle the current player's turn."""
        current_player = self.players[self.current_player]
        print(f"\n{current_player.name}'s turn! Pieces: {current_player.pieces}")

        # Prompt for user input (replace this with GUI or AI logic if needed)
        try:
            x = int(input("Enter the row (0-2): "))
            y = int(input("Enter the column (0-2): "))
            piece = input("Enter the piece size (S, M, L): ").strip().upper()

            # Attempt to place the piece
            result = self.board.place_piece(x, y, piece, self.current_player, 
                                            {1: self.players[1].pieces, 2: self.players[2].pieces})
            if result == "Winner":
                print(f"\n{current_player.name} wins the game!")
                self.game_state = "win"
            elif result == "Draw":
                print("\nThe game ends in a draw!")
                self.game_state = "draw"
            elif result is True:
                print(f"{current_player.name} placed {piece} at ({x}, {y}).")
                self.current_player = 2 if self.current_player == 1 else 1  # Switch turns
            else:
                print("Invalid move, try again.")
        except ValueError as e:
            print(f"Invalid input: {e}. Try again!")
        except Exception as e:
            print(f"Error: {e}. Try again!")

    def end_game(self):
        """Handle end-of-game logic."""
        print("\nGame Over!")
        if self.game_state == "win":
            winner = self.players[self.current_player]
            print(f"Congratulations, {winner.name}!")
        elif self.game_state == "draw":
            print("It's a tie!")
        print("Thanks for playing!")
