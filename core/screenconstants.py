import pygame
from pylygon import Polygon


pygame.display.init()
SCREEN_W = w = pygame.display.Info().current_w
SCREEN_H = h = pygame.display.Info().current_h
SCREEN_RECT = Polygon([(0, 0), (w, 0), (w, h), (0, h)])
