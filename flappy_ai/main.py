import pygame
from flappy_ai.assets import load_assets
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.base import Base
from flappy_ai.config import *

# Initialize pygame
pygame.init()

# Set up the display and clock
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load assets
assets = load_assets()

# Create bird, pipes, and base objects
bird = Bird(100, WINDOW_HEIGHT // 2, assets["bird"])
base = Base(assets["base"], WINDOW_HEIGHT - BASE_HEIGHT)

# Groups for pipes
pipes = pygame.sprite.Group()

# Main game loop
running = True
while running:
    # Frame rate control
    dt = clock.tick(60) / 1000

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game objects
    bird.update()
    base.update(4)  # Move base horizontally

    # Generate new pipes every certain interval
    if len(pipes) == 0 or pipes.sprites()[-1].rect.x < WINDOW_WIDTH - PIPE_DISTANCE:
        pipes.add(Pipe(WINDOW_WIDTH))

    # Move pipes
    pipes.update()

    # Remove off-screen pipes
    for pipe in pipes:
        if pipe.rect.right < 0:
            pipes.remove(pipe)

    # Drawing to the screen
    screen.blit(assets["background"], (0, 0))  # Draw background
    pipes.draw(screen)  # Draw pipes
    screen.blit(base.image, base.rect)  # Draw base
    screen.blit(bird.image, bird.rect)  # Draw bird

    # Update display
    pygame.display.update()

# Quit pygame
pygame.quit()
