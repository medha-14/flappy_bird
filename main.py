import pygame
from random import randint

# Constants
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 480
BASE_HEIGHT=120

# Classes
class Background(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = background_day
        self.rect = self.image.get_rect(topleft=(0, 0))

class BaseBack(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = base
        self.rect = self.image.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT))

class Bird(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        self.frames = [
            pygame.image.load("images/bluebird-downflap.png").convert_alpha(),
            pygame.image.load("images/bluebird-midflap.png").convert_alpha(),
            pygame.image.load("images/bluebird-upflap.png").convert_alpha()
        ]
        
        self.frames = [pygame.transform.scale_by(frame, 1.5) for frame in self.frames]
        
       
        self.index = 0
        self.counter = 0
        self.animation_speed = 10
        
        self.image = self.frames[self.index]
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/2))

    def animate(self):
      
        self.counter += 1
        
        if self.counter > self.animation_speed:
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.counter = 0

    def update(self, dt):
        self.animate()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.rect.top > 0:
                self.rect.y -= int(200 * dt)
        else:
            if self.rect.bottom < (WINDOW_HEIGHT-BASE_HEIGHT):
                self.rect.y += int(150 * dt)


# Initialize
pygame.init()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
Clock = pygame.time.Clock()
running = True

# Imports
background_day = pygame.image.load("images/background-day.png").convert_alpha()
background_day = pygame.transform.scale(background_day, (WINDOW_WIDTH, WINDOW_HEIGHT))

background_night = pygame.image.load("images/background-night.png").convert_alpha()
background_night = pygame.transform.scale(background_night, (WINDOW_WIDTH, WINDOW_HEIGHT))

base = pygame.image.load("images/base.png").convert_alpha()
base = pygame.transform.scale(base, (WINDOW_WIDTH, BASE_HEIGHT))

# Sprites
all_sprites = pygame.sprite.Group()
background = Background(all_sprites)
base = BaseBack(all_sprites)
bird = Bird(all_sprites)

# Game loop
while running:
    dt = Clock.tick(60) / 1000

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update(dt)

    # Draw
    display_surface.fill((0, 0, 0))
    all_sprites.draw(display_surface)
    pygame.display.update()

pygame.quit()
