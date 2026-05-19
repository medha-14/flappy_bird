from pathlib import Path

# Absolute path to the flappy_ai package directory
BASE_DIR = Path(__file__).parent

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 600
BASE_HEIGHT = 112        # actual height of base.png
PIPE_GAP = 180           # vertical gap between top and bottom pipe
PIPE_DISTANCE = 250      # horizontal distance between successive pipes
PIPE_START_X = WINDOW_WIDTH + 10
BIRD_START_X = 100
BIRD_START_Y = WINDOW_HEIGHT // 2
FLOOR_OFFSET = 50
