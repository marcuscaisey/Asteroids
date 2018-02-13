import pygame.freetype

from ship import Ship
from screen_constants import HEIGHT

WHITE = (255, 255, 255)

PADDING = 0.02 * HEIGHT  # Padding of HUD from corner of screen
SCORE_SIZE = 0.06 * HEIGHT
ICON_LENGTH = 0.045 * HEIGHT


class HUD:
    """HUD object which displays score and number of lives ship has"""
    def __init__(self):
        pygame.freetype.init()
        self.font = pygame.freetype.Font('Hyperspace.otf', SCORE_SIZE)
        self.icon = Ship(ICON_LENGTH, self.icon_centre())

    def icon_centre(self):
        text_height = self.font.get_rect('0', size=SCORE_SIZE).height
        x = 0.36 * ICON_LENGTH
        y = 0.67 * ICON_LENGTH + text_height + 0.015 * HEIGHT
        return (x, y)

    def draw(self, surface, score, lives):
        """Draw HUD to surface."""
        self.font.render_to(surface, (PADDING, PADDING), str(score), WHITE)
        for i in range(lives):
            self.icon.move(PADDING + i * ICON_LENGTH, PADDING).draw(surface)
