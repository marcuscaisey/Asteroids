from __future__ import division

import pygame
import pygame.freetype

from asteroid import Asteroid
from screen_constants import WIDTH, HEIGHT
from ship import Ship
from hud import HUD


BLACK, WHITE = (0, 0, 0), (255, 255, 255)

INITIAL_ASTEROIDS = 5
START_OF_ROUND_DELAY = 2
GAMEOVER_SIZE = 0.2 * HEIGHT
SCORE_SIZE = 0.12 * HEIGHT
PLAY_AGAIN_SIZE = 0.08 * HEIGHT
# Scores for destroying each asteroid size
SCORE = {
    1: 100,  # Small asteroid
    2: 50,  # Medium asteroid
    3: 20,  # Large asteroid
}
MAX_FPS = 60


class AsteroidsGame:
    """Asteroids game."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Asteroids')
        pygame.mouse.set_visible(False)
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.exit = False
        self.font = pygame.freetype.Font('Hyperspace.otf')
        self.highscore = 0
        self.reset()

    def reset(self):
        """Start a new game."""
        self.ship = Ship()
        self.asteroids = []
        self.round = 0
        self.lives = 3
        self.score = 0
        self.hud = HUD()
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

    def draw_text(self, text, y, size):
        """Draw text to surface centred at height y."""
        text_width = self.font.get_rect(text, size=size).width
        x = 0.5 * (WIDTH - text_width)
        self.font.render_to(self.surface, (x, y), text, WHITE, size=size)

    def draw_end_screen(self):
        """Draw game after game over."""
        self.surface.fill(BLACK)
        # Calculations for spacing of text
        v = 0.1 * HEIGHT
        h1 = self.font.get_rect('0', size=GAMEOVER_SIZE).height
        h2 = self.font.get_rect('0', size=SCORE_SIZE).height
        h3 = self.font.get_rect('0', size=PLAY_AGAIN_SIZE).height
        s2 = 0.5 * h2
        s1 = 0.5 * (HEIGHT - 2 * v - h1 - 2 * h2 - h3 - s2)
        y = v
        self.draw_text('game over', y, GAMEOVER_SIZE)
        y += h1 + s1
        self.draw_text('score {}'.format(self.score), y, SCORE_SIZE)
        y += h2 + s2
        self.draw_text('highscore {}'.format(self.highscore), y, SCORE_SIZE)
        y += h2 + s1
        self.draw_text('press space to play again', y, PLAY_AGAIN_SIZE)

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit = True
                elif event.key == pygame.K_LEFT:
                    self.ship.rotate_direction -= 1
                elif event.key == pygame.K_RIGHT:
                    self.ship.rotate_direction += 1
                elif event.key == pygame.K_UP:
                    self.ship.boosting = True
                elif event.key == pygame.K_SPACE:
                    if self.lives > 0:
                        self.ship.shoot_bullet()
                    else:
                        self.reset()
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
                    self.destroy_asteroid(asteroid)
                    self.score += SCORE[asteroid.size]
                    if self.score > self.highscore:
                        self.highscore = self.score
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
        self.hud.draw(self.surface, self.score, self.lives)

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
