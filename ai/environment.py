import numpy as np

from game.game_logic import TicTacToe2  # Assuming this is your original class

class TicTacToeEnv(TicTacToe2):  # Inherit all the game logic
    def __init__(self):
        super().__init__()  # Initialize the parent class

    def reset(self):
        super().reset_board()  # Use existing reset logic
        return self.get_state()  # Return the state for RL

    def step(self, piece_size, x, y):
        if not self.is_valid_move(piece_size, x, y):
            return self.get_state(), -10, True  # Penalty for invalid move

        self.make_move(piece_size, x, y)
        reward, done = (1, True) if self.check_winner(x, y) else (0, self.check_draw())

        if not done:
            self.current_player = 3 - self.current_player  # Switch player

        return self.get_state(), reward, done

    def get_state(self):
        owners_flat = self.board_owners.flatten()
        pieces_flat = self.board_pieces.flatten()
        player_pieces = self.player_pieces[self.current_player]
        opponent_pieces = self.player_pieces[3 - self.current_player]
        player_pieces_padded = player_pieces + [0] * (6 - len(player_pieces))
        opponent_pieces_padded = opponent_pieces + [0] * (6 - len(opponent_pieces))
        return owners_flat.tolist() + pieces_flat.tolist() + player_pieces_padded + opponent_pieces_padded
