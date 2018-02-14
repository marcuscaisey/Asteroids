from __future__ import division
from random import randint

import pygame
from pygame.math import Vector2

from base_polygon import BasePolygon
from bullet import Bullet
from screen_constants import WIDTH, HEIGHT, AREA


WHITE = (255, 255, 255)

SMALL_SPEED = 0.15 * WIDTH
LARGE_SPEED = 0.12 * WIDTH
SMALL_HEIGHT = 0.03 * HEIGHT
LARGE_HEIGHT = 0.06 * HEIGHT
# Largest angle that small/large saucer can miss ship by when shooting
SMALL_INACCURACY = 20
LARGE_INACCURACY = 50
FIRE_RATE = 0.5  # Shots per second


class Saucer(BasePolygon):
    """Saucer object which shoots bullets."""

    def __init__(self, size):
        self.size = size  # 1 = small, 2 = large
        self.height = SMALL_HEIGHT if size == 1 else LARGE_HEIGHT
        self.width = 2.3 * self.height
        self.speed = SMALL_SPEED if size == 1 else LARGE_SPEED
        self.direction = 2 * randint(0, 1) - 1  # -1 = left, 1 = right
        self.shot_timer = 0
        self.fired_bullets = []
        super(Saucer, self).__init__(self.initial_points(), False)

    def initial_points(self):
        """Return initial points of saucer at origin."""
        y = randint(2 * self.height // 3, HEIGHT - self.height // 3)
        points_at_origin = [
            (0, 0),  # left
            (0.25 * self.width, self.height / 3),
            (0.5 * self.width, self.height / 3),  # bottom
            (0.75 * self.width, self.height / 3),
            (self.width, 0),  # right
            (0.75 * self.width, -self.height / 3),
            (0.625 * self.width, -2 * self.height / 3),
            (0.5 * self.width, -2 * self.height / 3),  # top
            (0.375 * self.width, -2 * self.height / 3),
            (0.25 * self.width, -self.height / 3),
        ]
        return [Vector2(-self.width, y) + point for point in points_at_origin]

    def wrap_int(self, n, a, b):
        """
        Wraps int n in interval [a, b].

        i.e. for [5, 10]: 12 gets wrapped to 7 since it's 2 greater than 10
        """
        return a + (n - a) % (b - a)

    def aim_at(self, source_index, ship):
        """
        Return direction from source to ship, offset by angle depending
        on size of saucer.
        """
        source = self.P[source_index]
        # Angle to ship from source point on saucer
        inaccuracy = SMALL_INACCURACY if self.size == 1 else LARGE_INACCURACY
        theta = Vector2(*(ship.C - source)).as_polar()[1]
        theta += randint(-inaccuracy, inaccuracy)
        # Need to wrap theta after adding offset so that saucer doesn't
        # shoot through itself
        if source_index == 0:  # left
            theta_min, theta_max = 90, 270
        elif source_index == 2:  # bottom
            theta_min, theta_max = 0, 180
        elif source_index == 4:  # right
            theta_min, theta_max = -90, 90
        elif source_index == 7:  # top
            theta_min, theta_max = -180, 0
        return Vector2(1, 0).rotate(self.wrap_int(theta, theta_min, theta_max))

    def shoot(self, ship):
        """
        Shoot bullet at ship, accuracy depending on size of saucer.
        """
        # If centre of ship is between top and bottom of saucer, shoot from
        # left or right of saucer, else shoot from top or bottom
        if self.P[7][1] <= ship.C[1] <= self.P[2][1]:
            source_index = 0 if ship.C[0] < self.P[0][0] else 4
        else:
            source_index = 7 if ship.C[1] < self.P[7][1] else 2
        source = self.P[source_index]
        bullet_direction = self.aim_at(source_index, ship)
        self.fired_bullets.append(Bullet(source, bullet_direction))

    def shoots(self, other):
        """
        Return True if one of saucers bullets hits other and removes
        that bullet from fired_bullets.
        """
        for bullet in reversed(self.fired_bullets):
            if bullet.hits(other):
                self.fired_bullets.remove(bullet)
                return True
        return False

    def wrap(self):
        """
        Wrap saucer to opposite side of screen if it leaves screen area.
        """
        if not self.hits(AREA):
            if self.C[0] < 0 and self.direction == -1:
                self.C = (WIDTH + self.width / 2, self.C[1])
            elif self.C[0] > WIDTH and self.direction == 1:
                self.C = (0 - self.width / 2, self.C[1])

    def update(self, ship, dt):
        """Update saucer by dt seconds."""
        self.move_ip(self.speed * self.direction * dt, 0)
        self.wrap()

        self.shot_timer += dt
        if self.shot_timer > 1 / FIRE_RATE:
            self.shot_timer %= 1 / FIRE_RATE
            self.shoot(ship)

        for bullet in reversed(self.fired_bullets):
            if bullet.faded:
                self.fired_bullets.remove(bullet)
            else:
                bullet.update(dt)

    def draw(self, surface):
        """Draw saucer to surface."""
        pygame.draw.aalines(surface, WHITE, True, self.P)
        pygame.draw.aalines(surface, WHITE, False, [self.P[0], self.P[4]])
        pygame.draw.aalines(surface, WHITE, False, [self.P[5], self.P[9]])

        for bullet in self.fired_bullets:
            bullet.draw(surface)
