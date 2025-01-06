import pygame
from random import randint

# Constants
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 480
BASE_HEIGHT=120

# Classes
class Background(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = background_day
        self.rect = self.image.get_rect(topleft=(0, 0))

class Bird(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        self.frames = [
            pygame.image.load("images/bluebird-downflap.png").convert_alpha(),
            pygame.image.load("images/bluebird-midflap.png").convert_alpha(),
            pygame.image.load("images/bluebird-upflap.png").convert_alpha()
        ]
        
        self.index = 0
        self.counter = 0
        self.animation_speed = 10
        
        self.image = self.frames[self.index]
        self.rect = self.image.get_frect(center=(120,WINDOW_HEIGHT/2))
        self.mask = pygame.mask.from_surface(self.image)

        # Fly Timer
        self.can_fly=True
        self.last_fly_time=0
        self.cooldown_time=1000

    def Keytimer(self):
        self.current_time = pygame.time.get_ticks()
        if self.current_time - self.last_shoot_time >= self.cooldown_time:
            self.can_shoot=True       

    def animate(self):
      
        self.counter += 1
        
        if self.counter > self.animation_speed:
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.counter = 0

    def update(self, dt):
        self.animate()
        keys = pygame.key.get_just_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.can_fly:
            if self.rect.top > 0:
                self.rect.y -= int(4000 * dt)
                wing_sound.play()
        else:
            if self.rect.bottom < (WINDOW_HEIGHT-BASE_HEIGHT):
                self.rect.y += int(150* dt)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midtop=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.x -= int(100 * dt)

class UpPipe(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.x -= int(100 * dt)

def collisions():
    global running
    collided = pygame.sprite.spritecollide(bird, pipe_sprites, True, pygame.sprite.collide_mask)
    if collided:
        print("Collision detected!")
        die_sound.play()
        running = False

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
base_rect = base.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT))

pipe_down = pygame.image.load("images/pipe-green.png").convert_alpha()
pipe_up= pygame.transform.rotate(pipe_down,180)

die_sound=pygame.mixer.Sound("audio/die.ogg")
die_sound.set_volume(0.3)
hit_sound=pygame.mixer.Sound("audio/hit.ogg")
hit_sound.set_volume(0.3)
point_sound=pygame.mixer.Sound("audio/point.ogg")
point_sound.set_volume(0.3)
swoosh_sound=pygame.mixer.Sound("audio/swoosh.ogg")
swoosh_sound.set_volume(0.3)
wing_sound=pygame.mixer.Sound("audio/wing.ogg")
wing_sound.set_volume(0.3)


# Sprites
all_sprites = pygame.sprite.Group()
pipe_sprites = pygame.sprite.Group()
background = Background(all_sprites)
bird = Bird(all_sprites)

# Pipe event
pipe_event = pygame.event.custom_type()
pygame.time.set_timer(pipe_event,1250)  

# Game loop
while running:
    dt = Clock.tick(60) / 1000

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pipe_event:
            bottom_pipe_height = randint(200, 480)
            Pipe(pipe_down, (WINDOW_WIDTH, bottom_pipe_height), [all_sprites, pipe_sprites])
            
            top_pipe_height = bottom_pipe_height - (randint(125,175))
            UpPipe(pipe_up, (WINDOW_WIDTH, top_pipe_height), [all_sprites, pipe_sprites])

    # Update
    all_sprites.update(dt)
    pipe_sprites.update(dt)
    collisions()
    
    # Draw
    display_surface.fill((0, 0, 0)) 
    all_sprites.draw(display_surface)  
    pipe_sprites.draw(display_surface)
    display_surface.blit(base,base_rect)
    

    pygame.display.update()

pygame.quit()
