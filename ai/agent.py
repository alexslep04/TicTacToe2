"""
RL agents for TicTacToe2.
Includes DQN agent, random baseline, and minimax baseline.
"""

import copy
import random
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from ai.environment import TicTacToeEnv, NUM_ACTIONS


# State size: 9 owners + 9 pieces + 6 player pieces + 6 opponent pieces = 30
STATE_SIZE = 30


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    @abstractmethod
    def select_action(self, state: list, legal_mask: np.ndarray) -> int:
        """Select an action given the current state and legal action mask."""
        pass
    
    def train_step(self, *args, **kwargs) -> Optional[float]:
        """Perform a training step. Returns loss if applicable."""
        return None


class RandomAgent(BaseAgent):
    """Agent that selects random legal actions."""
    
    def select_action(self, state: list, legal_mask: np.ndarray) -> int:
        """Select a random legal action. Caller must ensure legal actions exist."""
        legal_actions = np.where(legal_mask)[0]
        return int(np.random.choice(legal_actions))


class DQNetwork(nn.Module):
    """Deep Q-Network for action-value estimation."""
    
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_size),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class ReplayBuffer:
    """Experience replay buffer for DQN training."""
    
    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)
    
    def push(
        self,
        state: list,
        action: int,
        reward: float,
        next_state: list,
        done: bool,
        next_legal_mask: np.ndarray,
    ) -> None:
        """Store a transition in the buffer."""
        self.buffer.append((state, action, reward, next_state, done, next_legal_mask))
    
    def sample(self, batch_size: int) -> tuple:
        """Sample a batch of transitions."""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones, next_masks = zip(*batch)
        return (
            torch.FloatTensor(states),
            torch.LongTensor(actions),
            torch.FloatTensor(rewards),
            torch.FloatTensor(next_states),
            torch.BoolTensor(dones),
            torch.BoolTensor(np.array(next_masks)),
        )
    
    def __len__(self) -> int:
        return len(self.buffer)


class DQNAgent(BaseAgent):
    """Deep Q-Network agent with experience replay and epsilon-greedy exploration."""
    
    def __init__(
        self,
        state_size: int = STATE_SIZE,
        action_size: int = NUM_ACTIONS,
        hidden_size: int = 128,
        learning_rate: float = 1e-3,
        gamma: float = 0.99,
        buffer_size: int = 10000,
        batch_size: int = 64,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay: float = 0.9995,
        device: Optional[str] = None,
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.batch_size = batch_size
        
        # Epsilon-greedy exploration
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        
        # Device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Networks
        self.policy_net = DQNetwork(state_size, action_size, hidden_size).to(self.device)
        self.target_net = DQNetwork(state_size, action_size, hidden_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)
    
    def select_action(self, state: list, legal_mask: np.ndarray) -> int:
        """Select action using epsilon-greedy policy with legal action masking.
        
        Caller must ensure legal actions exist (game ends in draw if none).
        """
        legal_actions = np.where(legal_mask)[0]
        
        if random.random() < self.epsilon:
            # Explore: random legal action
            return int(np.random.choice(legal_actions))
        
        # Exploit: best legal action according to Q-values
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor).squeeze(0).cpu().numpy()
            
            # Mask illegal actions with -inf
            masked_q = np.full(self.action_size, -np.inf)
            masked_q[legal_actions] = q_values[legal_actions]
            
            return int(np.argmax(masked_q))
    
    def store_transition(
        self,
        state: list,
        action: int,
        reward: float,
        next_state: list,
        done: bool,
        next_legal_mask: np.ndarray,
    ) -> None:
        """Store a transition in the replay buffer."""
        self.replay_buffer.push(state, action, reward, next_state, done, next_legal_mask)
    
    def train_step(self) -> Optional[float]:
        """Perform one training step using a batch from the replay buffer."""
        if len(self.replay_buffer) < self.batch_size:
            return None
        
        # Sample batch
        states, actions, rewards, next_states, dones, next_masks = self.replay_buffer.sample(
            self.batch_size
        )
        states = states.to(self.device)
        actions = actions.to(self.device)
        rewards = rewards.to(self.device)
        next_states = next_states.to(self.device)
        dones = dones.to(self.device)
        next_masks = next_masks.to(self.device)
        
        # Current Q values
        current_q = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q values with legal action masking
        with torch.no_grad():
            next_q = self.target_net(next_states)
            # Mask illegal actions
            next_q[~next_masks] = -float("inf")
            max_next_q = next_q.max(dim=1)[0]
            # Handle terminal states — no future value after game ends
            max_next_q[dones] = 0.0
            # Negamax Bellman update: after any move the next state is encoded
            # from the OPPONENT's perspective (1=theirs, 2=ours).  Their high
            # Q-value means they are in a good position, which is BAD for us.
            # Negating converts the opponent's best value into our cost, giving
            # the correct zero-sum adversarial backup:
            #   Q(s,a) = r + γ · (−max_a′ Q(s′,a′))
            target_q = rewards - self.gamma * max_next_q
        
        # Loss and optimization
        loss = nn.functional.mse_loss(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for stability
        nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)
        self.optimizer.step()
        
        return loss.item()
    
    def update_target_network(self) -> None:
        """Copy weights from policy network to target network."""
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def decay_epsilon(self) -> None:
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
    
    def get_policy_net(self) -> nn.Module:
        """Return the policy network for saving."""
        return self.policy_net


