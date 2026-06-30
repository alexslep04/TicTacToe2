# TicTacToe2 — CLI Command Reference

## Installation

```bash
# Install all dependencies (includes GPU-enabled PyTorch for CUDA 12.8)
pip install -r requirements.txt
```

> **Note:** The `requirements.txt` targets Python 3.14 + RTX 20xx/30xx/40xx (driver ≥ 520).
> If CUDA is unavailable the agent automatically falls back to CPU.

---

## Playing the Game

### Text-based (human vs human)
```bash
python main.py
```
Starts a turn-by-turn CLI game. Each turn you are prompted for a piece size
(1–3), a row (0–2), and a column (0–2).

---

### Graphical UI (human vs human)
```bash
python -m game.game_ui
```
Opens a pygame window. Click a piece size in the panel, then click a cell on
the board to place it. Valid-move cells are highlighted in green.

| Key | Action |
|-----|--------|
| Click piece panel | Select a piece size |
| Click board cell  | Place selected piece |
| `R` | Restart the current game |
| `ESC` | Quit |

---

### Play against a trained model
```bash
python -m ai.run play models/model.pt
```
Text-based game against a DQN agent. You choose which player (1 or 2) you
want to be; the model plays the other side with no exploration (ε = 0).

```bash
# Play against a specific numbered run
python -m ai.run play models/model_1.pt
```

---

## Training

```bash
# Train with defaults (10 000 episodes, output to models/)
python -m ai.run train

# Custom episode count
python -m ai.run train --episodes 20000

# Custom output directory (useful for experiments)
python -m ai.run train --out runs/experiment1

# Custom episode count + output directory + seed
python -m ai.run train --episodes 50000 --out runs/long_run --seed 123
```

**What gets saved** (all in the `--out` directory):

| File | Contents |
|------|----------|
| `model.pt` | Final trained network weights |
| `metrics.json` | Per-episode win / loss / draw / reward / ε / loss |
| `training_curves.png` | Four-panel training chart |

If files already exist from a previous run they are **never overwritten** —
the next run is automatically suffixed: `model_1.pt`, `model_2.pt`, etc.

**Training flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--episodes N` | `10000` | Number of self-play episodes |
| `--out DIR` | `models` | Directory to write outputs |
| `--seed N` | `42` | Random seed for reproducibility |

---

## Evaluation

### Evaluate a saved model against baselines
```bash
python -m ai.run eval models/model.pt

# More games for a tighter estimate
python -m ai.run eval models/model.pt --games 200
```
Runs the model (ε = 0) against a **random agent** (100 games) and a
**depth-4 Minimax agent** (up to 20 games). Prints win / loss / draw counts
and rates for each.

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--games N` | `100` | Games to play against the random baseline |

---

## Model vs Model

```bash
python -m ai.run versus models/model.pt models/model_1.pt

# More games
python -m ai.run versus models/model.pt models/model_1.pt --games 200
```
Pits two trained `.pt` files against each other. Each model plays first in
exactly half of the games. Prints wins, losses, and draws for each side.

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--games N` | `100` | Total games to play |

---

## Subcommand Summary

```
python -m ai.run <subcommand> [flags]
```

| Subcommand | Description |
|------------|-------------|
| `train`   | Train a new DQN agent via self-play and save the final model |
| `eval`    | Evaluate a saved model against random and minimax baselines |
| `versus`  | Pit two saved models against each other |
| `play`    | Play a terminal game against a saved model |
