"""
Utility functions for the TicTacToe2 RL project.
Includes seeding, model save/load, metrics tracking, and plotting.
"""

import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import matplotlib.pyplot as plt


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility across all libraries."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def save_model(model: torch.nn.Module, path: str, metadata: Optional[dict] = None) -> None:
    """
    Save a PyTorch model checkpoint with optional metadata.
    
    Args:
        model: The PyTorch model to save.
        path: File path for the checkpoint.
        metadata: Optional dict of training metadata (episode, epsilon, etc.).
    """
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "metadata": metadata or {},
    }
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    torch.save(checkpoint, path)


def load_model(model: torch.nn.Module, path: str) -> dict:
    """
    Load a PyTorch model checkpoint.
    
    Args:
        model: The PyTorch model to load weights into.
        path: File path of the checkpoint.
        
    Returns:
        Metadata dict from the checkpoint.
    """
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    return checkpoint.get("metadata", {})


@dataclass
class MetricsTracker:
    """Track training metrics over episodes."""

    wins:           list = field(default_factory=list)
    losses:         list = field(default_factory=list)
    draws:          list = field(default_factory=list)
    rewards:        list = field(default_factory=list)
    episode_lengths: list = field(default_factory=list)
    epsilons:       list = field(default_factory=list)
    losses_train:   list = field(default_factory=list)  # MSE loss values
    loss_episodes:  list = field(default_factory=list)  # episode number for each loss value

    def record_episode(
        self,
        result: str,
        total_reward: float,
        episode_length: int,
        epsilon: float,
        train_loss: Optional[float] = None,
        episode_num: Optional[int] = None,
    ) -> None:
        """
        Record metrics for a completed episode.

        Args:
            result:         One of 'win', 'loss', 'draw'.
            total_reward:   Cumulative reward for the episode.
            episode_length: Number of steps taken.
            epsilon:        Current exploration rate.
            train_loss:     MSE loss from the last gradient step (None if buffer
                            not yet full).
            episode_num:    1-based episode number used to align the loss on the
                            chart x-axis.  Defaults to len(wins)+1 if omitted.
        """
        self.wins.append(1 if result == "win" else 0)
        self.losses.append(1 if result == "loss" else 0)
        self.draws.append(1 if result == "draw" else 0)
        self.rewards.append(total_reward)
        self.episode_lengths.append(episode_length)
        self.epsilons.append(epsilon)
        if train_loss is not None:
            self.losses_train.append(train_loss)
            ep = episode_num if episode_num is not None else len(self.wins)
            self.loss_episodes.append(ep)

    def get_recent_stats(self, window: int = 100) -> dict:
        """Return win/loss/draw/reward averages over the last `window` episodes."""
        if not self.wins:
            return {"win_rate": 0, "loss_rate": 0, "draw_rate": 0, "avg_reward": 0}
        n = min(window, len(self.wins))
        return {
            "win_rate":  sum(self.wins[-n:])    / n,
            "loss_rate": sum(self.losses[-n:])  / n,
            "draw_rate": sum(self.draws[-n:])   / n,
            "avg_reward": sum(self.rewards[-n:]) / n,
        }

    def save(self, path: str) -> None:
        """Save metrics to a JSON file."""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump({
                "wins":           self.wins,
                "losses":         self.losses,
                "draws":          self.draws,
                "rewards":        self.rewards,
                "episode_lengths": self.episode_lengths,
                "epsilons":       self.epsilons,
                "losses_train":   self.losses_train,
                "loss_episodes":  self.loss_episodes,
            }, f)

    def load(self, path: str) -> None:
        """Load metrics from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        self.wins            = data.get("wins", [])
        self.losses          = data.get("losses", [])
        self.draws           = data.get("draws", [])
        self.rewards         = data.get("rewards", [])
        self.episode_lengths = data.get("episode_lengths", [])
        self.epsilons        = data.get("epsilons", [])
        self.losses_train    = data.get("losses_train", [])
        self.loss_episodes   = data.get("loss_episodes", [])


def plot_training_curves(metrics: MetricsTracker, save_path: str, window: int = 100) -> None:
    """
    Plot training curves and save to disk. Does NOT open an interactive window.

    Four panels:
      - Win / Loss / Draw rates (rolling average)
      - Episode reward          (rolling average)
      - Exploration rate ε      (raw)
      - Network training loss   (rolling average)

    Args:
        metrics:   MetricsTracker with recorded episode data.
        save_path: File path for the saved PNG (e.g. "models/training_curves.png").
        window:    Rolling-average window size (default 100 episodes).
    """
    n = len(metrics.wins)
    episodes = list(range(1, n + 1))

    def smooth(data: list) -> tuple:
        """Return (x_range, smoothed_values) using a rolling mean."""
        if len(data) >= window:
            arr = np.convolve(data, np.ones(window) / window, mode="valid")
            return list(range(window, len(data) + 1)), arr
        return episodes[:len(data)], np.array(data, dtype=float)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("TicTacToe2 — Training Metrics", fontsize=14, fontweight="bold")

    # ── Win / Loss / Draw rates ───────────────────────────────────────────────
    ax = axes[0, 0]
    wx, wy = smooth(metrics.wins)
    lx, ly = smooth(metrics.losses)
    dx, dy = smooth(metrics.draws)
    ax.plot(wx, wy, color="#2ecc71", label="Win")
    ax.plot(lx, ly, color="#e74c3c", label="Loss")
    ax.plot(dx, dy, color="#3498db", label="Draw")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Rate")
    ax.set_title(f"Win / Loss / Draw Rate  (rolling {window})")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ── Episode reward ────────────────────────────────────────────────────────
    ax = axes[0, 1]
    rx, ry = smooth(metrics.rewards)
    ax.plot(rx, ry, color="#9b59b6")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Total Reward")
    ax.set_title(f"Episode Reward  (rolling {window})")
    ax.grid(True, alpha=0.3)

    # ── Epsilon decay ─────────────────────────────────────────────────────────
    ax = axes[1, 0]
    ax.plot(episodes, metrics.epsilons, color="#e67e22")
    ax.set_xlabel("Episode")
    ax.set_ylabel("ε  (exploration rate)")
    ax.set_title("Epsilon Decay")
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    # ── Network training loss ─────────────────────────────────────────────────
    # loss_episodes gives the actual episode number for each recorded loss so
    # the x-axis always aligns with the episode axis of the other panels —
    # even though training only starts after the replay buffer fills up.
    ax = axes[1, 1]
    if metrics.losses_train and metrics.loss_episodes:
        loss_x = np.array(metrics.loss_episodes, dtype=float)
        loss_y = np.array(metrics.losses_train,  dtype=float)
        if len(loss_y) >= window:
            # Rolling mean over values; align x to the last episode in each window
            smoothed_y = np.convolve(loss_y, np.ones(window) / window, mode="valid")
            smoothed_x = loss_x[window - 1:]
            ax.plot(smoothed_x, smoothed_y, color="#795548")
        else:
            ax.plot(loss_x, loss_y, color="#795548", alpha=0.6)
        ax.set_xlabel("Episode")
        ax.set_ylabel("MSE Loss")
        ax.set_title(f"Network Training Loss  (rolling {window})")
        ax.set_xlim(left=1, right=max(n, loss_x[-1]) if len(loss_x) else n)
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Buffer not yet full — no loss recorded",
                ha="center", va="center", transform=ax.transAxes, color="gray",
                fontsize=10)
        ax.set_title("Network Training Loss")
        ax.set_xlabel("Episode")
        ax.set_ylabel("MSE Loss")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close(fig)  # Never open an interactive window


@dataclass
class Config:
    """Central configuration for training hyperparameters."""

    # Training
    num_episodes: int = 100000
    batch_size: int = 128
    learning_rate: float = 1e-3
    gamma: float = 0.99         # Discount factor

    # Exploration — decays from 1.0 → 0.2 over 100 000 episodes (80/20 split)
    # decay = 0.2^(1/100000) ≈ 0.999984
    epsilon_start: float = 1.0
    epsilon_end: float = 0.2
    epsilon_decay: float = 0.999984

    # Replay buffer
    buffer_size: int = 100000
    min_buffer_size: int = 10000  # Minimum samples before training starts

    # Network
    hidden_size: int = 128

    # Output — final model + chart are written here; no intermediate checkpoints
    models_dir: str = "models"

    # Seeding
    seed: int = 42

    def save(self, path: str) -> None:
        """Save config to JSON file."""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.__dict__, f, indent=2)

    @classmethod
    def load(cls, path: str) -> "Config":
        """Load config from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls(**data)
