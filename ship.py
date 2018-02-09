from __future__ import division
import pygame
from polygon import BasePolygon
from bullet import Bullet
from pygame.math import Vector2
from math import radians

# COLOURS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Ship(BasePolygon):
    """Ship object."""

    @classmethod
    def initialise_constants(cls, screen_width, screen_height):
        """
        Initialise constants for Ship which depend on the dimensions of
        the screen.
        """
        cls.LENGTH = 0.07 * screen_height
        cls.INITIAL_POSITION = Vector2(screen_width / 2, screen_height / 2)
        cls.BOOST_FORCE = 0.5 * screen_height
        # Speed in full rotations per second
        cls.ROTATE_SPEED = 0.8
        # Number of seconds that ship will be invincible for when invincible
        cls.INVINCIBLE_TIME = 2
        # Number of times ship flickers per second when invincible
        cls.INVINCIBLE_FLICKER_RATE = 12

    def __init__(self):
        super(Ship, self).__init__(self.main_points())
        self.direction = Vector2(0, -1)
        self.rotate_direction = 0  # left = -1, right = 1
        self.boosting = False
        self.velocity = Vector2(0, 0)
        self.invincible = False
        self.invincible_duration = 0
        self.fired_bullets = []

    def main_points(self):
        """
        Return initial points for main part of ship centred in middle of
        screen.
        """
        length, width = Ship.LENGTH, 0.36 * Ship.LENGTH
        points_at_origin = [(-width, length), (0, 0), (width, length)]
        return [Ship.INITIAL_POSITION + point for point in points_at_origin]

    def rotate(self, theta):
        """Rotate ship by theta degrees clockwise."""
        self.direction.rotate_ip(theta)
        self.rotate_ip(radians(theta))

    def update(self, screen_area, dt):
        """Update ship and fired bullets by dt seconds."""
        if self.invincible:
            self.invincible_duration += dt
            if self.invincible_duration > Ship.INVINCIBLE_TIME:
                self.invincible_duration = 0
                self.invincible = False

        self.rotate(Ship.ROTATE_SPEED * 360 * dt * self.rotate_direction)
        if self.boosting:
            self.velocity += Ship.BOOST_FORCE * self.direction * dt
        self.velocity = self.velocity.lerp((0, 0), 0.01)
        self.move_ip(*(self.velocity * dt))
        self.wrap(screen_area)

        for bullet in reversed(self.fired_bullets):
            if bullet.faded:
                self.fired_bullets.remove(bullet)
            else:
                bullet.update(screen_area, dt)

    def shoot_bullet(self):
        """Append new bullet to list of fired bullets."""
        # Bullets are fired from the nose of the ship
        self.fired_bullets.append(Bullet(self.P[1], self.direction))

    def hits(self, other):
        """Return True if ship hits other and ship is not invincible."""
        return super(Ship, self).hits(other) and not self.invincible

    def shoots(self, other):
        """
        Return True if one of ships bullets hits other and removes that
        bullet from fired_bullets
        """
        for bullet in reversed(self.fired_bullets):
            if bullet.hits(other):
                self.fired_bullets.remove(bullet)
                return True
        return False

    def rear_points(self):
        """Return points for rear of ship."""
        # Rear of the ship is a horizontal line 3/4 of the way down the ship
        rear_length, rear_width = 0.75 * Ship.LENGTH, 0.27 * Ship.LENGTH
        origin = self.P[1] - (rear_length * self.direction)
        return [
            origin - rear_width * self.direction.rotate(90),
            origin + rear_width * self.direction.rotate(90)
        ]

    def flame_points(self):
        """Return points for ship's boost flame."""
        rear_length = 0.75 * Ship.LENGTH
        flame_length, flame_width = 0.25 * Ship.LENGTH, 0.125 * Ship.LENGTH
        origin = self.P[1] - (rear_length * self.direction)
        return [
            origin - flame_width * self.direction.rotate(90),
            origin - flame_length * self.direction,
            origin + flame_width * self.direction.rotate(90),
        ]

    def draw(self, surface):
        """Draw ship and its boost flame if boosting."""
        # If invincible, ship should flicker INVINCIBLE_FLICKER_RATE (n) times
        # per second. So split each second into intervals of width 1/n (w).
        # Want ship to not be drawn every other w seconds, so floor divide
        # invincible_duration by W and if result is odd then don't draw ship.
        w = 1 / Ship.INVINCIBLE_FLICKER_RATE
        if not self.invincible or (self.invincible_duration // w) % 2 == 0:
            pygame.draw.aalines(surface, WHITE, False, self.P)
            pygame.draw.aalines(surface, WHITE, False, self.rear_points())
            if self.boosting:
                pygame.draw.aalines(surface, WHITE, False, self.flame_points())

        for bullet in self.fired_bullets:
            bullet.draw(surface)
