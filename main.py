import pygame
from random import randint

# Constants
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 480
BASE_HEIGHT = 120

# Variables
ground_scroll = 0
scroll_speed = 4
game_active = True
falling = False  # New state for falling after collision

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
        self.can_fly = True
        self.last_fly_time = 0
        self.cooldown_time = 1000

    def animate(self):
        self.counter += 1
        if self.counter > self.animation_speed:
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.counter = 0

    def update(self, dt):
        self.animate()
        keys = pygame.key.get_just_pressed()

        if game_active:  # Bird only flies when the game is active
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.can_fly:
                if self.rect.top > 0:
                    self.rect.y -= int(4000 * dt)
                    wing_sound.play()
            else:
                if self.rect.bottom < (WINDOW_HEIGHT - BASE_HEIGHT):
                    self.rect.y += int(150 * dt)
        elif falling:  # Bird starts falling after collision
            if self.rect.bottom < (WINDOW_HEIGHT - BASE_HEIGHT):
                self.rect.y += int(150 * dt)
            # Ensure bird stops at the base level
            if self.rect.bottom >= (WINDOW_HEIGHT - BASE_HEIGHT):
                self.rect.bottom = WINDOW_HEIGHT - BASE_HEIGHT

# Pipe class remains unchanged
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

# Collisions check
def collisions():
    global scroll_speed, game_state, game_active, falling
    collided = pygame.sprite.spritecollide(bird, pipe_sprites, False, pygame.sprite.collide_mask)
    if collided:
        hit_sound.play()
        die_sound.play()
        game_active = False  # Stop the game, no more flying
        falling = True  # Start the falling logic
        scroll_speed = 0
        game_state = "game_over"  # Correctly update the game state here

# Initialize
pygame.init()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
Clock = pygame.time.Clock()
running = True
game_state = "start"
game_active = True

# Imports for images and sounds (unchanged)
background_day = pygame.image.load("images/background-day.png").convert_alpha()
background_day = pygame.transform.scale(background_day, (WINDOW_WIDTH, WINDOW_HEIGHT))

background_night = pygame.image.load("images/background-night.png").convert_alpha()
background_night = pygame.transform.scale(background_night, (WINDOW_WIDTH, WINDOW_HEIGHT))

base = pygame.image.load("images/base.png").convert_alpha()
base = pygame.transform.scale(base, (WINDOW_WIDTH+20, BASE_HEIGHT))


pipe_down = pygame.image.load("images/pipe-green.png").convert_alpha()
pipe_up= pygame.transform.rotate(pipe_down,180)

game_over = pygame.image.load("images/gameover.png").convert_alpha()
game_over_rect = game_over.get_frect(center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/2))
start_screen = pygame.image.load("images/message.png").convert_alpha()
start_screen_rect = game_over.get_frect(center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/2- 150))

die_sound = pygame.mixer.Sound("audio/die.ogg")
die_sound.set_volume(0.3)
hit_sound = pygame.mixer.Sound("audio/hit.ogg")
hit_sound.set_volume(0.3)
point_sound = pygame.mixer.Sound("audio/point.ogg")
point_sound.set_volume(0.3)
swoosh_sound = pygame.mixer.Sound("audio/swoosh.ogg")
swoosh_sound.set_volume(0.3)
wing_sound = pygame.mixer.Sound("audio/wing.ogg")
wing_sound.set_volume(0.3)


# Sprites and groups
all_sprites = pygame.sprite.Group()
pipe_sprites = pygame.sprite.Group()
background = Background(all_sprites)
bird = Bird(all_sprites)

# Pipe event
pipe_event = pygame.event.custom_type()
pygame.time.set_timer(pipe_event, 1250)

# Game loop
while running:
    dt = Clock.tick(60) / 1000

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "start":
            # Start game on SPACE or UP key
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                game_state = "play"
                bird.rect.center = (120, WINDOW_HEIGHT / 2)  # Reset bird position
                pipe_sprites.empty()  # Clear pipes
                scroll_speed = 4  # Reset scroll speed
                game_active = True
                falling = False  # Reset falling state

        elif game_state == "game_over":
            # Return to start screen on any key press
            if event.type == pygame.KEYDOWN:
                game_state = "start"
                bird.rect.center = (120, WINDOW_HEIGHT / 2)  # Reset bird position after game over
                pipe_sprites.empty()  # Clear pipes
                scroll_speed = 4  # Reset scroll speed
                falling = False  # Reset falling state

        elif game_state == "play" and event.type == pipe_event:
            # Add pipes during gameplay
            bottom_pipe_height = randint(200, 480)
            Pipe(pipe_down, (WINDOW_WIDTH + 100, bottom_pipe_height), [all_sprites, pipe_sprites])

            top_pipe_height = bottom_pipe_height - randint(125, 175)
            UpPipe(pipe_up, (WINDOW_WIDTH + 100, top_pipe_height), [all_sprites, pipe_sprites])

    # Update game logic
    if game_state == "play":
        if game_active:
            all_sprites.update(dt)
            pipe_sprites.update(dt)
            collisions()
        else:
            # Handle game over falling logic
            bird.rect.y += int(150 * dt)  # Continue falling after game over
            if bird.rect.bottom >= WINDOW_HEIGHT - BASE_HEIGHT:
                bird.rect.bottom = WINDOW_HEIGHT - BASE_HEIGHT

    # Draw appropriate screen
    display_surface.fill((0, 0, 0))  # Clear the screen

    if game_state == "start":
        # Draw the start screen
        display_surface.blit(background_day, (0, 0))
        display_surface.blit(base, (0, 480))
        display_surface.blit(start_screen, start_screen_rect)

    elif game_state == "play":
        # Draw the main game
        all_sprites.draw(display_surface)
        pipe_sprites.draw(display_surface)
        display_surface.blit(base, (ground_scroll, 480))
        ground_scroll -= scroll_speed
        if abs(ground_scroll) >= 30:
            ground_scroll = 0

    elif game_state == "game_over":
        # Draw "Game Over" screen
        all_sprites.draw(display_surface)
        pipe_sprites.draw(display_surface)
        display_surface.blit(base, (ground_scroll, 480))
        display_surface.blit(game_over, game_over_rect)

    pygame.display.update()

pygame.quit()
