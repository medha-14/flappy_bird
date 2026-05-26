"""
Train a DQN agent on Flappy Bird with configurable reward policies.

Usage
-----
    # Train with default hybrid reward for 200k steps
    python -m flappy_ai.train

    # Train with a specific reward policy and more steps
    python -m flappy_ai.train --policy sparse --steps 500000

    # Train ALL policies (for paper benchmarks)
    python -m flappy_ai.train --all --steps 300000 --seeds 5

After training, models are saved under ``models/``.
"""

import argparse
import os
import json
import time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend – no display required
import matplotlib.pyplot as plt
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import BaseCallback

from flappy_ai.env import FlappyEnv

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent  # flappy_bird/
MODEL_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

MODEL_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

POLICIES = ["sparse", "dense", "penalty", "distance", "hybrid"]


# ── callback to log episode rewards ─────────────────────────────────────────

class RewardLogger(BaseCallback):
    """Records episode rewards and lengths for plotting later."""

    def __init__(self):
        super().__init__()
        self.episode_rewards: list[float] = []
        self.episode_lengths: list[int] = []
        self.episode_scores: list[int] = []
        self._current_reward = 0.0
        self._current_length = 0

    def _on_step(self) -> bool:
        # SB3 vectorised envs expose info dicts in self.locals["infos"]
        infos = self.locals.get("infos", [])
        for info in infos:
            if "episode" in info:
                self.episode_rewards.append(info["episode"]["r"])
                self.episode_lengths.append(info["episode"]["l"])
                # Our custom "score" is passed through info
                self.episode_scores.append(info.get("score", 0))
        return True


# ── training routine ─────────────────────────────────────────────────────────

