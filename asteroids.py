from __future__ import division
import pygame
import pygame.freetype
from pygame.math import Vector2
from pylygon import Polygon
from math import sin, cos, radians
from numpy import array, dot
from random import randint

# COLOURS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class BasePolygon(Polygon):
    """
    Base polygon class which includes some fixes to bugs in pylygon
    Polygon class.
    """

    # Default _rotate method uses 'if not origin:' to test if origin is None
    # which does not work for a numpy array as the truth value of a numpy array
    # with more than one element is ambiguous.
    def _rotate(self, x0, theta, origin=None):
        # Modified line from original code
        origin = self.C if origin is None else origin

        origin = origin.reshape(2, 1)
        x0 = x0.reshape(2, 1)
        x0 = x0 - origin  # assingment operator (-=) would modify original x0

        A = array([[cos(theta), -sin(theta)],  # rotation matrix
                   [sin(theta), cos(theta)]])

        return (dot(A, x0) + origin).ravel()

    # Default rotate_ip method creates new Polygon with points rotated
    # by theta. This changes the order of the points in self.P which makes
    # it more difficult to define which edges to draw.
    def rotate_ip(self, theta):
        self.P[:] = self.rotopoints(theta)
        self.edges[:] = self.rotoedges(theta)

    def hits(self, other):
        """Return true if self hits other polygon."""
        return self.collidepoly(other) is not False

    def wrap(self, screen_area):
        """
        Wrap polygon to opposite side of screen if polygon leaves
        screen area.
        """
        if self.collidepoly(screen_area) is False:
            # Width and height of screen area are both stored in third point of
            # screen_area
            width, height = screen_area.P[2][0], screen_area.P[2][1]

            # Polygon should only be wrapped if it's moving away from the edge
            # of the screen. Wrap by translating the polygon so that its
            # furthest point from the edge of the screen is now on the opposite
            # edge of the screen.
            if self.C[0] < 0 and self.velocity.x < 0:
                self.move_ip(width - min(self.P, key=lambda x: x[0])[0], 0)
            elif self.C[0] > width and self.velocity.x > 0:
                self.move_ip(-max(self.P, key=lambda x: x[0])[0], 0)
            elif self.C[1] < 0 and self.velocity.y < 0:
                self.move_ip(0, height - min(self.P, key=lambda x: x[1])[1])
            elif self.C[1] > height and self.velocity.y > 0:
                self.move_ip(0, -max(self.P, key=lambda x: x[1])[1])


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


class Bullet(Vector2):
    """Bullet object."""

    @classmethod
    def initialise_constants(cls, screen_height):
        """
        Initialise constants for Bullet which depend on the dimensions
        of the screen.
        """
        cls.SPEED = 0.8 * screen_height
        cls.RADIUS = screen_height // 300
        cls.LIFESPAN = 0.9  # Duration in seconds until bullet fades

    def __init__(self, centre, direction):
        self.centre = Vector2(*centre)
        self.velocity = Bullet.SPEED * direction
        self.duration = 0
        self.faded = False

    def hits(self, other):
        """Return True if bullet hits other polygon."""
        return other.collidepoint(self.centre) != 0

    def wrap(self, screen_area):
        """
        Wrap bullet to opposite side of screen if bullet leaves
        screen area.
        """
        if not self.hits(screen_area):
            width, height = screen_area.P[2][0], screen_area.P[2][1]
            if ((self.centre.x < 0 and self.velocity.x < 0)
               or (self.centre.x > width and self.velocity.x > 0)):
                self.centre.x = width - self.centre.x
            elif ((self.centre.y < 0 and self.velocity.y < 0)
                  or (self.centre.y > height and self.velocity.y > 0)):
                self.centre.y = height - self.centre.y

    def update(self, screen_area, dt):
        """Update bullet by dt seconds."""
        if self.duration < Bullet.LIFESPAN:
            self.duration += dt
            self.centre += self.velocity * dt
            self.wrap(screen_area)
        else:
            self.faded = True

    def draw(self, surface):
        """Draw bullet."""
        # draw.circle takes only integer arguments for centre position
        int_centre = map(int, map(round, self.centre))
        pygame.draw.circle(surface, WHITE, int_centre, Bullet.RADIUS)


class Asteroid(BasePolygon):
    """Asteroid object."""

    @classmethod
    def initialise_constants(cls, screen_width, screen_height):
        """
        Initialise constants for Asteroid which depend on the dimensions
        of the screen.
        """
        cls.MAX_CENTRE_X, cls.MAX_CENTRE_Y = screen_width, screen_height
        cls.MIN_SIDES = 10
        # Controls how much radius of asteroid points can vary
        cls.RADIUS_CONSTANT = screen_height // 120
        cls.MIN_SPEED = screen_height / 12
        cls.MAX_SPEED = 0.18 * screen_height
        # Asteroid size to Radius conversion
        cls.RADIUS = {
            3: 0.08 * screen_height,  # Large
            2: 0.04 * screen_height,  # Medium
            1: 0.02 * screen_height,  # Small
        }

    def __init__(self, centre=None, size=3):
        self.size = size
        self.velocity = self.random_velocity()
        super(Asteroid, self).__init__(self.random_points(centre), False)

    def initial_centre(self):
        """Return random position near edge of screen."""
        x = randint(0, Asteroid.MAX_CENTRE_X)
        y = randint(0, Asteroid.MAX_CENTRE_Y)
        while 0.25 < x / Asteroid.MAX_CENTRE_X < 0.75:
            x = randint(0, Asteroid.MAX_CENTRE_X)
        while 0.25 < y / Asteroid.MAX_CENTRE_Y < 0.75:
            y = randint(0, Asteroid.MAX_CENTRE_Y)
        return (x, y)

    def random_points(self, centre=None):
        """Return list of random points about centre."""
        centre = self.initial_centre() if centre is None else centre
        dr = Asteroid.RADIUS[self.size] // Asteroid.RADIUS_CONSTANT
        points = []
        theta = 0
        while theta < 360:
            r = Asteroid.RADIUS[self.size] + randint(-dr, dr)
            points.append(centre + Vector2(r, 0).rotate(theta))
            theta += randint(1, 360 / Asteroid.MIN_SIDES)
        return points

    def random_velocity(self):
        """
        Return random velocity with speed depending linearly on radius.
        """
        x1, y1 = Asteroid.RADIUS[1], Asteroid.MAX_SPEED
        x2, y2 = Asteroid.RADIUS[3], Asteroid.MIN_SPEED
        speed = (y2 - y1) / (x2 - x1) * (Asteroid.RADIUS[self.size] - x1) + y1
        return speed * Vector2(1, 0).rotate(randint(0, 359))

    def split(self):
        """Return two asteroids of next size."""
        return [Asteroid(self.C, self.size - 1) for _ in range(2)]

    def update(self, screen_area, dt):
        """Update asteroid by dt seconds."""
        self.move_ip(*self.velocity * dt)
        self.wrap(screen_area)

    def draw(self, surface):
        """Draw asteroid."""
        pygame.draw.aalines(surface, WHITE, True, self.P)


