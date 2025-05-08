import pygame
from flappy_ai.assets import load_assets
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.base import Base
from flappy_ai.config import *

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

assets = load_assets()
bird = Bird(100, WINDOW_HEIGHT // 2, assets["bird"])
pipes = pygame.sprite.Group()
base = Base(assets["base"], WINDOW_HEIGHT - BASE_HEIGHT)
running = True

while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    bird.update()
    base.update(4)

    screen.blit(assets["background"], (0, 0))
    pipes.draw(screen)
    screen.blit(base.image, base.rect)
    screen.blit(bird.image, bird.rect)

    pygame.display.update()

pygame.quit()
