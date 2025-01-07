import pygame

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_frect(center=(x, y))
        self.velocity = 0
        self.gravity = 0.5
        self.lift = -10
        self.tick = 0

