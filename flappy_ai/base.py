import pygame

class Base(pygame.sprite.Sprite):
    def __init__(self, image, y_position):
        super().__init__()
        self.image  = image
        self.width  = image.get_width()
        self.rect   = self.image.get_rect(topleft=(0, y_position))
        self.x1     = 0
        self.x2     = self.width   # second copy placed right after first
        self.y      = y_position

    def update(self, scroll_speed):
        self.x1 -= scroll_speed
        self.x2 -= scroll_speed
        # When a copy scrolls fully off-screen to the left, wrap it to the right
        if self.x1 + self.width <= 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width <= 0:
            self.x2 = self.x1 + self.width

    def draw(self, surface):
        surface.blit(self.image, (self.x1, self.y))
        surface.blit(self.image, (self.x2, self.y))
