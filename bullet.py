import pygame
from pygame.math import Vector2

from screen_constants import WIDTH, HEIGHT, AREA


WHITE = (255, 255, 255)

SPEED = 0.8 * HEIGHT
RADIUS = HEIGHT // 300
LIFESPAN = 0.9  # Duration in seconds until bullet fades


class Bullet(Vector2):
    """Bullet object."""

    def __init__(self, source, direction):
        self.centre = Vector2(*source)
        self.velocity = SPEED * direction
        self.duration = 0
        self.faded = False

    def hits(self, other):
        """Return True if bullet hits other polygon."""
        return other.collidepoint(self.centre) != 0

    def wrap(self):
        """
        Wrap bullet to opposite side of screen if it leaves screen area.
        """
        if not self.hits(AREA):
            if ((self.centre.x < 0 and self.velocity.x < 0)
               or (self.centre.x > WIDTH and self.velocity.x > 0)):
                self.centre.x = WIDTH - self.centre.x
            elif ((self.centre.y < 0 and self.velocity.y < 0)
                  or (self.centre.y > HEIGHT and self.velocity.y > 0)):
                self.centre.y = HEIGHT - self.centre.y

    def update(self, dt):
        """Update bullet by dt seconds."""
        if self.duration < LIFESPAN:
            self.duration += dt
            self.centre += self.velocity * dt
            self.wrap()
        else:
            self.faded = True

    def draw(self, surface):
        """Draw bullet to surface."""
        # draw.circle takes only integer arguments for centre position
        int_centre = map(int, map(round, self.centre))
        pygame.draw.circle(surface, WHITE, int_centre, RADIUS)
