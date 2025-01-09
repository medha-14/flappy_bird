import pygame

class Base(pygame.sprite.Sprite):
    def __init__(self, image, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(0, y))
        self.scroll = 0

    def update(self, speed):
        self.scroll -= speed
        if abs(self.scroll) > 30:
            self.scroll = 0
