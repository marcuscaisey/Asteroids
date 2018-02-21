import pygame.freetype

from ..helpers import find_asset
from ..screenconstants import SCREEN_H
from .ships import Ship


WHITE = (255, 255, 255)

FONT_PATH = find_asset('fonts\Hyperspace.otf')

PADDING = 0.02 * SCREEN_H
SCORE_SIZE = 0.06 * SCREEN_H
ICON_LENGTH = 0.045 * SCREEN_H


class HUD:
    """HUD object which displays score and number of lives ship has."""
    def __init__(self):
        pygame.freetype.init()
        self.font = pygame.freetype.Font(FONT_PATH, SCORE_SIZE)
        # life icon is just a ship object which only gets drawn
        self.icon = Ship(ICON_LENGTH, self.icon_centre())

    def icon_centre(self):
        """Return centre for life icon."""
        # This aligns icon horizontally with score
        x = 0.36 * ICON_LENGTH
        # This moves icon below score
        score_height = self.font.get_rect('0', size=SCORE_SIZE).height
        y = 0.67 * ICON_LENGTH + score_height + 0.015 * SCREEN_H
        return (x, y)

    def draw(self, surface, score, lives):
        """Draw HUD to surface."""
        self.font.render_to(surface, (PADDING, PADDING), str(score), WHITE)
        for i in range(lives):
            self.icon.move(PADDING + i * ICON_LENGTH, PADDING).draw(surface)
