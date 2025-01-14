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

def eval_genomes(genomes, config):
    nets = []
    birds = []
    ge = []

    # Initialize birds and networks for each genome
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))  # Starting position
        genome.fitness = 0
        ge.append(genome)
    
    clock = pygame.time.Clock()
    run = True

    while run and len(birds) > 0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
# Inside eval_genomes

    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for x, bird in enumerate(birds):
            bird.move()  # Update bird's position
            ge[x].fitness += 0.1  # Reward bird for surviving