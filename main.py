from __future__ import division

import pygame
import pygame.freetype
from pylygon import Polygon

from asteroid import Asteroid
from ship import Ship

pygame.display.init()
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h


BLACK, WHITE = (0, 0, 0), (255, 255, 255)

START_OF_ROUND_TIME = 3  # Seconds to wait before starting new round
INITIAL_ASTEROIDS = 4  # Number of asteroids at start of game

# Scores for destroying each asteroid size
SCORE = {
    1: 100,  # Small asteroid
    2: 50,  # Medium asteroid
    3: 20,  # Large asteroid
}
SCORE_FONT_SIZE = screen_height // 18
SCORE_POSITION = (screen_height // 90, screen_height // 90)

MAX_FPS = 60


class AsteroidsGame:
    """Asteroids game."""

    def __init__(self):
        w, h = screen_width, screen_height
        self.surface = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
        self.screen_area = Polygon([(0, 0), (w, 0), (w, h), (0, h)])
        self.clock = pygame.time.Clock()
        self.exit = False
        self.font = pygame.freetype.Font('Hyperspace.otf')
        self.highscore = 0
        self.reset()

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
        number_of_asteroids = INITIAL_ASTEROIDS + self.round - 1
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
        self.draw_text(SCORE_POSITION, str(self.score), SCORE_FONT_SIZE)

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
                    self.score += SCORE[asteroid.size]
                    self.destroy_asteroid(asteroid)
        else:
            self.start_of_round_timer += dt
            if self.start_of_round_timer > START_OF_ROUND_TIME:
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
                dt = self.clock.tick(MAX_FPS) / 1000
                self.update(dt)
                self.draw()
            else:
                self.draw_end_screen()
            pygame.display.update()


def main():
    pygame.init()
    pygame.display.set_caption('Asteroids')
    pygame.mouse.set_visible(False)
    AsteroidsGame().play()


if __name__ == '__main__':
    main()
