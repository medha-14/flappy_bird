import pygame
from random import randint

#classes
class Background(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.image=background_day
        self.rect=self.image.get_frect(topleft=(0,0))

class BaseBack(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.image=base
        self.rect=self.image.get_frect(midbottom=(WINDOW_WIDTH/2,WINDOW_HEIGHT))        

class Bird(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = bird
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.rect.top > 0:
                self.rect.y -= int(200 * dt)

#initialize
pygame.init()
WINDOW_HEIGHT=720
WINDOW_WIDTH=480
display_surface=pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
Clock=pygame.time.Clock()
running =True

#imports
background_day = pygame.image.load("images/background-day.png").convert_alpha()
background_day = pygame.transform.scale(background_day, (WINDOW_WIDTH, WINDOW_HEIGHT))

background_night = pygame.image.load ("images/background-night.png").convert_alpha()
background_night= pygame.transform.scale(background_night, (WINDOW_WIDTH, WINDOW_HEIGHT))

base = pygame.image.load("images/base.png").convert_alpha()
base = pygame.transform.scale(base, (WINDOW_WIDTH, 120))

bird = pygame.image.load("images/bluebird-downflap.png").convert_alpha()
bird = pygame.transform.scale_by(bird, 1.5)

#sprites
all_sprites=pygame.sprite.Group()
background  = Background(all_sprites)
base = BaseBack(all_sprites)
bird = Bird(all_sprites)

#gameloop
while running :
    dt= Clock.tick()/1000 
    #events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #update
    all_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()    
