"""
Training and evaluation loop for TicTacToe2 RL agents.

Why no periodic eval-vs-random during training?
------------------------------------------------
Periodically pausing training to run 50 evaluation games against a random
opponent adds wall-clock time without giving the *training* loop any new
gradient signal.  The self-play win/loss/draw rates printed every 100
episodes already show whether the agent is improving.  A final evaluation
against the random and minimax baselines is run once training is fully
complete, so you still get an objective benchmark — just without interrupting
the learning process every 100 steps.
"""

import argparse
import os
from typing import Optional

import numpy as np

from ai.environment import TicTacToeEnv
from ai.agent import DQNAgent, RandomAgent, MinimaxAgent, BaseAgent
from ai.utils import (
    set_seed,
    save_model,
    load_model,
    MetricsTracker,
    plot_training_curves,
    Config,
)

# Reward constants — must match ai/environment.py
WIN_REWARD  =  3.0
LOSS_REWARD = -1.0
DRAW_REWARD = -1.0


# ── File-naming helpers ────────────────────────────────────────────────────────

def _next_run_prefix(directory: str) -> str:
    """
    Return the suffix that makes the next set of output files unique.

    First run  → ""       → model.pt / metrics.json / training_curves.png
    Second run → "_1"     → model_1.pt / metrics_1.json / training_curves_1.png
    Third run  → "_2"     → model_2.pt / …
    """
    if not os.path.exists(os.path.join(directory, "model.pt")):
        return ""
    i = 1
    while os.path.exists(os.path.join(directory, f"model_{i}.pt")):
        i += 1
    return f"_{i}"


# ── Episode runner ─────────────────────────────────────────────────────────────

def run_episode(
    env: TicTacToeEnv,
    agent: BaseAgent,
    opponent: BaseAgent,
    train: bool = True,
    agent_starts: bool = True,
) -> tuple[str, float, int]:
    """
    Run a single episode.

    Returns:
        (result, total_reward, episode_length) from the agent's perspective.
    """
    state = env.reset()
    legal_mask = env.legal_action_mask()

    total_reward    = 0.0
    episode_length  = 0
    current_is_agent = agent_starts

    # Remember agent's last (state, action) to assign a delayed loss reward
    # when the opponent wins on the very next turn.
    agent_last_state  = None
    agent_last_action = None

    while True:
        episode_length += 1

        # ── Draw: no legal actions ───────────────────────────────────────────
        if not legal_mask.any():
            if train and agent_last_state is not None and isinstance(agent, DQNAgent):
                agent.store_transition(
                    agent_last_state, agent_last_action,
                    DRAW_REWARD, state, True, legal_mask,
                )
                total_reward += DRAW_REWARD
            return "draw", total_reward, episode_length

        # ── Select action ────────────────────────────────────────────────────
        if current_is_agent:
            action = agent.select_action(state, legal_mask)
            agent_last_state  = state
            agent_last_action = action
        else:
            action = opponent.select_action(state, legal_mask)

        next_state, reward, done, info = env.step(action)
        next_legal_mask = info.get("legal_action_mask", env.legal_action_mask())

        # ── Terminal transitions ─────────────────────────────────────────────
        if done:
            if reward > 0:          # current player won
                if current_is_agent:
                    if train and isinstance(agent, DQNAgent):
                        agent.store_transition(
                            state, action,
                            WIN_REWARD, next_state, True, next_legal_mask,
                        )
                        total_reward += WIN_REWARD
                    return "win", total_reward, episode_length
                else:               # opponent won → agent lost
                    if train and agent_last_state is not None and isinstance(agent, DQNAgent):
                        agent.store_transition(
                            agent_last_state, agent_last_action,
                            LOSS_REWARD, next_state, True, next_legal_mask,
                        )
                        total_reward += LOSS_REWARD
                    return "loss", total_reward, episode_length
            else:                   # draw via environment
                if train and isinstance(agent, DQNAgent):
                    if current_is_agent:
                        agent.store_transition(
                            state, action,
                            DRAW_REWARD, next_state, True, next_legal_mask,
                        )
                    elif agent_last_state is not None:
                        agent.store_transition(
                            agent_last_state, agent_last_action,
                            DRAW_REWARD, next_state, True, next_legal_mask,
                        )
                    total_reward += DRAW_REWARD
                return "draw", total_reward, episode_length

        # ── Non-terminal agent move: 0 immediate reward ──────────────────────
        if train and current_is_agent and isinstance(agent, DQNAgent):
            agent.store_transition(state, action, 0.0, next_state, False, next_legal_mask)

        state = next_state
        legal_mask = next_legal_mask
        current_is_agent = not current_is_agent


