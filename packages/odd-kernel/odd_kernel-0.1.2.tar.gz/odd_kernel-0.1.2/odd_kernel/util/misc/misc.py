import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame


def ding():
    asset_path = os.path.join(os.path.dirname(__file__), "assets", "ding.wav")
    pygame.init()
    pygame.mixer.music.load(asset_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.quit()