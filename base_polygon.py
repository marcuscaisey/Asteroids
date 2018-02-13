from math import cos, sin

from numpy import array, dot
from pylygon import Polygon

from screen_constants import WIDTH, HEIGHT, AREA


class BasePolygon(Polygon):
    """
    Base polygon class which includes some modifications to the original
    Polygon class methods.
    """

    # Original Polygon _rotate method uses 'if not origin:' to test if origin
    # is None which does not work for a numpy array as the truth value of a
    # numpy array with more than one element is ambiguous.
    def _rotate(self, x0, theta, origin=None):
        # if not origin: origin = self.C
        origin = self.C if origin is None else origin

        origin = origin.reshape(2, 1)
        x0 = x0.reshape(2, 1)
        x0 = x0 - origin  # assingment operator (-=) would modify original x0

        A = array([[cos(theta), -sin(theta)],  # rotation matrix
                   [sin(theta), cos(theta)]])

        return (dot(A, x0) + origin).ravel()

    # Original Polygon rotate_ip method creates new Polygon with points rotated
    # by theta. This changes the order of the points in self.P which makes
    # it more difficult to define which edges to draw.
    def rotate_ip(self, theta):
        # other = Polygon(self.rotopoints(theta))
        # self.P[:] = other.P
        # self.edges[:] = other.edges
        self.P[:] = self.rotopoints(theta)
        self.edges[:] = self.rotoedges(theta)

    def hits(self, other):
        """Return true if self hits other polygon."""
        return self.collidepoly(other) is not False

    def wrap(self):
        """
        Wrap polygon to opposite side of screen if polygon leaves
        screen area.
        """
        if self.collidepoly(AREA) is False:
            # Polygon should only be wrapped if it's moving away from the edge
            # of the screen. Wrap by translating the polygon so that its
            # furthest point from the edge of the screen is now on the opposite
            # edge of the screen.
            if self.C[0] < 0 and self.velocity.x < 0:
                self.move_ip(WIDTH - min(self.P, key=lambda x: x[0])[0], 0)
            elif self.C[0] > WIDTH and self.velocity.x > 0:
                self.move_ip(-max(self.P, key=lambda x: x[0])[0], 0)
            elif self.C[1] < 0 and self.velocity.y < 0:
                self.move_ip(0, HEIGHT - min(self.P, key=lambda x: x[1])[1])
            elif self.C[1] > HEIGHT and self.velocity.y > 0:
                self.move_ip(0, -max(self.P, key=lambda x: x[1])[1])
