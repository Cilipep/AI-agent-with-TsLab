"""DQN Reinforcement Learning agent for BTC trading."""
import os

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque


class DuelingDQN(nn.Module):
    def __init__(self, state_size, action_size=3, hidden=128):
        super().__init__()
        self.feature = nn.Sequential(
            nn.Linear(state_size, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.value = nn.Sequential(
            nn.Linear(hidden, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )
        self.advantage = nn.Sequential(
            nn.Linear(hidden, 64),
            nn.ReLU(),
            nn.Linear(64, action_size),
        )

    def forward(self, x):
        feat = self.feature(x)
        val = self.value(feat)
        adv = self.advantage(feat)
        return val + adv - adv.mean(dim=1, keepdim=True)


class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (np.array(states), np.array(actions), np.array(rewards, dtype=np.float32),
                np.array(next_states), np.array(dones, dtype=np.float32))

    def __len__(self):
        return len(self.buffer)


class TradingEnv:
    """Simple trading environment for DQN."""
    def __init__(self, prices, features, window=30, commission=0.001,
                 stop_loss=0.03, take_profit=0.09):
        self.prices = prices
        self.features = features
        self.window = window
        self.commission = commission
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.n = len(prices) - window
        self.reset()

    def reset(self):
        self.step_idx = 0
        self.position = 0  # 0=flat, 1=long
        self.entry_price = 0
        self.total_reward = 0
        self.trades = []
        self.equity = [1.0]
        return self._get_state()

    def _get_state(self):
        start = self.step_idx
        end = start + self.window
        return self.features[start:end].flatten().astype(np.float32)

    def step(self, action):
        # action: 0=hold, 1=buy, 2=sell
        current_price = self.prices[self.step_idx + self.window]
        reward = 0
        done = False

        if action == 1 and self.position == 0:  # Buy
            self.position = 1
            self.entry_price = current_price
            reward -= self.commission  # entry cost

        elif action == 2 and self.position == 1:  # Sell
            pnl = (current_price - self.entry_price) / self.entry_price
            reward += pnl - self.commission  # exit cost
            self.trades.append(pnl)
            self.position = 0

        # Check stop-loss / take-profit if in position
        if self.position == 1:
            pnl = (current_price - self.entry_price) / self.entry_price
            if pnl <= -self.stop_loss:
                reward += pnl - self.commission
                self.trades.append(pnl)
                self.position = 0
            elif pnl >= self.take_profit:
                reward += pnl - self.commission
                self.trades.append(pnl)
                self.position = 0

        # Update equity
        eq = self.equity[-1] * (1 + reward)
        self.equity.append(eq)
        self.total_reward += reward

        self.step_idx += 1
        if self.step_idx >= self.n:
            done = True
            # Close open position at end
            if self.position == 1:
                final_price = self.prices[self.step_idx + self.window - 1]
                pnl = (final_price - self.entry_price) / self.entry_price
                reward += pnl - self.commission
                self.trades.append(pnl)
                self.position = 0

        next_state = self._get_state() if not done else np.zeros_like(self._get_state())
        return next_state, reward, done


class DQNAgent:
    def __init__(self, state_size, action_size=3, lr=1e-3, gamma=0.99,
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=5000):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.steps = 0

        self.policy_net = DuelingDQN(state_size, action_size)
        self.target_net = DuelingDQN(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.buffer = ReplayBuffer(10000)
        self.losses = []

    def select_action(self, state, min_confidence=0.0):
        self.steps += 1
        self.epsilon = max(self.epsilon_end,
                           self.epsilon - (self.epsilon - self.epsilon_end) / self.epsilon_decay)

        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        with torch.no_grad():
            state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            q_values = self.policy_net(state_t)
            q_vals = q_values.numpy().flatten()

            # Aggressive filter: only act if confidence is high enough
            max_q = q_vals.max()
            if max_q < min_confidence:
                return 0  # Hold

            return int(q_vals.argmax())

    def train_step(self, batch_size=64):
        if len(self.buffer) < batch_size:
            return

        states, actions, rewards, next_states, dones = self.buffer.sample(batch_size)

        states_t = torch.tensor(states, dtype=torch.float32)
        actions_t = torch.tensor(actions, dtype=torch.long)
        rewards_t = torch.tensor(rewards, dtype=torch.float32)
        next_states_t = torch.tensor(next_states, dtype=torch.float32)
        dones_t = torch.tensor(dones, dtype=torch.float32)

        # Current Q values
        q_values = self.policy_net(states_t)
        q_vals = q_values.gather(1, actions_t.unsqueeze(1)).squeeze(1)

        # Double DQN: use policy net for action selection, target net for evaluation
        with torch.no_grad():
            next_actions = self.policy_net(next_states_t).argmax(dim=1)
            next_q_values = self.target_net(next_states_t)
            next_q_vals = next_q_values.gather(1, next_actions.unsqueeze(1)).squeeze(1)
            target_q = rewards_t + self.gamma * next_q_vals * (1 - dones_t)

        loss = nn.SmoothL1Loss()(q_vals, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()

        self.losses.append(loss.item())

    def update_target(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())


def train_dqn(prices, features, window=30, episodes=100, commission=0.001,
              stop_loss=0.03, take_profit=0.09, min_confidence=0.6,
              n_cpu=2, quiet=True):
    """Train DQN agent on price data."""
    torch.set_num_threads(n_cpu)
    state_size = window * features.shape[1]
    env = TradingEnv(prices, features, window, commission, stop_loss, take_profit)
    agent = DQNAgent(state_size, lr=1e-3, gamma=0.99)

    best_reward = -float("inf")
    best_state = None

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False

        while not done:
            action = agent.select_action(state, min_confidence)
            next_state, reward, done = env.step(action)
            agent.buffer.push(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            agent.train_step(batch_size=64)

        if ep % 10 == 0:
            agent.update_target()

        if total_reward > best_reward:
            best_reward = total_reward
            best_state = {k: v.cpu().clone() for k, v in agent.policy_net.state_dict().items()}

        if not quiet and ep % 20 == 0:
            n_trades = len(env.trades)
            win_rate = (np.array(env.trades) > 0).mean() * 100 if n_trades > 0 else 0
            print(f"  Ep {ep:3d} | reward={total_reward:+.4f} | trades={n_trades} | win={win_rate:.0f}%")

    if best_state:
        agent.policy_net.load_state_dict(best_state)
        agent.target_net.load_state_dict(best_state)

    return agent


def evaluate_dqn(agent, prices, features, window=30, commission=0.001,
                 stop_loss=0.03, take_profit=0.09, min_confidence=0.6):
    """Evaluate trained DQN agent."""
    env = TradingEnv(prices, features, window, commission, stop_loss, take_profit)
    state = env.reset()
    done = False

    agent.policy_net.eval()
    while not done:
        action = agent.select_action(state, min_confidence)
        state, _, done = env.step(action)

    n_trades = len(env.trades)
    equity = np.array(env.equity)
    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100
    win_rate = (np.array(env.trades) > 0).mean() * 100 if n_trades > 0 else 0

    return {
        "total_return_pct": total_return,
        "max_drawdown_pct": max_dd,
        "n_trades": n_trades,
        "win_rate_pct": win_rate,
        "equity": equity,
        "trades": env.trades,
    }
