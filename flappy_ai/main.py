import pygame
import sys
import math
from flappy_ai.assets import load_assets
from flappy_ai.bird import Bird
from flappy_ai.pipe import Pipe
from flappy_ai.base import Base
from flappy_ai.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BASE_HEIGHT,
    PIPE_DISTANCE, PIPE_START_X, BIRD_START_X, BIRD_START_Y,
)

# ── init ─────────────────────────────────────────────────────────────────────

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

assets = load_assets()

# Night transition score threshold
NIGHT_SCORE = 15

# ── font setup (robust fallback) ─────────────────────────────────────────────

def make_font(size, bold=False):
    """Try system fonts, fall back to default."""
    for name in ["Helvetica", "Arial", "DejaVu Sans", None]:
        try:
            if name:
                f = pygame.font.SysFont(name, size, bold=bold)
            else:
                f = pygame.font.Font(None, size)
            return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_big   = make_font(36, bold=True)
font_med   = make_font(22, bold=True)
font_small = make_font(18)

# ── helpers ──────────────────────────────────────────────────────────────────

def get_background(score):
    """Cross-fade from day to night as score approaches NIGHT_SCORE."""
    if score >= NIGHT_SCORE:
        return assets["bg_night"]
    if score <= 0:
        return assets["bg_day"]
    # Smooth blend
    alpha = int(255 * score / NIGHT_SCORE)
    day   = assets["bg_day"].copy()
    night = assets["bg_night"].copy()
    night.set_alpha(alpha)
    day.blit(night, (0, 0))
    return day


def draw_score(surface, score, digit_imgs, y=20):
    digits  = str(score)
    total_w = sum(digit_imgs[d].get_width() for d in digits)
    x       = (WINDOW_WIDTH - total_w) // 2
    for d in digits:
        surface.blit(digit_imgs[d], (x, y))
        x += digit_imgs[d].get_width()


def draw_scene(surface, bg, pipes, base, bird, score):
    """Draw the full game scene (background → pipes → base → bird → score)."""
    surface.blit(bg, (0, 0))
    for pipe in pipes:
        pipe.draw(surface)
    base.draw(surface)
    surface.blit(bird.image, bird.rect)
    draw_score(surface, score, assets["digits"])


def reset_game():
    bird  = Bird(BIRD_START_X, BIRD_START_Y, assets["bird"])
    base  = Base(assets["base"], WINDOW_HEIGHT - BASE_HEIGHT)
    pipes = []
    return bird, base, pipes, 0, 3.5   # score, pipe_speed (slightly slower start)


# ── start screen ─────────────────────────────────────────────────────────────

def start_screen(surface):
    """Show the message.png splash and wait for SPACE.  Returns False to quit."""
    msg_img  = assets["message"]
    msg_rect = msg_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))

    bird   = Bird(BIRD_START_X, BIRD_START_Y, assets["bird"])
    base   = Base(assets["base"], WINDOW_HEIGHT - BASE_HEIGHT)
    bg     = assets["bg_day"]
    bob    = 0      # animation counter for gentle bird bob

    assets["sounds"]["swoosh"].play()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        # Gentle bird bobbing
        bob += 1
        bob_offset = int(math.sin(bob * 0.08) * 8)

        base.update(2)

        surface.blit(bg, (0, 0))
        base.draw(surface)
        surface.blit(msg_img, msg_rect)

        # Bob the bird next to the message
        bird_img = bird.images[bird.index]
        if bob % 8 == 0:
            bird.index = (bird.index + 1) % len(bird.images)
        bx = WINDOW_WIDTH // 2
        by = WINDOW_HEIGHT // 2 - 80 + bob_offset
        surface.blit(bird_img, bird_img.get_rect(center=(bx, by)))

        pygame.display.update()


# ── game over screen ─────────────────────────────────────────────────────────