def train_single(
    policy: str,
    total_timesteps: int = 200_000,
    seed: int = 0,
    verbose: int = 1,
) -> dict:
    """Train one DQN agent and return metrics."""

    print(f"\n{'='*60}")
    print(f"  Training — policy={policy!r}  seed={seed}  steps={total_timesteps}")
    print(f"{'='*60}\n")

    env = FlappyEnv(reward_policy=policy, render_mode=None)
    # Wrap with Monitor for episode stats
    from stable_baselines3.common.monitor import Monitor
    env = Monitor(env)

    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=1e-4,
        buffer_size=50_000,
        learning_starts=1_000,
        batch_size=64,
        gamma=0.99,
        target_update_interval=1_000,
        exploration_fraction=0.3,
        exploration_final_eps=0.02,
        verbose=verbose,
        seed=seed,
    )

    logger = RewardLogger()
    t0 = time.time()
    model.learn(total_timesteps=total_timesteps, callback=logger)
    elapsed = time.time() - t0

    # Save model
    model_path = MODEL_DIR / f"dqn_{policy}_seed{seed}"
    model.save(str(model_path))
    print(f"Model saved → {model_path}")

    # Compute summary metrics
    rewards = np.array(logger.episode_rewards)
    scores = np.array(logger.episode_scores)

    # Moving average (window = 50)
    window = min(50, len(rewards))
    if window > 0:
        ma = np.convolve(rewards, np.ones(window) / window, mode="valid")
    else:
        ma = rewards

    metrics = {
        "policy": policy,
        "seed": seed,
        "total_timesteps": total_timesteps,
        "num_episodes": len(rewards),
        "mean_reward": float(rewards.mean()) if len(rewards) else 0,
        "std_reward": float(rewards.std()) if len(rewards) else 0,
        "max_reward": float(rewards.max()) if len(rewards) else 0,
        "mean_score": float(scores.mean()) if len(scores) else 0,
        "max_score": int(scores.max()) if len(scores) else 0,
        "training_time_s": round(elapsed, 1),
        "episode_rewards": rewards.tolist(),
        "episode_scores": scores.tolist(),
        "moving_avg_reward": ma.tolist(),
    }

    # Save raw metrics as JSON
    json_path = RESULTS_DIR / f"metrics_{policy}_seed{seed}.json"
    with open(json_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved → {json_path}")

    env.close()
    return metrics


# ── plotting ─────────────────────────────────────────────────────────────────

def plot_single(metrics: dict, out_dir: Path):
    """Save learning-curve plot for one run."""
    rewards = metrics["episode_rewards"]
    ma = metrics["moving_avg_reward"]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rewards, alpha=0.25, color="steelblue", label="Episode reward")
    ax.plot(
        range(len(rewards) - len(ma), len(rewards)),
        ma,
        color="darkblue",
        linewidth=2,
        label="Moving avg (50 ep)",
    )
    ax.set_xlabel("Episode")
    ax.set_ylabel("Reward")
    ax.set_title(f"DQN — {metrics['policy']} reward  (seed {metrics['seed']})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = out_dir / f"curve_{metrics['policy']}_seed{metrics['seed']}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved → {path}")


def plot_comparison(all_metrics: dict[str, list[dict]], out_dir: Path):
    """
    Overlay the moving-average reward curves of every policy.
    ``all_metrics`` maps policy name → list of per-seed metric dicts.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = {
        "sparse": "#e74c3c",
        "dense": "#3498db",
        "penalty": "#e67e22",
        "distance": "#2ecc71",
        "hybrid": "#9b59b6",
    }

    for policy, runs in all_metrics.items():
        # Average the moving-avg curves across seeds
        min_len = min(len(r["moving_avg_reward"]) for r in runs)
        if min_len == 0:
            continue
        stacked = np.array([r["moving_avg_reward"][:min_len] for r in runs])
        mean = stacked.mean(axis=0)
        std = stacked.std(axis=0)

        x = np.arange(min_len)
        c = colors.get(policy, "gray")
        ax.plot(x, mean, label=policy.capitalize(), color=c, linewidth=2)
        ax.fill_between(x, mean - std, mean + std, color=c, alpha=0.15)

    ax.set_xlabel("Episode (moving-avg window)")
    ax.set_ylabel("Mean Reward")
    ax.set_title("DQN Reward Shaping Comparison — Flappy Bird")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = out_dir / "comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Comparison plot saved → {path}")


def plot_score_bar(all_metrics: dict[str, list[dict]], out_dir: Path):
    """Bar chart of mean peak score per policy."""
    policies = []
    means = []
    stds = []

    for policy, runs in all_metrics.items():
        policies.append(policy.capitalize())
        scores = [r["mean_score"] for r in runs]
        means.append(np.mean(scores))
        stds.append(np.std(scores))

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#e74c3c", "#3498db", "#e67e22", "#2ecc71", "#9b59b6"]
    bars = ax.bar(policies, means, yerr=stds, capsize=5, color=colors[:len(policies)],
                  edgecolor="black", linewidth=0.5)
    ax.set_ylabel("Mean Score")
    ax.set_title("Average Game Score by Reward Policy")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    path = out_dir / "score_bar.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Score bar chart saved → {path}")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train DQN on Flappy Bird")
    parser.add_argument("--policy", type=str, default="hybrid",
                        choices=POLICIES, help="Reward policy to use")
    parser.add_argument("--steps", type=int, default=200_000,
                        help="Total training timesteps")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--all", action="store_true",
                        help="Train ALL policies (for paper benchmarks)")
    parser.add_argument("--seeds", type=int, default=1,
                        help="Number of seeds per policy (used with --all)")
    args = parser.parse_args()

    if args.all:
        all_metrics: dict[str, list[dict]] = {}
        for policy in POLICIES:
            all_metrics[policy] = []
            for s in range(args.seeds):
                m = train_single(policy, args.steps, seed=s, verbose=0)
                plot_single(m, RESULTS_DIR)
                all_metrics[policy].append(m)

        # Generate comparison plots
        plot_comparison(all_metrics, RESULTS_DIR)
        plot_score_bar(all_metrics, RESULTS_DIR)
        print(f"\n✅  All training complete.  Results in {RESULTS_DIR}/")
    else:
        m = train_single(args.policy, args.steps, seed=args.seed)
        plot_single(m, RESULTS_DIR)
        print(f"\n✅  Training complete.  Model in {MODEL_DIR}/")


if __name__ == "__main__":
    main()
