import pygame
from flappy_ai.config import BASE_DIR, WINDOW_WIDTH, WINDOW_HEIGHT

def load_assets():
    idir = BASE_DIR / "images"
    adir = BASE_DIR / "audio"

    def img(name):
        return pygame.image.load(str(idir / name)).convert_alpha()

    def imgb(name):
        return pygame.image.load(str(idir / name)).convert()

    bird_images = [
        img("bluebird-downflap.png"),
        img("bluebird-midflap.png"),
        img("bluebird-upflap.png"),
    ]
    bg_day   = pygame.transform.scale(imgb("background-day.png"),   (WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_night = pygame.transform.scale(imgb("background-night.png"), (WINDOW_WIDTH, WINDOW_HEIGHT))
    base_raw = img("base.png")
    base_img = pygame.transform.scale(base_raw, (WINDOW_WIDTH, base_raw.get_height()))
    pipe_img = img("pipe-green.png")

    # Digits live in images/numbers/
    digit_images = {}
    for i in range(10):
        digit_images[str(i)] = pygame.image.load(
            str(idir / "numbers" / f"{i}.png")
        ).convert_alpha()

    game_over_img = img("gameover.png")
    message_img   = img("message.png")

    def snd(name):
        return pygame.mixer.Sound(str(adir / name))

    point_sound  = snd("point.ogg")
    hit_sound    = snd("hit.ogg")
    wing_sound   = snd("wing.ogg")
    die_sound    = snd("die.ogg")
    swoosh_sound = snd("swoosh.ogg")

    return {
        "bird":        bird_images,
        "bg_day":      bg_day,
        "bg_night":    bg_night,
        "background":  bg_day,       # default
        "base":        base_img,
        "pipe":        pipe_img,
        "digits":      digit_images,
        "game_over":   game_over_img,
        "message":     message_img,
        "sounds": {
            "point":  point_sound,
            "hit":    hit_sound,
            "wing":   wing_sound,
            "die":    die_sound,
            "swoosh": swoosh_sound,
        },
    }
