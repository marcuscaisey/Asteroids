import pygame
from pylygon import Polygon


pygame.display.init()
W = pygame.display.Info().current_w
H = pygame.display.Info().current_h
SCREEN_AREA = Polygon([(0, 0), (W, 0), (W, H), (0, H)])

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
