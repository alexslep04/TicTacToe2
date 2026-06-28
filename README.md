# TicTacToe2

A variant of Tic Tac Toe with **stackable, sized pieces** ("Gobblet"-style), plus
the scaffolding for a Reinforcement Learning (RL) agent to learn to play it.

## The Game

Unlike classic Tic Tac Toe, each player has a limited set of pieces of three
different sizes. A larger piece can be placed on top of (cover) a smaller piece —
including the opponent's — which makes the strategy considerably deeper than the
standard game.

- Each player starts with the pieces `[1, 1, 2, 2, 3, 3]` (two each of sizes 1, 2, 3).
- A move consists of choosing a `piece_size` and a board cell `(x, y)`.
- A move is valid only if the chosen piece is bigger than the piece currently in
  that cell (and the player still has that piece available).
- Win by getting three cells you **own** in a row, column, or diagonal.
- A draw occurs when the current player has no valid moves remaining.

State is tracked with two 3x3 grids:
- `board_pieces` — the size of the piece occupying each cell.
- `board_owners` — which player (1 or 2) owns the top piece in each cell.

## Project Structure

```
TicTacToe2/
├── main.py                 # CLI entry point — play a human-vs-human game
├── requirements.txt        # pygame, numpy, torch
├── game/
│   ├── game_logic.py       # TicTacToe2 — core rules, board state, move validation
│   └── game_ui.py          # (empty) intended pygame UI
└── ai/
    ├── environment.py      # TicTacToeEnv — RL-style wrapper over game logic
    ├── agent.py            # (empty) intended RL agent / policy network
    ├── run.py              # (empty) intended training / evaluation loop
    └── utils.py            # (empty) intended helpers
```

## Running

Install dependencies and start a text-based game:

```bash
pip install -r requirements.txt
python main.py
```

You'll be prompted for a piece size (1-3), a row (0-2), and a column (0-2) each turn.

## Current Status

| Component                     | Status        |
| ----------------------------- | ------------- |
| Core game rules (`game_logic`)| Implemented   |
| CLI play (`main.py`)          | Implemented   |
| RL environment (`environment`)| Partial / WIP |
| Graphical UI (`game_ui.py`)   | Not started   |
| RL agent (`agent.py`)         | Not started   |
| Training loop (`run.py`)      | Not started   |
| Utilities (`utils.py`)        | Not started   |

## Reinforcement Learning Approach

The intended design treats the game as a standard RL environment and is set up to
be trained with PyTorch (`torch` is a declared dependency).

### Environment (`ai/environment.py`)

`TicTacToeEnv` subclasses the game logic and exposes a Gym-like interface:

- **`reset()`** — clears the board and returns the initial state.
- **`step(piece_size, x, y)`** — applies a move and returns
  `(state, reward, done)`.
- **`get_state()`** — flattens the game into a fixed-length feature vector:
  - 9 cell-owner values + 9 cell-piece sizes (board encoding),
  - the current player's remaining pieces, padded to length 6,
  - the opponent's remaining pieces, padded to length 6
  - (30 features total).

### Reward Structure

- `+1` for a winning move.
- `-10` for an illegal move (a strong shaping penalty).
- `0` for ongoing play and for draws.

### Self-Play Setup

After a non-terminal move the environment flips `current_player`, so a single
agent can be trained via self-play, alternating sides each turn.

## What's Missing / How to Improve

The RL side is currently only a partial environment — the agent, training loop,
and several design details still need work. Notable gaps and suggested
improvements:

### Bugs / correctness

- **State encoding will crash.** `get_state()` calls `board_owners.flatten()` and
  `board_pieces.flatten()`, but in `game_logic.py` these are plain Python lists of
  lists, not NumPy arrays. They need to be converted (e.g. `np.array(...).flatten()`)
  or stored as NumPy arrays from the start.
- **No action masking.** `get_possible_moves()` exists in the logic but isn't
  surfaced to the agent. Without masking, the agent must learn legality purely
  from the `-10` penalty, which is slow and noisy. Expose a legal-action mask in
  the state/step interface.
- **Reward sign for the opponent.** Because of self-play side-switching, a win is
  always `+1` from the mover's perspective, but there's no explicit `-1` signal
  to the player who just enabled the loss. Consider zero-sum rewards so the agent
  clearly learns to avoid setting up the opponent.

### Missing components

- **Agent (`agent.py`)** — implement a policy. Options: tabular Q-learning (the
  state space is small enough to be tractable), DQN, or a PPO/actor-critic network
  in PyTorch. A simple Minimax baseline would also be valuable for benchmarking.
- **Training loop (`run.py`)** — episode rollout, experience storage/replay,
  optimization steps, epsilon decay / exploration schedule, checkpointing, and
  logging of win/draw/loss rates over time.
- **Utilities (`utils.py`)** — model save/load, metrics, seeding, plotting.
- **Graphical UI (`game_ui.py`)** — `pygame` is a dependency but unused; a board
  renderer would help visualize both human play and agent behaviour.

### Design improvements

- **Evaluation harness.** Track performance against a random player and a Minimax
  player to measure real learning, not just self-play reward.
- **Reward shaping review.** The `-10` illegal-move penalty dominates early
  training; combining a legal-action mask with a smaller penalty (or none) is
  usually more stable.
- **Reproducibility & config.** Add seeding and a central config/hyperparameters
  file (learning rate, gamma, epsilon schedule, episodes).
- **Symmetry exploitation.** The board has 8-fold symmetry; augmenting or
  canonicalizing states can speed up learning significantly.
- **Testing.** Add unit tests for win/draw detection and move validation,
  especially the stacking ("cover") rules, which are the trickiest part.
```