class AsteroidsGame:
    """Asteroids game."""

    INITIAL_ASTEROIDS = 4  # Number of asteroids at start of game
    START_OF_ROUND_TIME = 3  # Seconds to wait before starting new round
    # Scores for destroying each asteroid size
    SCORE = {
        3: 20,
        2: 50,
        1: 100,
    }
    MAX_FPS = 60

    def __init__(self, screen_width, screen_height):
        w, h = screen_width, screen_height
        self.surface = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
        pygame.display.set_caption('Asteroids')
        self.screen_area = Polygon([(0, 0), (w, 0), (w, h), (0, h)])
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.initialise_constants(screen_width, screen_height)
        self.exit = False
        self.score_font = pygame.freetype.Font('Hyperspace.otf', h // 15)
        self.highscore = 0
        self.reset()

    def initialise_constants(self, screen_width, screen_height):
        """
        Initialise constants for Ship, Asteroid, Bullet classes
        which depend on the dimensions of the screen.
        """
        Ship.initialise_constants(screen_width, screen_height)
        Asteroid.initialise_constants(screen_width, screen_height)
        Bullet.initialise_constants(screen_height)

    def reset(self):
        """Start a new game."""
        self.playing = True
        self.round = 0
        self.score = 0
        self.start_of_round_timer = 0
        self.ship = Ship()
        self.asteroids = []
        self.start_new_round()

    def start_new_round(self):
        """Start new round."""
        self.round += 1
        self.asteroids[:] = self.generate_asteroids()
        self.ship.invincible = True

    def generate_asteroids(self):
        """Return list of 3 + self.round asteroids."""
        number_of_asteroids = AsteroidsGame.INITIAL_ASTEROIDS + self.round - 1
        return [Asteroid() for _ in range(number_of_asteroids)]

    def destroy_asteroid(self, asteroid):
        """
        Remove asteroid from asteroids list and add two more smaller
        asteroids if asteroid is not smallest size.
        """
        self.asteroids.remove(asteroid)
        if asteroid.size > 1:
            self.asteroids.extend(asteroid.split())

    # draw_text function instead!!!
    def draw_score(self):
        self.score_font.render_to(self.surface, (5, 5), str(self.score), WHITE)

    def event_handler(self):
        # could this be made more readable?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit = True
                elif event.key == pygame.K_LEFT:
                    self.ship.rotate_direction -= 1
                elif event.key == pygame.K_RIGHT:
                    self.ship.rotate_direction += 1
                elif event.key == pygame.K_UP:
                    self.ship.boosting = True
                elif event.key == pygame.K_SPACE:
                    self.ship.shoot_bullet()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.ship.rotate_direction += 1
                if event.key == pygame.K_RIGHT:
                    self.ship.rotate_direction -= 1
                elif event.key == pygame.K_UP:
                    self.ship.boosting = False

    def update(self, dt):
        """Update game by dt seconds."""
        self.ship.update(self.screen_area, dt)

        if self.asteroids:
            for asteroid in reversed(self.asteroids):
                asteroid.update(self.screen_area, dt)
                if self.ship.hits(asteroid):
                    self.destroy_asteroid(asteroid)
                elif self.ship.shoots(asteroid):
                    self.score += AsteroidsGame.SCORE[asteroid.size]
                    self.destroy_asteroid(asteroid)
        else:
            self.start_of_round_timer += dt
            if self.start_of_round_timer > AsteroidsGame.START_OF_ROUND_TIME:
                self.start_new_round()
                self.start_of_round_timer = 0

    def draw(self):
        """Draw game while playing."""
        self.surface.fill(BLACK)
        self.ship.draw(self.surface)
        for asteroid in self.asteroids:
            asteroid.draw(self.surface)
        self.draw_score()

    def draw_end_screen(self):
        """Draw game after game over."""
        pass

    def play(self):
        """Play game until exit is True."""
        while not self.exit:
            self.event_handler()
            if self.playing:
                # Time since last frame in seconds
                dt = self.clock.tick(AsteroidsGame.MAX_FPS) / 1000
                self.update(dt)
                self.draw()
            else:
                self.draw_end_screen()
            pygame.display.update()


def main(width=None, height=None):
    pygame.init()
    width = pygame.display.Info().current_w if width is None else width
    height = pygame.display.Info().current_h if height is None else height
    AsteroidsGame(width, height).play()


if __name__ == '__main__':
    main()
