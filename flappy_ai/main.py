import pygame
from flappy_ai.assets import load_assets
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.base import Base
from flappy_ai.config import *

pygame.init()

# Initialize screen and clock
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load assets
assets = load_assets()

# Initialize game elements
bird = Bird(100, WINDOW_HEIGHT // 2, assets["bird"])
base = Base(assets["base"], WINDOW_HEIGHT - BASE_HEIGHT)
pipes = pygame.sprite.Group()

# Sound effects
point_sound = assets["sounds"]["point"]
hit_sound = assets["sounds"]["hit"]
wing_sound = assets["sounds"]["wing"]

# Game variables
pipe_speed = 4
score = 0

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            wing_sound.play()
            bird.jump()

    bird.update()
    base.update(pipe_speed)

    if len(pipes) == 0 or pipes.sprites()[-1].rect.x < WINDOW_WIDTH - PIPE_DISTANCE:
        pipes.add(Pipe(WINDOW_WIDTH))

    for pipe in pipes:
        pipe.rect.x -= pipe_speed
        pipe.top_rect.x -= pipe_speed

        if not pipe.passed and pipe.rect.right < bird.rect.left:
            pipe.passed = True
            score += 1
            point_sound.play()
            if score % 10 == 0:
                pipe_speed += 1

        if pipe.rect.right < 0:
            pipes.remove(pipe)

    for pipe in pipes:
        if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
            hit_sound.play()
            running = False

    if bird.rect.bottom >= WINDOW_HEIGHT - BASE_HEIGHT:
        hit_sound.play()
        running = False

    screen.blit(assets["background"], (0, 0))
    pipes.draw(screen) 
    screen.blit(base.image, base.rect)
    screen.blit(bird.image, bird.rect)

    score_str = str(score)
    x_pos = 10
    for digit in score_str:
        screen.blit(assets["digits"][digit], (x_pos, 10))
        x_pos += assets["digits"][digit].get_width()

    pygame.display.update()

pygame.quit()
