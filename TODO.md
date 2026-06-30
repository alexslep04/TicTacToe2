# TODO / Backlog

Known bugs, resolved issues, and remaining work for TicTacToe2.

## Resolved

- [x] **`get_state()` `.flatten()` crash.** `get_state()` called `.flatten()` on
  `board_owners` / `board_pieces`, which are plain Python lists in
  `game_logic.py`, not NumPy arrays. Fixed by wrapping them in `np.array(...)`
  before flattening.
- [x] **Action masking added.** Fixed 27-action space (`3 sizes × 3 rows × 3 cols`)
  with `legal_action_mask()`. Agents only ever select from legal actions, so
  illegal moves — including reusing an exhausted piece — are structurally
  impossible.
- [x] **Illegal-action penalty removed.** The old `-10` reward was dead code once
  masking was in place. `step()` now asserts move legality and raises immediately
  if an illegal action is attempted, surfacing any masking bugs.
- [x] **Loss reward added.** When the opponent wins, `run.py` retroactively assigns
  **−2** to the agent's last transition so the network learns which of its own
  moves enabled the loss.
- [x] **Draw handled before action selection.** If the current player has no legal
  moves, `run_episode()` ends the game as a draw before calling `select_action()`,
  preventing `np.random.choice([])` crashes.
- [x] **Agent (`agent.py`) implemented.** `DQNAgent` (two-layer MLP, experience
  replay, ε-greedy, target network), `RandomAgent`, and `MinimaxAgent`
  (alpha-beta pruning) are all implemented.
- [x] **Training loop (`run.py`) implemented.** Self-play rollouts, 4 gradient
  updates per episode, target-network sync every 50 episodes, ε decay, and a
  final evaluation against random and Minimax baselines.
- [x] **No mid-training eval-vs-random.** Periodic evaluation against an external
  opponent was removed — it consumed wall-clock time without improving the
  gradient signal. Final benchmarks still run after training completes.
- [x] **No intermediate checkpoints.** Only the final model is saved, keeping the
  output directory clean. Files written: `model.pt`, `metrics.json`,
  `training_curves.png`.
- [x] **Model-vs-model mode.** `python -m ai.run versus <model_a> <model_b>`
  pits two saved `.pt` files against each other.
- [x] **Training chart auto-saved.** `plot_training_curves()` saves a four-panel
  PNG to disk and never opens an interactive window.
- [x] **Utilities (`utils.py`) implemented.** `Config`, `MetricsTracker`,
  `save_model`, `load_model`, `set_seed`, `plot_training_curves`.
- [x] **Graphical UI (`game_ui.py`) implemented.** Pygame board renderer with
  piece-size panels, click-to-place, valid-move highlighting, and win/draw overlay.
- [x] **Reward values updated.** Win = **+3**, Draw = **−1** (same as loss),
  Loss = **−1**.  Draw carries the same penalty as losing so the agent is always
  incentivised to play for a win.
- [x] **State encoding normalised (self-play symmetry fix).** `get_state()`
  previously encoded `board_owners` with absolute player IDs (1 or 2).  Player 1
  and player 2 saw identical board positions encoded differently, preventing the
  Q-network from generalising across both roles.  Fixed to current-player
  perspective: `1 = my piece`, `2 = opponent's piece`, `0 = empty`.
- [x] **Self-play transitions doubled.** `run_episode()` previously only stored
  buffer transitions for the "agent" side, discarding every opponent-side move and
  halving the learning signal per episode.  Both sides now track their last
  `(state, action)` and store transitions; terminal rewards (WIN / LOSS / DRAW)
  are assigned correctly to both the mover and the loser.
- [x] **CLI `--episodes` default fixed.** The argument parser had `default=10000`
  which silently overrode `Config.num_episodes = 100 000`.  Changed to
  `default=None` so `python -m ai.run train` runs the full 100 000 episodes.
- [x] **Negamax Bellman update (critical self-play bug).** With the normalised state
  encoding, after any move the next state is from the *opponent's* perspective.
  The original update `Q(s,a) = r + γ·max Q(s′,a′)` treated the opponent's
  best value as a *benefit*, training the agent to actively help the opponent.
  This caused >74 % losses against a purely random player after 100 k episodes.
  Fixed to the correct zero-sum adversarial (negamax) update:
  `Q(s,a) = r − γ·max Q(s′,a′)`.
  **All models trained before commit `1d04814` must be discarded and retrained.**

## Open — remaining work

- [ ] **Unit tests.** Win/draw detection and the stacking ("cover") rules are the
  trickiest logic and should have automated tests. Piece exhaustion edge cases
  are also worth covering.
- [ ] **Symmetry exploitation.** The board has 8-fold symmetry; augmenting or
  canonicalising states before storing transitions could significantly speed up
  learning.
- [ ] **Hyperparameter tuning.** The defaults in `Config` (lr, γ, ε schedule,
  hidden size, buffer size) are reasonable but have not been systematically
  optimised.
