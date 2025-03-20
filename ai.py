import pygame
import neat
import sys
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.assets import load_assets
from flappy_ai.config import *
from flappy_ai.ai_utils import draw_window, process_birds

# Initialize Pygame
pygame.init()
WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird AI")
assets = load_assets()

FLOOR = WIN.get_height() - FLOOR_OFFSET

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
    pipes = [Pipe(PIPE_START_X)]
    score, run = 0, True

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(BIRD_START_X, BIRD_START_Y))
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
            pipes.append(Pipe(PIPE_START_X))

        check_ground_collision(birds, ge, nets)

        draw_window(WIN, birds, pipes, score, assets)

    pygame.time.wait(1500)
    pygame.quit()
