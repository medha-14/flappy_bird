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

score = 0
running = True

def game_over():
    screen.blit(assets["game_over"], (
        (WINDOW_WIDTH - assets["game_over"].get_width()) // 2,
        WINDOW_HEIGHT // 3
    ))
    pygame.display.update()
    pygame.time.wait(2000)

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    bird.update()
    base.update(4)

    if len(pipes) == 0 or pipes.sprites()[-1].rect.x < WINDOW_WIDTH - PIPE_DISTANCE:
        pipes.add(Pipe(WINDOW_WIDTH))

    pipes.update()

    for pipe in pipes:
        if pipe.rect.right < 0:
            pipes.remove(pipe)

        if pipe.rect.colliderect(bird.rect) or pipe.top_rect.colliderect(bird.rect):
            game_over()
            running = False

        if not pipe.passed and pipe.rect.right < bird.rect.left:
            pipe.passed = True
            score += 1

    if bird.rect.bottom >= WINDOW_HEIGHT or bird.rect.top <= 0:
        game_over()
        running = False

    screen.blit(assets["background"], (0, 0))
    pipes.draw(screen)
    screen.blit(base.image, base.rect)
    screen.blit(bird.image, bird.rect)

  
    pygame.display.update()

pygame.quit()
