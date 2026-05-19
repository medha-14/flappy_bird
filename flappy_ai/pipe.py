import pygame
import random
from flappy_ai.config import WINDOW_HEIGHT, BASE_HEIGHT, PIPE_GAP

class Pipe(pygame.sprite.Sprite):
    """
    A pipe pair (top + bottom).  The sprite image is the bottom pipe;
    top_rect and bottom_rect are used for collision and drawing.
    """
    MIN_PIPE_HEIGHT = 50   # minimum visible pipe height on screen

    def __init__(self, pipe_img, x):
        super().__init__()

        # gap_y = top edge of the bottom pipe
        # Ensure top pipe is at least MIN_PIPE_HEIGHT visible at top of screen:
        #   top_pipe_bottom = gap_y - PIPE_GAP  >=  MIN_PIPE_HEIGHT
        #   => gap_y >= MIN_PIPE_HEIGHT + PIPE_GAP
        # Ensure bottom pipe is at least MIN_PIPE_HEIGHT visible above the base:
        #   gap_y <= WINDOW_HEIGHT - BASE_HEIGHT - MIN_PIPE_HEIGHT
        min_gap_y = self.MIN_PIPE_HEIGHT + PIPE_GAP
        max_gap_y = WINDOW_HEIGHT - BASE_HEIGHT - self.MIN_PIPE_HEIGHT
        gap_y = random.randint(min_gap_y, max_gap_y)

        # ---- Bottom pipe (original image, top-left at gap_y) ----
        self.image = pipe_img
        self.rect  = self.image.get_rect(topleft=(x, gap_y))

        # ---- Top pipe (flipped image, bottom at gap_y - PIPE_GAP) ----
        self.top_image = pygame.transform.flip(pipe_img, False, True)
        self.top_rect  = self.top_image.get_rect(midbottom=(x + pipe_img.get_width() // 2,
                                                             gap_y - PIPE_GAP))

        # Alias so collision code can use either name
        self.bottom_rect = self.rect

        self.passed = False

    def draw(self, surface):
        """Draw both pipe halves onto surface."""
        surface.blit(self.top_image, self.top_rect)
        surface.blit(self.image,     self.rect)
