from __future__ import division
from math import radians
from random import randint

import pygame
from pygame.math import Vector2

from .basepolygon import BasePolygon
from ..screenconstants import SCREEN_W, SCREEN_H, SCREEN_RECT


WHITE = (255, 255, 255)

# SHIP CONSTANTS
SHIP_LENGTH = 0.07 * SCREEN_H
SHIP_BOOST_FORCE = 0.55 * SCREEN_H
INITIAL_CENTRE = (SCREEN_W / 2, SCREEN_H / 2)
SHIP_ROTATE_SPEED = 0.8  # Full rotations per second
SHIP_INVINCIBLE_TIME = 2  # Number of seconds ship will be invincible for
SHIP_INVINCIBLE_FLICKER_RATE = 12  # Flickers per second when invincible

# SAUCER CONSTANTS
SAUCER_SMALL_SPEED = 0.15 * SCREEN_W
SAUCER_LARGE_SPEED = 0.12 * SCREEN_W
SAUCER_SMALL_HEIGHT = 0.03 * SCREEN_H
SAUCER_LARGE_HEIGHT = 0.06 * SCREEN_H
SAUCER_SMALL_INACCURACY = 20
SAUCER_LARGE_INACCURACY = 50
SAUCER_FIRE_RATE = 0.5  # Shots per second

# BULLET CONSTANTS
BULLET_SPEED = 0.8 * SCREEN_H
BULLET_RADIUS = SCREEN_H // 300
BULLET_LIFESPAN = 0.9  # Duration in seconds until bullet fades


