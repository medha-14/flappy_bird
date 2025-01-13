import pygame

class Pipe(pygame.sprite.Sprite):
    def __init__(self, image, x, y, flipped=False):
        super().__init__()
        self.image = pygame.transform.flip(image, False, flipped) if flipped else image
        self.rect = self.image.get_rect(midtop=(x, y)) if not flipped else self.image.get_rect(midbottom=(x, y))

    def update(self, speed):
        self.rect.x -= speed
