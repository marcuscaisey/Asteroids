import pygame
from pygame.math import Vector2

# COLOURS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


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
