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

FLOOR = WIN.get_height() - 50  # Define the floor position

def draw_window(win, birds, pipes, score, assets):
    win.fill((0, 0, 0))  # Fill the background with black

    for pipe in pipes:
        pipe.draw(win)  # Draw each pipe

    for bird in birds:
        bird.draw(win)  # Draw each bird

    # Draw the scoe
    font = pygame.font.SysFont("arial", 30)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    win.blit(score_text, (10, 10))

    pygame.display.update()  # Update the screen

def update_bird_fitness(birds, ge, nets, pipes, pipe_ind):
    for x, bird in enumerate(birds):
        bird.move()  # Move bird
        ge[x].fitness += 0.1  # Reward for surviving

        # Neural Network inputs:
        output = nets[x].activate((
            bird.y,  # Bird's y position
            abs(bird.y - pipes[pipe_ind].height),  # Distance to next pipe
            abs(bird.x - pipes[pipe_ind].x)  # Distance to pipe
        ))

        if output[0] > 0.5:  # If output > 0.5, bird jumps
            bird.jump()

def handle_collisions(birds, ge, nets, pipes):
    rem = []
    for pipe in pipes:
        for x, bird in enumerate(birds):
            if pipe.collide(bird):  # Check if bird hits pipe
                ge[x].fitness -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                return True  # Pipe passed by bird

        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            rem.append(pipe)
    
    # Remove passed pipes
    for r in rem:
        pipes.remove(r)

    return False

def eval_genomes(genomes, config):
    nets = []
    birds = []
    ge = []
    pipes = [Pipe(600)]  # Initialize the pipes list with one pipe

    # Initialize birds and networks for each genome
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))  # Starting position
        genome.fitness = 0
        ge.append(genome)
    
    clock = pygame.time.Clock()
    run = True
    score = 0  # Initialize score

    while run and len(birds) > 0:
        clock.tick(30)

        pipe_ind = 0
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1  # Target the next pipe

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        update_bird_fitness(birds, ge, nets, pipes, pipe_ind)

        # Pipe handling logic
        add_pipe = handle_collisions(birds, ge, nets, pipes)
        
        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5  # Reward for passing a pipe
            pipes.append(Pipe(600))  # Add a new pipe

        # Check for bird hitting the ground or top
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= FLOOR or bird.y < 0:  # Bird hits ground or top
                ge[x].fitness -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(WIN, birds, pipes, score, assets)

    pygame.quit()