# ── Training ───────────────────────────────────────────────────────────────────

def train_agent(config: Config) -> DQNAgent:
    """
    Train a DQN agent via self-play and save the final model.

    If outputs already exist in models_dir the new files are numbered
    (model_1.pt, model_2.pt, …) so previous runs are never overwritten.
    """
    set_seed(config.seed)

    env   = TicTacToeEnv()
    agent = DQNAgent(
        hidden_size   = config.hidden_size,
        learning_rate = config.learning_rate,
        gamma         = config.gamma,
        buffer_size   = config.buffer_size,
        batch_size    = config.batch_size,
        epsilon_start = config.epsilon_start,
        epsilon_end   = config.epsilon_end,
        epsilon_decay = config.epsilon_decay,
    )

    metrics = MetricsTracker()
    os.makedirs(config.models_dir, exist_ok=True)

    # Determine unique filenames for this run
    prefix       = _next_run_prefix(config.models_dir)
    model_path   = os.path.join(config.models_dir, f"model{prefix}.pt")
    metrics_path = os.path.join(config.models_dir, f"metrics{prefix}.json")
    chart_path   = os.path.join(config.models_dir, f"training_curves{prefix}.png")

    print(f"Training for {config.num_episodes} episodes  |  device: {agent.device}")
    print(f"Outputs → {model_path}  |  {chart_path}")
    print("(self-play — agent vs itself, alternating who goes first)\n")

    for episode in range(config.num_episodes):
        agent_starts = episode % 2 == 0

        result, total_reward, ep_length = run_episode(
            env, agent, agent, train=True, agent_starts=agent_starts
        )

        # Multiple gradient updates per episode
        train_loss = None
        if len(agent.replay_buffer) >= config.min_buffer_size:
            for _ in range(4):
                loss = agent.train_step()
                if loss is not None:
                    train_loss = loss

        # Sync target network periodically (every 0.5% of episodes)
        if episode % 500 == 0:
            agent.update_target_network()

        agent.decay_epsilon()

        metrics.record_episode(
            result, total_reward, ep_length,
            agent.epsilon, train_loss, episode + 1,
        )

        if (episode + 1) % 1000 == 0:
            stats = metrics.get_recent_stats(1000)
            print(
                f"Episode {episode + 1:>6}/{config.num_episodes} | "
                f"Win {stats['win_rate']:>5.1%}  "
                f"Loss {stats['loss_rate']:>5.1%}  "
                f"Draw {stats['draw_rate']:>5.1%}  "
                f"ε={agent.epsilon:.4f}"
            )

    # Save final model
    save_model(
        agent.get_policy_net(),
        model_path,
        {"episodes": config.num_episodes, "epsilon": agent.epsilon},
    )
    metrics.save(metrics_path)
    print(f"\nSaved model  → {model_path}")

    # Save training chart
    plot_training_curves(metrics, save_path=chart_path)
    print(f"Saved chart  → {chart_path}")

    return agent


# ── Evaluation helpers ─────────────────────────────────────────────────────────

