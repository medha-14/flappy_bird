import pygame

def load_assets():
    bird_images = [
        pygame.image.load("images/bluebird-downflap.png").convert_alpha(),
        pygame.image.load("images/bluebird-midflap.png").convert_alpha(),
        pygame.image.load("images/bluebird-upflap.png").convert_alpha()
    ]
    background = pygame.image.load("images/background-day.png").convert()
    base_img = pygame.image.load("images/base.png").convert_alpha()
    pipe_img = pygame.image.load("images/pipe-green.png").convert_alpha()
    return {
        "bird": bird_images,
        "background": background,
        "base": base_img,
        "pipe": pipe_img
    }
