from __future__ import division
import pygame
import pygame.freetype
from pylygon import Polygon
from bullet import Bullet
from ship import Ship
from asteroid import Asteroid

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


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
        self.font = pygame.freetype.Font('Hyperspace.otf')
        self.highscore = 0
        self.reset()

    def initialise_constants(self, screen_width, screen_height):
        """
        Initialise constants for Ship, Asteroid, Bullet classes which
        depend on the dimensions of the screen.
        """
        Ship.initialise_constants(screen_width, screen_height)
        Asteroid.initialise_constants(screen_width, screen_height)
        Bullet.initialise_constants(screen_height)
        self.score_font_size = screen_height // 18
        self.score_position = (screen_height // 100, screen_height // 100)

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

    def draw_text(self, position, text, size):
        self.font.render_to(self.surface, position, text, WHITE, size=size)

    def draw_score(self):
        self.draw_text(self.score_position, str(self.score), self.score_font_size)

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