def evaluate_agent(
    agent: BaseAgent,
    opponent: BaseAgent,
    num_games: int = 100,
) -> dict:
    """Evaluate agent against opponent (ε=0, no training)."""
    env     = TicTacToeEnv()
    results = {"win": 0, "loss": 0, "draw": 0}

    original_epsilon = None
    if isinstance(agent, DQNAgent):
        original_epsilon = agent.epsilon
        agent.epsilon = 0.0

    for i in range(num_games):
        result, _, _ = run_episode(
            env, agent, opponent, train=False, agent_starts=(i % 2 == 0)
        )
        results[result] += 1

    if original_epsilon is not None:
        agent.epsilon = original_epsilon

    return {
        "wins":      results["win"],
        "losses":    results["loss"],
        "draws":     results["draw"],
        "win_rate":  results["win"]  / num_games,
        "loss_rate": results["loss"] / num_games,
        "draw_rate": results["draw"] / num_games,
    }


def evaluate_against_all(agent: BaseAgent, num_games: int = 100) -> None:
    """Benchmark agent against random and minimax opponents."""
    print("\n=== Final Evaluation ===")

    r = evaluate_agent(agent, RandomAgent(), num_games)
    print(f"vs Random  ({num_games} games): "
          f"W {r['wins']} ({r['win_rate']:.1%})  "
          f"L {r['losses']} ({r['loss_rate']:.1%})  "
          f"D {r['draws']} ({r['draw_rate']:.1%})")

    mm_games = min(num_games, 20)
    m = evaluate_agent(agent, MinimaxAgent(max_depth=4), mm_games)
    print(f"vs Minimax ({mm_games} games): "
          f"W {m['wins']} ({m['win_rate']:.1%})  "
          f"L {m['losses']} ({m['loss_rate']:.1%})  "
          f"D {m['draws']} ({m['draw_rate']:.1%})")


# ── Model-vs-model ─────────────────────────────────────────────────────────────

def versus(model_a_path: str, model_b_path: str, num_games: int = 100) -> None:
    """Pit two trained models against each other."""
    for path in (model_a_path, model_b_path):
        if not os.path.exists(path):
            print(f"Error: model file not found: {path}")
            print("Tip: models are saved as  models/model.pt  (or model_1.pt, model_2.pt…)")
            return

    agent_a = DQNAgent()
    agent_b = DQNAgent()
    load_model(agent_a.get_policy_net(), model_a_path)
    load_model(agent_b.get_policy_net(), model_b_path)
    agent_a.epsilon = 0.0
    agent_b.epsilon = 0.0

    label_a = os.path.splitext(os.path.basename(model_a_path))[0]
    label_b = os.path.splitext(os.path.basename(model_b_path))[0]

    print(f"\n=== {label_a}  vs  {label_b}  ({num_games} games) ===")

    env    = TicTacToeEnv()
    wins_a = 0
    wins_b = 0
    draws  = 0

    for i in range(num_games):
        result, _, _ = run_episode(
            env, agent_a, agent_b, train=False, agent_starts=(i % 2 == 0)
        )
        if result == "win":
            wins_a += 1
        elif result == "loss":
            wins_b += 1
        else:
            draws += 1

    print(f"  {label_a}: {wins_a} wins  ({wins_a/num_games:.1%})")
    print(f"  {label_b}: {wins_b} wins  ({wins_b/num_games:.1%})")
    print(f"  Draws:    {draws}          ({draws/num_games:.1%})")


# ── Human vs AI ───────────────────────────────────────────────────────────────

