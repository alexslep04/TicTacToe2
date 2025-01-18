from game.board import Board

class GameManager:
    def __init__(self, player1, player2, renderer, events):
        """Initialize the Game Manager with players, renderer, and event handler."""
        self.board = Board()  # Initialize the board internally
        self.players = {1: player1, 2: player2}
        self.renderer = renderer  # Renderer for UI
        self.events = events  # Event handler for input
        self.current_player = 1  # Player 1 starts
        self.selected_piece = None  # Track the currently selected piece
        self.game_state = "ongoing"  # States: "ongoing", "win", "draw"

    def start_game(self):
        """Start the game by resetting the board and pieces."""
        self.board.reset()
        for player in self.players.values():
            player.reset_pieces()
        self.game_state = "ongoing"
        self.run_game_loop()

    def run_game_loop(self):
        """Main game loop."""
        while self.game_state == "ongoing":
            self.renderer.draw_board(self.board, self.players, self.current_player, self.selected_piece)
            event = self.events.get_event()

            if event:
                if event["type"] == "select_piece":
                    self.select_piece(event["piece"])
                elif event["type"] == "place_piece":
                    x, y = event["coordinates"]
                    self.place_piece_on_board(x, y)

            self.check_game_state()

    def select_piece(self, piece):
        """Handle piece selection."""
        current_player = self.players[self.current_player]
        if piece in current_player.pieces and current_player.pieces[piece] > 0:
            self.selected_piece = piece
            self.renderer.highlight_piece(piece)  # Highlight the selected piece
        else:
            self.renderer.show_message("Invalid selection. Try again!")

    def place_piece_on_board(self, x, y):
        """Attempt to place the selected piece on the board."""
        if self.selected_piece is None:
            self.renderer.show_message("No piece selected!")
            return

        current_player = self.players[self.current_player]
        try:
            result = self.board.place_piece(x, y, self.selected_piece, self.current_player,
                                            {1: self.players[1].pieces, 2: self.players[2].pieces})
            if result == True:
                self.selected_piece = None  # Clear selection after a valid move
                self.renderer.show_message(f"Placed piece at ({x}, {y})")
            elif result == "Winner":
                self.game_state = "win"
                self.renderer.show_message(f"{current_player.name} wins!")
            elif result == "Draw":
                self.game_state = "draw"
                self.renderer.show_message("It's a draw!")
            else:
                self.renderer.show_message("Invalid move. Try again!")
        except Exception as e:
            self.renderer.show_message(f"Error: {e}")

    def check_game_state(self):
        """Check if the game is over or proceed to the next turn."""
        if self.game_state == "ongoing":
            self.current_player = 2 if self.current_player == 1 else 1  # Switch turns
        else:
            self.end_game()

    def end_game(self):
        """Handle end-of-game logic."""
        self.renderer.show_message("Game Over!")
        if self.game_state == "win":
            winner = self.players[self.current_player]
            self.renderer.show_message(f"Congratulations, {winner.name}!")
        elif self.game_state == "draw":
            self.renderer.show_message("It's a tie!")
