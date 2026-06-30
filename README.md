# TicTacToe2

A variant of Tic Tac Toe with **stackable, sized pieces** ("Gobblet"-style), plus
a Reinforcement Learning (RL) agent that learns to play it via self-play.

## The Game

Unlike classic Tic Tac Toe, each player has a limited set of pieces of three
different sizes. A larger piece can be placed on top of (cover) a smaller piece —
including the opponent's — which makes the strategy considerably deeper than the
standard game.

- Each player starts with pieces `[1, 1, 2, 2, 3, 3]` (two each of sizes 1, 2, 3).
- A move consists of choosing a `piece_size` and a board cell `(x, y)`.
- A move is valid only if the chosen piece is **bigger** than the piece currently
  in that cell (and the player still has that piece available).
- Win by getting three cells you **own** in a row, column, or diagonal.
- A draw occurs when the current player has no valid moves remaining.

State is tracked with two 3×3 grids:
- `board_pieces` — the size of the piece occupying each cell.
- `board_owners` — which player (1 or 2) owns the top piece in each cell.

## Project Structure

```
TicTacToe2/
├── main.py                 # CLI entry point — human vs human (text)
├── requirements.txt        # pygame-ce, numpy, torch, matplotlib
├── game/
│   ├── game_logic.py       # TicTacToe2 — core rules, board state, move validation
│   └── game_ui.py          # Pygame graphical UI (human vs human)
└── ai/
    ├── environment.py      # TicTacToeEnv — Gym-style RL wrapper
    ├── agent.py            # DQNAgent, RandomAgent, MinimaxAgent
    ├── run.py              # train / eval / versus CLI
    └── utils.py            # Config, MetricsTracker, save/load, plotting
```

## Installation

```bash
pip install -r requirements.txt
```

## Running

### Text-based human vs human
```bash
python main.py
```

### Graphical UI (human vs human)
```bash
python -m game.game_ui
```

### Train a DQN agent
```bash
# Default: 10 000 self-play episodes, output written to models/
python -m ai.run train

# Custom episode count and output directory
python -m ai.run train --episodes 20000 --out runs/experiment1
```

After training, three files are written to the output directory:

| File | Contents |
|---|---|
| `model.pt` | Final trained network weights |
| `metrics.json` | Per-episode win / loss / draw / reward / ε / loss data |
| `training_curves.png` | Four-panel chart of all training metrics |

### Evaluate a saved model
```bash
python -m ai.run eval models/model.pt
python -m ai.run eval models/model.pt --games 200
```

Runs the model (ε = 0, no exploration) against a random baseline and a
depth-4 Minimax player.

### Pit two trained models against each other
```bash
python -m ai.run versus models/model.pt runs/experiment1/model.pt
python -m ai.run versus models/model.pt runs/experiment1/model.pt --games 200
```

## Current Status

| Component | Status |
|---|---|
| Core game rules (`game_logic.py`) | ✅ Implemented |
| CLI play (`main.py`) | ✅ Implemented |
| Graphical UI (`game_ui.py`) | ✅ Implemented |
| RL environment (`environment.py`) | ✅ Implemented |
| DQN agent (`agent.py`) | ✅ Implemented |
| Random baseline (`agent.py`) | ✅ Implemented |
| Minimax baseline (`agent.py`) | ✅ Implemented |
| Training loop — self-play (`run.py`) | ✅ Implemented |
| Model-vs-model evaluation (`run.py`) | ✅ Implemented |
| Utilities — config / metrics / chart (`utils.py`) | ✅ Implemented |

## Reinforcement Learning Design

### Environment (`ai/environment.py`)

`TicTacToeEnv` subclasses `TicTacToe2` and exposes a Gym-style interface:

- **`reset()`** — clears the board and returns the initial 30-element state vector.
- **`step(action)`** — applies a flat action index (0–26) and returns
  `(state, reward, done, info)`.
- **`legal_action_mask()`** — boolean array of shape `(27,)` marking every
  currently legal action. Agents always select from this mask, so illegal moves
  are structurally impossible.
- **`get_state()`** — 30-element feature vector:
  9 cell-owner values + 9 cell-piece sizes + 6 current-player piece counts
  (zero-padded) + 6 opponent piece counts (zero-padded).

Action space: `piece_size ∈ {1,2,3}  ×  row ∈ {0,1,2}  ×  col ∈ {0,1,2}` → 27 discrete actions.

### Reward Structure

| Outcome | Reward |
|---|---|
| Win | **+2** |
| Loss | **−2** (assigned retroactively to the agent's last move) |
| Draw | **−0.5** (penalises both sides — winning is always preferred) |
| Ongoing move | **0** |

The −2 loss signal is applied in `run.py` to the **agent's previous transition**,
not the opponent's winning move, so the network correctly associates its own
choices with the eventual loss.

### Self-Play Training

The agent plays **against itself** — both sides share the same network and the
same ε-greedy policy, alternating who moves first each episode. After each episode:

- 4 gradient updates are applied (mini-batch size 64).
- The target network is synced every 50 episodes.
- ε decays multiplicatively from 1.0 → 0.05.

Evaluation against an external opponent is **not** run during training — it
adds wall-clock time without improving the gradient signal. The self-play
win/loss/draw rates printed every 100 episodes are sufficient to monitor
progress. A final objective benchmark against random and Minimax opponents
runs once training is complete.

### Agents (`ai/agent.py`)

| Class | Description |
|---|---|
| `DQNAgent` | Two-layer MLP, experience replay, ε-greedy, target network |
| `RandomAgent` | Picks uniformly at random from legal actions |
| `MinimaxAgent` | Alpha-beta pruning search (configurable depth, default 6) |

### Utilities (`ai/utils.py`)

- `Config` — dataclass of all hyperparameters; serialisable to JSON.
- `MetricsTracker` — records per-episode win/loss/draw/reward/ε/loss; saves to JSON.
- `plot_training_curves()` — saves a four-panel PNG to disk; never opens an
  interactive window.
- `set_seed()` / `save_model()` / `load_model()` — reproducibility and persistence helpers.

## Remaining Work

- **Unit tests** — win/draw detection and the stacking ("cover") rules are the
  trickiest logic and would benefit from automated tests.
- **Symmetry exploitation** — the board has 8-fold symmetry; augmenting or
  canonicalising states could accelerate learning significantly.
- **Hyperparameter tuning** — the defaults in `Config` are reasonable starting
  points but have not been systematically optimised.