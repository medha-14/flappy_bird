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
    
    # Load digit images for score (assuming you have images named 0.png, 1.png, ..., 9.png)
    digit_images = {}
    for i in range(10):
        digit_images[str(i)] = pygame.image.load(f"images/{i}.png").convert_alpha()

    return {
        "bird": bird_images,
        "background": background,
        "base": base_img,
        "pipe": pipe_img,
        "digits": digit_images  # Adding digit images to the dictionary
    }
