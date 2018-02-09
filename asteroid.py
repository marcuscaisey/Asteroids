from __future__ import division
import pygame
from polygon import BasePolygon
from pygame.math import Vector2
from random import randint

pygame.display.init()
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h

WHITE = (255, 255, 255)

MAX_CENTRE_X, MAX_CENTRE_Y = screen_width, screen_height
MIN_SIDES = 10
# Controls how much radius of asteroid points can vary
RADIUS_CONSTANT = screen_height // 120
MIN_SPEED = 0.08 * screen_height
MAX_SPEED = 0.18 * screen_height
# Asteroid size to Radius conversion
RADIUS = {
    3: 0.08 * screen_height,  # Large
    2: 0.04 * screen_height,  # Medium
    1: 0.02 * screen_height,  # Small
}


class Asteroid(BasePolygon):
    """Asteroid object."""

    def __init__(self, centre=None, size=3):
        self.size = size
        self.velocity = self.random_velocity()
        super(Asteroid, self).__init__(self.random_points(centre), False)

    def initial_centre(self):
        """Return random position near edge of screen."""
        x = randint(0, MAX_CENTRE_X)
        y = randint(0, MAX_CENTRE_Y)
        while 0.25 < x / MAX_CENTRE_X < 0.75:
            x = randint(0, MAX_CENTRE_X)
        while 0.25 < y / MAX_CENTRE_Y < 0.75:
            y = randint(0, MAX_CENTRE_Y)
        return (x, y)

    def random_points(self, centre=None):
        """Return list of random points about centre."""
        centre = self.initial_centre() if centre is None else centre
        dr = RADIUS[self.size] // RADIUS_CONSTANT
        points = []
        theta = 0
        while theta < 360:
            r = RADIUS[self.size] + randint(-dr, dr)
            points.append(centre + Vector2(r, 0).rotate(theta))
            theta += randint(1, 360 / MIN_SIDES)
        return points

    def random_velocity(self):
        """
        Return random velocity with speed depending linearly on radius.
        """
        x1, y1 = RADIUS[1], MAX_SPEED
        x2, y2 = RADIUS[3], MIN_SPEED
        speed = (y2 - y1) / (x2 - x1) * (RADIUS[self.size] - x1) + y1
        return speed * Vector2(1, 0).rotate(randint(0, 359))

    def split(self):
        """Return two asteroids of next size."""
        return [Asteroid(self.C, self.size - 1) for _ in range(2)]

    def update(self, screen_area, dt):
        """Update asteroid by dt seconds."""
        self.move_ip(*self.velocity * dt)
        self.wrap(screen_area)

    def draw(self, surface):
        """Draw asteroid to surface."""
        pygame.draw.aalines(surface, WHITE, True, self.P)
