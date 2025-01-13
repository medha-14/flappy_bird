import neat
import pygame
import os
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.assets import load_assets
from flappy_ai.config import *

def eval_genomes(genomes, config):
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird AI")

    assets = load_assets()

    # Lists to hold genome-related data
    birds = []
    nets = []
    ge = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(100, WINDOW_HEIGHT // 2, assets["bird"]))
        genome.fitness = 0
        ge.append(genome)

    running = True
    pipes = [Pipe(WINDOW_WIDTH + 100, assets["pipe"])]

    while running and len(birds) > 0:
        clock.tick(60)
        screen.blit(assets["background"], (0, 0))

        # Pipe logic
        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            pipe.draw(screen)

            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[i].fitness -= 1
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.width < 0:
                rem.append(pipe)

        if add_pipe:
            pipes.append(Pipe(WINDOW_WIDTH + 100, assets["pipe"]))
            for genome in ge:
                genome.fitness += 5

        for r in rem:
            pipes.remove(r)

        for i, bird in enumerate(birds):
            bird.move()

            # Input features: y-position, dist to next pipe, top of next pipe
            pipe_ind = 0
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].width:
                pipe_ind = 1

            bird_x = bird.x
            bird_y = bird.y
            pipe_x = pipes[pipe_ind].x
            pipe_top = pipes[pipe_ind].top
            pipe_bottom = pipes[pipe_ind].bottom

            # Feed-forward: [bird_y, dist to pipe, height diff]
            output = nets[i].activate((bird_y, abs(bird_y - pipe_top), abs(bird_y - pipe_bottom)))

            if output[0] > 0.5:
                bird.jump()

            # Reward for staying alive
            ge[i].fitness += 0.1

            # Ground collision
            if bird.y + bird.image.get_height() >= WINDOW_HEIGHT - BASE_HEIGHT or bird.y < 0:
                ge[i].fitness -= 1
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)

            bird.draw(screen)

        screen.blit(assets["base"], (0, WINDOW_HEIGHT - BASE_HEIGHT))
        pygame.display.update()

    pygame.quit()

def run_neat(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    p = neat.Population(config)

    # Add NEAT reporters for monitoring
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    # Run NEAT
    winner = p.run(eval_genomes, 50)
