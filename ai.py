import pygame
import neat
import sys
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.assets import load_assets
from flappy_ai.config import *

# Initialize Pygame
pygame.init()
WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird AI")
assets = load_assets()

FLOOR = WIN.get_height() - 50

def draw_window(win, birds, pipes, score, assets):
    win.fill((0, 0, 0))  # Black background
    for pipe in pipes:
        pipe.draw(win)
    for bird in birds:
        bird.draw(win)

    font = pygame.font.SysFont("arial", 30)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    win.blit(score_text, (10, 10))
    pygame.display.update()

def process_birds(birds, ge, nets, pipes, pipe_ind):
    for i, bird in enumerate(birds):
        bird.move()
        ge[i].fitness += 0.1

        # Neural net decisions
        output = nets[i].activate((
            bird.y,
            abs(bird.y - pipes[pipe_ind].height),
            abs(bird.x - pipes[pipe_ind].x)
        ))
        if output[0] > 0.5:
            bird.jump()

def remove_bird(i, birds, ge, nets):
    ge[i].fitness -= 1
    birds.pop(i)
    ge.pop(i)
    nets.pop(i)

def handle_pipe_collisions(pipes, birds, ge, nets):
    score_incremented = False
    to_remove = []

    for pipe in pipes:
        for i, bird in enumerate(birds):
            if pipe.collide(bird):
                remove_bird(i, birds, ge, nets)
            elif not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                score_incremented = True

        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            to_remove.append(pipe)

    for pipe in to_remove:
        pipes.remove(pipe)

    return score_incremented

def check_ground_collision(birds, ge, nets):
    for i in reversed(range(len(birds))):
        bird = birds[i]
        if bird.y + bird.img.get_height() >= FLOOR or bird.y < 0:
            remove_bird(i, birds, ge, nets)

def eval_genomes(genomes, config):
    nets, ge, birds = [], [], []
    pipes = [Pipe(600)]
    score, run = 0, True

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)

    clock = pygame.time.Clock()

    while run and birds:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pipe_ind = 0
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        process_birds(birds, ge, nets, pipes, pipe_ind)

        if handle_pipe_collisions(pipes, birds, ge, nets):
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(600))

        check_ground_collision(birds, ge, nets)

        draw_window(WIN, birds, pipes, score, assets)

    pygame.quit()
