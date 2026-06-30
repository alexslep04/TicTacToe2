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
- [x] **Reward values updated.** Win = **+2**, Draw = **−0.5**, Loss = **−2**.

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