class MinimaxAgent(BaseAgent):
    """
    Minimax agent with alpha-beta pruning.
    Uses the game's own logic to simulate moves.
    """
    
    def __init__(self, max_depth: int = 6):
        self.max_depth = max_depth
    
    def select_action(self, state: list, legal_mask: np.ndarray) -> int:
        """Select the best action using minimax with alpha-beta pruning.
        
        Caller must ensure legal actions exist (game ends in draw if none).
        """
        legal_actions = np.where(legal_mask)[0]
        
        # Create a fresh environment and restore state
        env = TicTacToeEnv()
        self._restore_state(env, state)
        
        best_action = None
        best_value = -float("inf")
        alpha = -float("inf")
        beta = float("inf")
        
        for action in legal_actions:
            # Create a copy of the environment for simulation
            env_copy = self._copy_env(env)
            _, reward, done, _ = env_copy.step(action)
            
            if done:
                value = reward  # Win = 1, Draw = -0.25
            else:
                # Opponent's turn (minimizing)
                value = self._minimax(env_copy, self.max_depth - 1, alpha, beta, False)
            
            if value > best_value:
                best_value = value
                best_action = action
            
            alpha = max(alpha, value)
        
        return best_action if best_action is not None else int(legal_actions[0])
    
    def _minimax(
        self,
        env: TicTacToeEnv,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        """Minimax with alpha-beta pruning."""
        legal_mask = env.legal_action_mask()
        legal_actions = np.where(legal_mask)[0]
        
        if len(legal_actions) == 0:
            return 0  # Draw
        
        if depth == 0:
            return 0  # Heuristic: neutral at depth limit
        
        if maximizing:
            value = -float("inf")
            for action in legal_actions:
                env_copy = self._copy_env(env)
                _, reward, done, _ = env_copy.step(action)
                
                if done:
                    child_value = reward
                else:
                    child_value = self._minimax(env_copy, depth - 1, alpha, beta, False)
                
                value = max(value, child_value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float("inf")
            for action in legal_actions:
                env_copy = self._copy_env(env)
                _, reward, done, _ = env_copy.step(action)
                
                if done:
                    # From minimizer's perspective, opponent winning is bad
                    child_value = -reward if reward > 0 else reward
                else:
                    child_value = self._minimax(env_copy, depth - 1, alpha, beta, True)
                
                value = min(value, child_value)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
    
    def _restore_state(self, env: TicTacToeEnv, state: list) -> None:
        """Restore environment state from the flat state vector."""
        # State format: 9 owners + 9 pieces + 6 player_pieces + 6 opponent_pieces
        owners = state[0:9]
        pieces = state[9:18]
        player_pieces = [p for p in state[18:24] if p > 0]
        opponent_pieces = [p for p in state[24:30] if p > 0]
        
        # Restore board
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                env.board_owners[i][j] = owners[idx]
                env.board_pieces[i][j] = pieces[idx]
        
        # Determine current player from state context
        # The state is always from current player's perspective
        env.current_player = 1
        env.player_pieces[1] = player_pieces
        env.player_pieces[2] = opponent_pieces
    
    def _copy_env(self, env: TicTacToeEnv) -> TicTacToeEnv:
        """Create a deep copy of the environment."""
        new_env = TicTacToeEnv()
        new_env.board_owners = [row[:] for row in env.board_owners]
        new_env.board_pieces = [row[:] for row in env.board_pieces]
        new_env.player_pieces = {
            1: env.player_pieces[1][:],
            2: env.player_pieces[2][:],
        }
        new_env.current_player = env.current_player
        return new_env
