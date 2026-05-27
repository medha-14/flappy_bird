"""
Gymnasium environment for Flappy Bird.

Replicates the game physics from bird.py / pipe.py / config.py but runs
entirely headless (no Pygame display) during training.  An optional
``render_mode="human"`` boots a Pygame window for visualisation.

Reward policies
---------------
The ``reward_policy`` constructor argument selects one of the five reward
shaping strategies evaluated in the companion paper.
"""

import math
import random
from typing import Optional

import gymnasium as gym
import numpy as np
from gymnasium import spaces

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 600
BASE_HEIGHT = 112
PIPE_GAP = 180
PIPE_DISTANCE = 250
PIPE_START_X = WINDOW_WIDTH + 10
BIRD_START_X = 100
BIRD_START_Y = WINDOW_HEIGHT // 2

GRAVITY = 0.4
LIFT = -7.5
MAX_FALL_VEL = 10

MIN_PIPE_HEIGHT = 50
PIPE_SPEED = 3.5

FLOOR_Y = WINDOW_HEIGHT - BASE_HEIGHT



class _Bird:
    """Minimal bird state – no Pygame dependency."""

    def __init__(self):
        self.y: float = float(BIRD_START_Y)
        self.vel: float = 0.0

    def jump(self):
        self.vel = LIFT

    def update(self):
        self.vel = min(self.vel + GRAVITY, MAX_FALL_VEL)
        self.y += self.vel


class _Pipe:
    """Minimal pipe pair – no Pygame dependency."""

    PIPE_WIDTH = 52 

    def __init__(self, x: float):
        self.x = x
        min_gap_y = MIN_PIPE_HEIGHT + PIPE_GAP
        max_gap_y = WINDOW_HEIGHT - BASE_HEIGHT - MIN_PIPE_HEIGHT
        self.gap_y = random.randint(min_gap_y, max_gap_y)
        self.gap_center = self.gap_y - PIPE_GAP / 2.0
        self.passed = False

    @property
    def top_rect(self):
        top_h = self.gap_y - PIPE_GAP
        return (self.x, 0, self.PIPE_WIDTH, top_h)

    @property
    def bottom_rect(self):
        return (self.x, self.gap_y, self.PIPE_WIDTH, WINDOW_HEIGHT - self.gap_y)


def _rect_collide(ax, ay, aw, ah, bx, by, bw, bh):
    """Axis-aligned bounding-box collision test."""
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by



