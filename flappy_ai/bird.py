import pygame

class Bird(pygame.sprite.Sprite):
    ANIM_SPEED   = 5     # frames between wing flaps
    MAX_FALL_VEL = 10    # terminal velocity
    GRAVITY      = 0.4   # gentler than before (was 0.5)
    LIFT         = -7.5  # softer jump (was -10)
    MAX_UP_ANGLE = 25    # degrees tilt up after flap
    MAX_DN_ANGLE = -70   # degrees tilt down at terminal fall
    ROT_SPEED    = 3     # how fast the bird rotates down per frame

    def __init__(self, x, y, images):
        super().__init__()
        self.images   = images
        self.index    = 0
        self.image    = self.images[self.index]
        self.rect     = self.image.get_rect(center=(x, y))
        self.velocity = 0.0
        self.angle    = 0.0
        self.tick     = 0

    def update(self):
        # Physics — float precision for smooth sub-pixel movement
        self.velocity = min(self.velocity + self.GRAVITY, self.MAX_FALL_VEL)
        self.rect.centery += int(self.velocity)

        # Wing animation
        self.tick += 1
        if self.tick % self.ANIM_SPEED == 0:
            self.index = (self.index + 1) % len(self.images)

        # Smooth rotation: tilt up on jump, gradually tilt down while falling
        if self.velocity < 0:
            self.angle = self.MAX_UP_ANGLE   # snap up on rise
        else:
            # Gradually rotate downward
            self.angle = max(self.angle - self.ROT_SPEED, self.MAX_DN_ANGLE)

        base  = self.images[self.index]
        self.image = pygame.transform.rotate(base, self.angle)
        self.rect  = self.image.get_rect(center=self.rect.center)

    def jump(self):
        self.velocity = self.LIFT
        self.angle    = self.MAX_UP_ANGLE
