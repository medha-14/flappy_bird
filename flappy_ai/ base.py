import pygame

class Base(pygame.sprite.Sprite):
    def __init__(self, image, y_position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = y_position

    def update(self, scroll_speed):
        self.rect.x -= scroll_speed
        if self.rect.right <= 0:
            self.rect.left = 0