def game_over_screen(surface, bg, pipes, base, bird, score):
    """
    Death animation (bird tumbles down) → overlay with score & controls.
    Returns True to restart, False to quit.
    """
    # ── death tumble animation ───────────────────────────────────────────────
    assets["sounds"]["hit"].play()
    fall_vel = 0
    for _ in range(40):
        clock.tick(60)
        # Drain events so window stays responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        fall_vel = min(fall_vel + 0.8, 12)
        bird.rect.centery += int(fall_vel)
        bird.angle = max(bird.angle - 6, -90)
        base_img = bird.images[bird.index]
        bird.image = pygame.transform.rotate(base_img, bird.angle)
        bird.rect  = bird.image.get_rect(center=bird.rect.center)

        if bird.rect.centery >= WINDOW_HEIGHT - BASE_HEIGHT - 10:
            bird.rect.centery = WINDOW_HEIGHT - BASE_HEIGHT - 10
            break

        draw_scene(surface, bg, pipes, base, bird, score)
        pygame.display.update()

    assets["sounds"]["die"].play()
    pygame.time.wait(300)

    # ── static game-over overlay ─────────────────────────────────────────────
    # Dark overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))

    # Game Over image
    go_img   = assets["game_over"]
    go_rect  = go_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))

    # Score panel
    score_txt  = font_big.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10))

    # Control hints
    retry_txt  = font_med.render("Press  R  to Retry", True, (255, 220, 100))
    retry_rect = retry_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))

    quit_txt   = font_small.render("ESC to Quit", True, (200, 200, 200))
    quit_rect  = quit_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 85))

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    assets["sounds"]["swoosh"].play()
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        # Redraw scene underneath
        draw_scene(surface, bg, pipes, base, bird, score)
        surface.blit(overlay, (0, 0))
        surface.blit(go_img, go_rect)
        surface.blit(score_txt, score_rect)
        surface.blit(retry_txt, retry_rect)
        surface.blit(quit_txt, quit_rect)
        pygame.display.update()


# ── main loop ────────────────────────────────────────────────────────────────

def main():
    running = True

    while running:
        # ── start screen ─────────────────────────────────────────────────────
        if not start_screen(screen):
            break

        bird, base, pipes, score, pipe_speed = reset_game()
        assets["sounds"]["wing"].play()
        bird.jump()

        alive = True
        while alive and running:
            clock.tick(60)

            # ── events ───────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    assets["sounds"]["wing"].play()
                    bird.jump()

            # ── update ───────────────────────────────────────────────────────
            bird.update()
            base.update(pipe_speed)

            # Spawn pipes
            if not pipes or pipes[-1].rect.x < WINDOW_WIDTH - PIPE_DISTANCE:
                pipes.append(Pipe(assets["pipe"], PIPE_START_X))

            scored_this_frame = False
            pipes_to_remove   = []
            for pipe in pipes:
                pipe.rect.x     -= pipe_speed
                pipe.top_rect.x -= pipe_speed

                if not pipe.passed and pipe.rect.x + pipe.rect.width < bird.rect.left:
                    pipe.passed       = True
                    scored_this_frame = True

                if pipe.rect.right < 0:
                    pipes_to_remove.append(pipe)

            for p in pipes_to_remove:
                pipes.remove(p)

            if scored_this_frame:
                score += 1
                assets["sounds"]["point"].play()
                # Gradual speed increase
                if score % 10 == 0:
                    pipe_speed += 0.5

            # ── collision ────────────────────────────────────────────────────
            dead = False
            for pipe in pipes:
                if (bird.rect.colliderect(pipe.top_rect) or
                    bird.rect.colliderect(pipe.bottom_rect)):
                    dead = True
                    break

            if bird.rect.bottom >= WINDOW_HEIGHT - BASE_HEIGHT or bird.rect.top <= 0:
                dead = True

            # ── draw ─────────────────────────────────────────────────────────
            bg = get_background(score)
            draw_scene(screen, bg, pipes, base, bird, score)
            pygame.display.update()

            # ── death → game over ────────────────────────────────────────────
            if dead:
                alive = False
                restart = game_over_screen(screen, bg, pipes, base, bird, score)
                if not restart:
                    running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