def play_human_vs_ai(model_path: str) -> None:
    """
    Play a text-based game against a trained DQN model.

    Usage:
        python -m ai.run play models/model.pt
    """
    if not os.path.exists(model_path):
        print(f"Error: model file not found: {model_path}")
        print("Tip: train a model first with  python -m ai.run train")
        return

    agent = DQNAgent()
    load_model(agent.get_policy_net(), model_path)
    agent.epsilon = 0.0
    print(f"\nLoaded model: {model_path}")

    while True:
        choice = input("Play as player 1 or 2? (1/2): ").strip()
        if choice in ("1", "2"):
            human_player = int(choice)
            break
        print("Please enter 1 or 2.")

    ai_player = 3 - human_player
    print(f"\nYou = Player {human_player}   AI = Player {ai_player}")
    print("Pieces per player: [1, 1, 2, 2, 3, 3]  (larger covers smaller)\n")

    env = TicTacToeEnv()

    while True:  # outer loop: play again
        state      = env.reset()
        legal_mask = env.legal_action_mask()

        while True:  # inner loop: one game
            env.print_board()
            print(f"\nPlayer {env.current_player}'s turn")
            print(f"  Your pieces : {sorted(env.player_pieces[human_player], reverse=True)}")
            print(f"  AI pieces   : {sorted(env.player_pieces[ai_player], reverse=True)}")

            if not legal_mask.any():
                print("\nNo legal moves available — it's a draw!")
                break

            if env.current_player == human_player:
                # ── Human move ───────────────────────────────────────────────
                while True:
                    try:
                        piece_size = int(input("\n  Piece size (1-3): "))
                        row        = int(input("  Row        (0-2): "))
                        col        = int(input("  Col        (0-2): "))
                        action = env.move_to_action(piece_size, row, col)
                        if legal_mask[action]:
                            break
                        print("  ✗ Illegal move — try again.")
                    except (ValueError, IndexError):
                        print("  ✗ Invalid input — try again.")
            else:
                # ── AI move ──────────────────────────────────────────────────
                action = agent.select_action(state, legal_mask)
                piece_size, row, col = env.action_to_move(action)
                print(f"\n  AI plays: piece={piece_size}  row={row}  col={col}")

            next_state, reward, done, info = env.step(action)
            legal_mask = info.get("legal_action_mask", env.legal_action_mask())
            state = next_state

            if done:
                env.print_board()
                if reward > 0:
                    if env.current_player == human_player:
                        print("\n🎉 You win!")
                    else:
                        print("\nAI wins!")
                else:
                    print("\nIt's a draw!")
                break

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TicTacToe2 RL — train / eval / versus / play")
    sub = parser.add_subparsers(dest="mode", required=True)

    # train
    p = sub.add_parser("train", help="Train a DQN agent via self-play")
    p.add_argument("--episodes", type=int, default=10000)
    p.add_argument("--seed",     type=int, default=42)
    p.add_argument("--out",      type=str, default="models",
                   help="Output directory (default: models/)")

    # eval
    p = sub.add_parser("eval", help="Evaluate a saved model vs random + minimax")
    p.add_argument("model", help="Path to .pt file")
    p.add_argument("--games", type=int, default=100)

    # versus
    p = sub.add_parser("versus", help="Pit two trained models against each other")
    p.add_argument("model_a", help="Path to first .pt file  (e.g. models/model.pt)")
    p.add_argument("model_b", help="Path to second .pt file (e.g. models/model_1.pt)")
    p.add_argument("--games", type=int, default=100)

    # play
    p = sub.add_parser("play", help="Play against a trained model in the terminal")
    p.add_argument("model", help="Path to .pt file  (e.g. models/model.pt)")

    args = parser.parse_args()

    if args.mode == "train":
        config = Config(num_episodes=args.episodes, seed=args.seed, models_dir=args.out)
        agent  = train_agent(config)
        evaluate_against_all(agent, num_games=100)

    elif args.mode == "eval":
        if not os.path.exists(args.model):
            print(f"Error: file not found: {args.model}")
            return
        agent = DQNAgent()
        load_model(agent.get_policy_net(), args.model)
        agent.epsilon = 0.0
        evaluate_against_all(agent, num_games=args.games)

    elif args.mode == "versus":
        versus(args.model_a, args.model_b, num_games=args.games)

    elif args.mode == "play":
        play_human_vs_ai(args.model)


if __name__ == "__main__":
    main()