class FlappyEnv(gym.Env):
    """
    Flappy Bird as a Gymnasium environment.

    Observation (5-dim continuous):
        0  bird_y            – normalised [0, 1]
        1  bird_velocity     – normalised roughly [-1, 1]
        2  dist_to_pipe      – normalised [0, 1]
        3  pipe_top_y        – normalised [0, 1] (bottom edge of top pipe)
        4  pipe_bottom_y     – normalised [0, 1] (top edge of bottom pipe)

    Actions (Discrete 2):
        0 = do nothing
        1 = flap

    Parameters
    ----------
    reward_policy : str
        One of ``"sparse"``, ``"dense"``, ``"penalty"``, ``"distance"``,
        ``"hybrid"``.
    render_mode : str | None
        ``"human"`` to open a Pygame window.
    max_steps : int
        Episode is truncated after this many steps.
    """

    metadata = {"render_modes": ["human"], "render_fps": 60}

    BIRD_W = 34
    BIRD_H = 24

    def __init__(
        self,
        reward_policy: str = "hybrid",
        render_mode: Optional[str] = None,
        max_steps: int = 5_000,
    ):
        super().__init__()
        self.reward_policy = reward_policy
        self.render_mode = render_mode
        self.max_steps = max_steps

        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(5,), dtype=np.float32,
        )
        self.action_space = spaces.Discrete(2)

        self.bird: Optional[_Bird] = None
        self.pipes: list[_Pipe] = []
        self.score: int = 0
        self.steps: int = 0

        self._screen = None
        self._clock = None
        self._assets = None


    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.bird = _Bird()
        self.pipes = [_Pipe(PIPE_START_X)]
        self.score = 0
        self.steps = 0
        return self._get_obs(), {}

    def step(self, action: int):
        assert self.bird is not None, "Call reset() first"

        if action == 1:
            self.bird.jump()

        self.bird.update()

        for p in self.pipes:
            p.x -= PIPE_SPEED
        if self.pipes[-1].x < WINDOW_WIDTH - PIPE_DISTANCE:
            self.pipes.append(_Pipe(PIPE_START_X))
        self.pipes = [p for p in self.pipes if p.x + _Pipe.PIPE_WIDTH > 0]

        scored = False
        for p in self.pipes:
            if not p.passed and p.x + _Pipe.PIPE_WIDTH < BIRD_START_X:
                p.passed = True
                self.score += 1
                scored = True

        bird_x = float(BIRD_START_X)
        bird_y = self.bird.y
        dead = False

        if bird_y + self.BIRD_H / 2 >= FLOOR_Y or bird_y - self.BIRD_H / 2 <= 0:
            dead = True

        if not dead:
            bx = bird_x - self.BIRD_W / 2
            by = bird_y - self.BIRD_H / 2
            for p in self.pipes:
                tx, ty, tw, th = p.top_rect
                bx2, by2, bw2, bh2 = p.bottom_rect
                if _rect_collide(bx, by, self.BIRD_W, self.BIRD_H, tx, ty, tw, th):
                    dead = True
                    break
                if _rect_collide(bx, by, self.BIRD_W, self.BIRD_H, bx2, by2, bw2, bh2):
                    dead = True
                    break

        reward = self._compute_reward(scored, dead)

        self.steps += 1
        truncated = self.steps >= self.max_steps
        terminated = dead

        if self.render_mode == "human":
            self.render()

        return self._get_obs(), reward, terminated, truncated, {"score": self.score}


    def _compute_reward(self, scored: bool, dead: bool) -> float:
        policy = self.reward_policy

        if policy == "sparse":
            if dead:
                return -1.0
            return 1.0 if scored else 0.0

        elif policy == "dense":
            if dead:
                return -1.0
            r = 0.1
            if scored:
                r += 1.0
            return r

        elif policy == "penalty":
            if dead:
                return -1.0
            r = 0.0
            if scored:
                r += 1.0
            pipe = self._nearest_pipe()
            if pipe is not None:
                dist_to_top = abs(self.bird.y - (pipe.gap_y - PIPE_GAP))
                dist_to_bot = abs(self.bird.y - pipe.gap_y)
                min_dist = min(dist_to_top, dist_to_bot)
                if min_dist < 30:
                    r -= 0.5
            return r

        elif policy == "distance":
            if dead:
                return -1.0
            pipe = self._nearest_pipe()
            if pipe is not None:
                dist = abs(self.bird.y - pipe.gap_center)
                max_dist = WINDOW_HEIGHT / 2.0
                r = 1.0 - (dist / max_dist)
                return max(r, 0.0)
            return 0.1

        elif policy == "hybrid":
            if dead:
                return -1.0
            r = 0.1 
            pipe = self._nearest_pipe()
            if pipe is not None:
                dist = abs(self.bird.y - pipe.gap_center)
                max_dist = WINDOW_HEIGHT / 2.0
                r += 0.5 * (1.0 - dist / max_dist)
            if scored:
                r += 2.0
            return r

        else:
            raise ValueError(f"Unknown reward policy: {policy!r}")

    def _nearest_pipe(self) -> Optional[_Pipe]:
        """Return the next pipe the bird hasn't passed yet."""
        for p in self.pipes:
            if p.x + _Pipe.PIPE_WIDTH > BIRD_START_X:
                return p
        return self.pipes[0] if self.pipes else None


    def _get_obs(self) -> np.ndarray:
        pipe = self._nearest_pipe()
        if pipe is None:
            return np.zeros(5, dtype=np.float32)

        return np.array([
            self.bird.y / WINDOW_HEIGHT,
            self.bird.vel / MAX_FALL_VEL,
            (pipe.x - BIRD_START_X) / WINDOW_WIDTH,
            (pipe.gap_y - PIPE_GAP) / WINDOW_HEIGHT,
            pipe.gap_y / WINDOW_HEIGHT,
        ], dtype=np.float32)


    def render(self):
        if self.render_mode != "human":
            return

        import pygame
        from flappy_ai.assets import load_assets

        if self._screen is None:
            pygame.init()
            pygame.mixer.init()
            self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Flappy Bird AI — DQN")
            self._clock = pygame.time.Clock()
            self._assets = load_assets()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        screen = self._screen
        assets = self._assets

        screen.blit(assets["bg_day"], (0, 0))

        pipe_img = assets["pipe"]
        pipe_img_top = pygame.transform.flip(pipe_img, False, True)
        for p in self.pipes:
            screen.blit(pipe_img, (int(p.x), int(p.gap_y)))
            top_h = p.gap_y - PIPE_GAP
            screen.blit(pipe_img_top, (int(p.x), int(top_h - pipe_img_top.get_height())))

        screen.blit(assets["base"], (0, FLOOR_Y))

        bird_img = assets["bird"][1]
        screen.blit(bird_img, (int(BIRD_START_X - self.BIRD_W / 2),
                               int(self.bird.y - self.BIRD_H / 2)))

        font = pygame.font.Font(None, 36)
        txt = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(txt, (10, 10))

        pol_txt = font.render(f"Policy: {self.reward_policy}", True, (255, 220, 100))
        screen.blit(pol_txt, (10, 45))

        pygame.display.flip()
        self._clock.tick(self.metadata["render_fps"])

    def close(self):
        if self._screen is not None:
            import pygame
            pygame.quit()
            self._screen = None
