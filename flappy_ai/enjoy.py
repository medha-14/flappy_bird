"""
Visualise a trained DQN agent playing Flappy Bird.

Usage
-----
    # Play with the hybrid-reward model (default)
    python -m flappy_ai.enjoy

    # Play with a specific model
    python -m flappy_ai.enjoy --policy sparse --seed 0

    # Run for N episodes
    python -m flappy_ai.enjoy --episodes 10
"""

import argparse
from pathlib import Path

from stable_baselines3 import DQN

from flappy_ai.env import FlappyEnv

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models"

POLICIES = ["sparse", "dense", "penalty", "distance", "hybrid"]


def enjoy(policy: str = "hybrid", seed: int = 0, episodes: int = 5):
    model_path = MODEL_DIR / f"dqn_{policy}_seed{seed}"
    if not model_path.with_suffix(".zip").exists():
        print(f"    Model not found: {model_path}.zip")
        print(f"    Train it first:  python -m flappy_ai.train --policy {policy} --seed {seed}")
        return

    print(f"Loading model from {model_path} …")
    model = DQN.load(str(model_path))

    env = FlappyEnv(reward_policy=policy, render_mode="human")

    for ep in range(1, episodes + 1):
        obs, _ = env.reset()
        done = False
        total_reward = 0.0
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            total_reward += reward
            done = terminated or truncated

        print(f"Episode {ep}:  score={info.get('score', '?')}  reward={total_reward:.1f}")

    env.close()


def main():
    parser = argparse.ArgumentParser(description="Watch trained DQN play Flappy Bird")
    parser.add_argument("--policy", type=str, default="hybrid", choices=POLICIES)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--episodes", type=int, default=5)
    args = parser.parse_args()

    enjoy(args.policy, args.seed, args.episodes)


if __name__ == "__main__":
    main()
