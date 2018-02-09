from __future__ import division

import pygame
import pygame.freetype

from asteroid import Asteroid
from constants import W, H, BLACK, WHITE
from ship import Ship


INITIAL_ASTEROIDS = 4
START_OF_ROUND_DELAY = 3
# Scores for destroying each asteroid size
SCORE = {
    1: 100,  # Small asteroid
    2: 50,  # Medium asteroid
    3: 20,  # Large asteroid
}
SCORE_FONT_SIZE = 0.056 * H
SCORE_POSITION = (0.02 * H, 0.02 * H)

ICON_LENGTH = 0.04 * H
LIFE_ICON = Ship(ICON_LENGTH, (0.86 * ICON_LENGTH, 2.625 * ICON_LENGTH))

MAX_FPS = 60


class AsteroidsGame:
    """Asteroids game."""

    def __init__(self):
        self.surface = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.exit = False
        self.font = pygame.freetype.Font('Hyperspace.otf')
        self.highscore = 0
        self.reset()

    def reset(self):
        """Start a new game."""
        self.lives = 3
        self.ship = Ship()
        self.asteroids = []
        self.round = 0
        self.score = 0
        self.start_of_round_timer = 0
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

    def draw_text(self, text, size, position):
        self.font.render_to(self.surface, position, text, WHITE, size=size)

    def draw_hud(self):
        self.draw_text(str(self.score), SCORE_FONT_SIZE, SCORE_POSITION)
        for i in range(self.lives):
            LIFE_ICON.move(i * 2.7 * LIFE_ICON.width, 0).draw(self.surface)

    def draw_end_screen(self):
        """Draw game after game over."""
        pass

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
        self.ship.update(dt)

        if self.asteroids:
            for asteroid in reversed(self.asteroids):
                asteroid.update(dt)
                if self.ship.hits(asteroid):
                    self.destroy_asteroid(asteroid)
                    self.lives -= 1
                    self.ship.spawn()
                elif self.ship.shoots(asteroid):
                    self.score += SCORE[asteroid.size]
                    self.destroy_asteroid(asteroid)
        else:
            self.start_of_round_timer += dt
            if self.start_of_round_timer > START_OF_ROUND_DELAY:
                self.start_new_round()
                self.start_of_round_timer = 0

    def draw(self):
        """Draw game while playing."""
        self.surface.fill(BLACK)
        self.ship.draw(self.surface)
        for asteroid in self.asteroids:
            asteroid.draw(self.surface)
        self.draw_hud()

    def play(self):
        """Play game until exit is True."""
        while not self.exit:
            self.event_handler()
            if self.lives > 0:
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
