import pygame
from pylygon import Polygon


pygame.display.init()
WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h
AREA = Polygon([(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)])