class Ship(BasePolygon):
    """Main ship object which is controlled by player."""

    def __init__(self, length=SHIP_LENGTH, initial_centre=INITIAL_CENTRE):
        self.length = length
        self.rear_length = 0.75 * length
        self.flame_length = 0.25 * length
        self.flame_width = 0.125 * length
        self.initial_centre = initial_centre
        self.rotate_direction = 0  # left = -1, 0 = none,  right = 1
        self.boosting = False
        self.spawn()

    def spawn(self):
        """Spawn ship at initial centre."""
        super(Ship, self).__init__(self.initial_points(), False)
        self.C = self.initial_centre
        self.direction = Vector2(0, -1)
        self.velocity = Vector2(0, 0)
        self.invincible = True
        self.invincible_duration = 0
        self.fired_bullets = []

    def initial_points(self):
        """Return initial points of ship at origin."""
        return [
            (-0.36 * self.length, self.length),
            (-0.36 * self.rear_length, self.rear_length),
            (0, 0),  # Nose
            (0.36 * self.rear_length, self.rear_length),
            (0.36 * self.length, self.length),
            ]

    def move(self, x, y):
        """Return a new ship moved by (x, y)."""
        return Ship(self.length, self.C + (x, y))

    def rotate(self, theta):
        """Rotate ship by theta degrees clockwise."""
        self.direction.rotate_ip(theta)
        self.rotate_ip(radians(theta))

    def shoot(self):
        """Shoot bullet, from nose, in direction ship is facing."""
        self.fired_bullets.append(Bullet(self.P[2], self.direction))

    def hits(self, other):
        """Return True if ship hits other and ship is not invincible."""
        return super(Ship, self).hits(other) and not self.invincible

    def shoots(self, other):
        """
        Return True if one of ships bullets hits other and removes that
        bullet from fired_bullets.
        """
        for bullet in reversed(self.fired_bullets):
            if bullet.hits(other):
                self.fired_bullets.remove(bullet)
                return True
        return False

    def update(self, dt):
        """Update ship and fired bullets by dt seconds."""
        if self.invincible:
            self.invincible_duration += dt
            if self.invincible_duration > SHIP_INVINCIBLE_TIME:
                self.invincible_duration = 0
                self.invincible = False

        self.rotate(SHIP_ROTATE_SPEED * 360 * dt * self.rotate_direction)
        if self.boosting:
            self.velocity += SHIP_BOOST_FORCE * self.direction * dt
        self.velocity = self.velocity.lerp((0, 0), 0.01)
        self.move_ip(*(self.velocity * dt))
        self.wrap()

        for bullet in reversed(self.fired_bullets):
            if bullet.faded:
                self.fired_bullets.remove(bullet)
            else:
                bullet.update(dt)

    def flame_points(self):
        """Return points for ships boost flame."""
        origin = self.P[2] - (self.rear_length * self.direction)
        return [
            origin - self.flame_width * self.direction.rotate(90),
            origin - self.flame_length * self.direction,
            origin + self.flame_width * self.direction.rotate(90),
        ]

    def draw(self, surface):
        """Draw ship (and its boost flame) to surface."""
        # If invincible, ship should flicker INVINCIBLE_FLICKER_RATE (n) times
        # per second. So split each second into intervals of width 1/n (w).
        # Want ship to not be drawn every other w seconds, so floor divide
        # invincible_duration by W and if result is odd then don't draw
        w = 1 / SHIP_INVINCIBLE_FLICKER_RATE
        if not self.invincible or (self.invincible_duration // w) % 2 == 0:
            # Line joining points on opposite sides of ship
            pygame.draw.aalines(surface, WHITE, False, [self.P[1], self.P[3]])
            pygame.draw.aalines(surface, WHITE, False, self.P)
            if self.boosting:
                pygame.draw.aalines(surface, WHITE, False, self.flame_points())

        for bullet in self.fired_bullets:
            bullet.draw(surface)


class Saucer(BasePolygon):
    """Saucer object which shoots bullets at main ship."""

    def __init__(self, size):
        self.size = size  # 1 = small, 2 = large
        self.height = SAUCER_SMALL_HEIGHT if size == 1 else SAUCER_LARGE_HEIGHT
        self.width = 2.3 * self.height
        self.speed = SAUCER_SMALL_SPEED if size == 1 else SAUCER_LARGE_SPEED
        self.direction = 2 * randint(0, 1) - 1  # -1 = left, 1 = right
        self.shot_timer = 0
        self.fired_bullets = []
        super(Saucer, self).__init__(self.initial_points(), False)

    def initial_points(self):
        """Return initial points of saucer at origin."""
        y = randint(2 * self.height // 3, SCREEN_H - self.height // 3)
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
        theta = Vector2(*(ship.C - source)).as_polar()[1]
        if self.size == 1:
            theta += randint(-SAUCER_SMALL_INACCURACY, SAUCER_SMALL_INACCURACY)
        elif self.size == 2:
            theta += randint(-SAUCER_LARGE_INACCURACY, SAUCER_LARGE_INACCURACY)
        # Need to wrap theta after adding offset so that saucer doesn't
        # shoot through itself
        if source_index == 0:  # left
            theta_min = 90
            theta_max = 270
        elif source_index == 2:  # bottom
            theta_min = 0
            theta_max = 180
        elif source_index == 4:  # right
            theta_min = -90
            theta_max = 90
        elif source_index == 7:  # top
            theta_min = -180
            theta_max = 0
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
        # Test whether centre of saucer is off screen first, since it's costly
        # to call hits method
        if not 0 <= self.C[0] <= SCREEN_W:
            if not self.hits(SCREEN_RECT):
                if self.C[0] < 0 and self.direction == -1:
                    self.C = (SCREEN_W + self.width / 2, self.C[1])
                elif self.C[0] > SCREEN_W and self.direction == 1:
                    self.C = (0 - self.width / 2, self.C[1])

    def update(self, ship, dt):
        """Update saucer by dt seconds."""
        self.move_ip(self.speed * self.direction * dt, 0)
        self.wrap()

        self.shot_timer += dt
        if self.shot_timer > 1 / SAUCER_FIRE_RATE:
            self.shot_timer %= 1 / SAUCER_FIRE_RATE
            self.shoot(ship)

        for bullet in reversed(self.fired_bullets):
            if bullet.faded:
                self.fired_bullets.remove(bullet)
            else:
                bullet.update(dt)

    def draw(self, surface):
        """Draw saucer to surface."""
        pygame.draw.aalines(surface, WHITE, True, self.P)
        # Lines joining points on opposite sides of saucer
        pygame.draw.aalines(surface, WHITE, False, [self.P[0], self.P[4]])
        pygame.draw.aalines(surface, WHITE, False, [self.P[5], self.P[9]])

        for bullet in self.fired_bullets:
            bullet.draw(surface)


class Bullet(Vector2):
    """Bullet object."""

    def __init__(self, source, direction):
        self.centre = Vector2(*source)
        self.velocity = BULLET_SPEED * direction
        self.duration = 0
        self.faded = False

    def hits(self, other):
        """Return True if bullet hits other polygon."""
        return other.collidepoint(self.centre) != 0

    def wrap(self):
        """
        Wrap bullet to opposite side of screen if it leaves screen area.
        """
        # Test whether centre is off screen first, since it's costly
        # to call hits method
        if not (0 <= self.centre <= SCREEN_W and 0 <= self.centre <= SCREEN_H):
            if not self.hits(SCREEN_RECT):
                if ((self.centre.x < 0 and self.velocity.x < 0)
                   or (self.centre.x > SCREEN_W and self.velocity.x > 0)):
                    self.centre.x = SCREEN_W - self.centre.x
                elif ((self.centre.y < 0 and self.velocity.y < 0)
                      or (self.centre.y > SCREEN_H and self.velocity.y > 0)):
                    self.centre.y = SCREEN_H - self.centre.y

    def update(self, dt):
        """Update bullet by dt seconds."""
        if self.duration < BULLET_LIFESPAN:
            self.duration += dt
            self.centre += self.velocity * dt
            self.wrap()
        else:
            self.faded = True

    def draw(self, surface):
        """Draw bullet to surface."""
        # draw.circle takes only integer arguments for centre position
        int_centre = map(int, map(round, self.centre))
        pygame.draw.circle(surface, WHITE, int_centre, BULLET_RADIUS)
