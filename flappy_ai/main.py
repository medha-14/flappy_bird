import pygame
from flappy_ai.assets import load_assets
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.base import Base
from flappy_ai.config import *

pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

assets = load_assets()

bird = Bird(100, WINDOW_HEIGHT // 2, assets["bird"])
base = Base(assets["base"], WINDOW_HEIGHT - BASE_HEIGHT)
pipes = pygame.sprite.Group()

score = 0  # Initialize the score
running = True

def game_over():
    screen.blit(assets["game_over"], (
        (WINDOW_WIDTH - assets["game_over"].get_width()) // 2,
        WINDOW_HEIGHT // 3
    ))
    pygame.display.update()
    pygame.time.wait(2000)
    
    
while running:
    dt = clock.tick(60) / 1000  # Limit to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    bird.update()
    base.update(4)

    # Update the score display
    score_str = str(score)
    x_pos = 10  # Starting position for drawing the score
    for digit in score_str:
        screen.blit(assets["digits"][digit], (x_pos, 10))  # Blit each digit image
        x_pos += assets["digits"][digit].get_width()  # Move x_pos to the next digit's position

    # Pipe logic: add a new pipe if the last pipe is far enough
    if len(pipes) == 0 or pipes.sprites()[-1].rect.x < WINDOW_WIDTH - PIPE_DISTANCE:
        pipes.add(Pipe(WINDOW_WIDTH))

    # Update all pipes
    pipes.update()

    # Remove pipes that have moved off-screen
    for pipe in pipes:
        if pipe.rect.right < 0:
            pipes.remove(pipe)
   # Draw everything to the screen
    screen.blit(assets["background"], (0, 0))  # Background
    pipes.draw(screen)  # Draw pipes
    screen.blit(base.image, base.rect)  # Draw base
    screen.blit(bird.image, bird.rect)  # Draw bird
 

   
    # Update the screen
    pygame.display.update()  # Update the screen

pygame.quit()
