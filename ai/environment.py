import numpy as np

from game.game_logic import TicTacToe2  # Assuming this is your original class

# Fixed action space: piece_size in {1, 2, 3}, x in {0, 1, 2}, y in {0, 1, 2}
# -> 3 * 3 * 3 = 27 discrete actions.
PIECE_SIZES = (1, 2, 3)
BOARD_SIZE = 3
NUM_ACTIONS = len(PIECE_SIZES) * BOARD_SIZE * BOARD_SIZE


class TicTacToeEnv(TicTacToe2):  # Inherit all the game logic
    def __init__(self):
        super().__init__()  # Initialize the parent class

    def reset(self):
        super().reset_board()  # Use existing reset logic
        return self.get_state()  # Return the state for RL

    # --- Action <-> move mapping -------------------------------------------
    @staticmethod
    def action_to_move(action):
        """Decode a flat action index into a (piece_size, x, y) move."""
        piece_idx, cell = divmod(action, BOARD_SIZE * BOARD_SIZE)
        x, y = divmod(cell, BOARD_SIZE)
        return PIECE_SIZES[piece_idx], x, y

    @staticmethod
    def move_to_action(piece_size, x, y):
        """Encode a (piece_size, x, y) move into a flat action index."""
        piece_idx = PIECE_SIZES.index(piece_size)
        return piece_idx * (BOARD_SIZE * BOARD_SIZE) + x * BOARD_SIZE + y

    def legal_action_mask(self):
        """
        Return a boolean mask of shape (NUM_ACTIONS,) where True marks a
        currently legal action for the current player. Use this to prevent
        the agent from ever selecting an illegal move.
        """
        mask = np.zeros(NUM_ACTIONS, dtype=bool)
        for piece_size, x, y in self.get_possible_moves():
            mask[self.move_to_action(piece_size, x, y)] = True
        return mask

    # --- Environment step ---------------------------------------------------
    def step(self, action, zero_sum: bool = False):
        """
        Apply a flat action index. Agents are expected to only select legal actions
        using the legal_action_mask, so illegal moves should never occur.
        
        Args:
            action: The flat action index to execute (must be legal).
            zero_sum: If True, returns (reward_for_mover, reward_for_opponent) tuple
                      in info dict to support zero-sum reward signals.
        
        Returns:
            (state, reward, done, info) tuple.
            
        Reward structure:
            +3   for winning
            -1   for losing  (assigned by run.py to the prior agent transition)
            -1   for draw    (same penalty as losing — strongly incentivises winning)
             0   for ongoing game
        """
        piece_size, x, y = self.action_to_move(action)

        # Assert move is valid - agents should only pick legal moves
        assert self.is_valid_move(piece_size, x, y), \
            f"Illegal move attempted: piece={piece_size}, x={x}, y={y}. Use legal_action_mask!"

        self.make_move(piece_size, x, y)
        
        won = self.check_winner(x, y)
        draw = self.check_draw() if not won else False
        done = won or draw
        
        # Reward from current mover's perspective
        if won:
            reward = 3.0
        elif draw:
            reward = -1.0
        else:
            reward = 0.0
        
        info = {}
        
        # Zero-sum rewards: provide explicit loss signal for opponent
        if zero_sum:
            if won:
                info["reward_mover"] = 3.0
                info["reward_opponent"] = -1.0
            elif draw:
                info["reward_mover"] = -1.0
                info["reward_opponent"] = -1.0
            else:
                info["reward_mover"] = 0.0
                info["reward_opponent"] = 0.0

        if not done:
            self.current_player = 3 - self.current_player  # Switch player

        info["legal_action_mask"] = self.legal_action_mask()
        return self.get_state(), reward, done, info

    def get_state(self):
        # board_owners / board_pieces are plain Python lists of lists in the
        # game logic, so convert to NumPy arrays before flattening.
        owners_flat = np.array(self.board_owners, dtype=np.int64).flatten()
        pieces_flat = np.array(self.board_pieces, dtype=np.int64).flatten()
        player_pieces = self.player_pieces[self.current_player]
        opponent_pieces = self.player_pieces[3 - self.current_player]
        player_pieces_padded = player_pieces + [0] * (6 - len(player_pieces))
        opponent_pieces_padded = opponent_pieces + [0] * (6 - len(opponent_pieces))
        return (
            owners_flat.tolist()
            + pieces_flat.tolist()
            + player_pieces_padded
            + opponent_pieces_padded
        )
