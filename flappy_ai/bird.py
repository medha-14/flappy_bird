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

    def update(self):
        self.velocity += self.gravity
        self.rect.y += self.velocity
        self.tick += 1

    def jump(self):
        self.velocity = self.lift

    def animate(self):
        self.index = (self.index + 1) % len(self.images)
        self.image = self.images[self.index]
