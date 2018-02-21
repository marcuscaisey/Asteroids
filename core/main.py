from __future__ import division
from random import uniform

import pygame as pg
import pygame.freetype

from .components import Asteroid, HUD, Saucer, Ship
from .helpers import find_asset
from .screenconstants import SCREEN_W, SCREEN_H


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

INITIAL_ASTEROIDS = 4
SECONDS_PER_SAUCER = 30
SMALL_SAUCER_RATE = 0.25
START_OF_ROUND_DELAY = 2

ASTEROID_SCORE = {
    1: 100,  # Small asteroid
    2: 50,  # Medium asteroid
    3: 20,  # Large asteroid
}
SAUCER_SCORE = {
    1: 1000,  # Small saucer
    2: 200,  # Large saucer
}
EXTRA_LIFE_SCORE = 10000

# Sizes for text on game over screen
GAMEOVER_SIZE = 0.2 * SCREEN_H
SCORE_SIZE = 0.12 * SCREEN_H
PLAY_AGAIN_SIZE = 0.08 * SCREEN_H
FONT_PATH = find_asset('fonts\Hyperspace.otf')

MAX_FPS = 60


class Game:
    """Asteroids game."""

    def __init__(self):
        pg.init()
        pg.display.set_caption('Asteroids')
        pg.mouse.set_visible(False)
        self.surface = pg.display.set_mode((SCREEN_W, SCREEN_H), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.exit = False
        self.font = pygame.freetype.Font(FONT_PATH)
        self.highscore = 0
        self.reset()

    def reset(self):
        """Start a new game."""
        self.ship = Ship()
        self.asteroids = []
        self.saucers = []
        self.round = 0
        self.lives = 3
        self.score = 0
        self.hud = HUD()
        self.saucer_timer = 0
        self.extra_life_counter = 0
        self.start_new_round()

    def start_new_round(self):
        """Start new round."""
        self.start_of_round_timer = 0
        self.round += 1
        self.asteroids[:] = self.generate_asteroids()
        self.ship.invincible = True

    def generate_asteroids(self):
        """Return list of 3 + self.round asteroids."""
        number_of_asteroids = INITIAL_ASTEROIDS + self.round - 1
        return [Asteroid() for _ in range(number_of_asteroids)]

    def generate_saucer(self, dt):
        """
        Add new saucer to list of saucers every SECONDS_PER_SAUCER
        seconds, with SMALL_SAUCER_RATE probablity of adding a small
        saucer.
        """
        self.saucer_timer += dt
        if self.saucer_timer > SECONDS_PER_SAUCER:
            self.saucer_timer %= SECONDS_PER_SAUCER
            size = 1 if uniform(0, 1) < SMALL_SAUCER_RATE else 2
            self.saucers.append(Saucer(size))

    def destroy_asteroid(self, asteroid):
        """
        Remove asteroid from asteroids list and add two more smaller
        asteroids if asteroid is not smallest size.
        """
        self.asteroids.remove(asteroid)
        if asteroid.size > 1:
            self.asteroids.extend(asteroid.split())

    def destroy_saucer(self, saucer):
        """Remove saucer from saucers list"""
        self.saucers.remove(saucer)

    def draw_text(self, text, y, size):
        """Draw text to surface centred at height y."""
        text_width = self.font.get_rect(text, size=size).width
        x = 0.5 * (SCREEN_W - text_width)
        self.font.render_to(self.surface, (x, y), text, WHITE, size=size)

    def draw_game_over_screen(self):
        """Draw game after game over."""
        self.surface.fill(BLACK)
        # Calculations for spacing of text
        v = 0.1 * SCREEN_H
        h1 = self.font.get_rect('0', size=GAMEOVER_SIZE).height
        h2 = self.font.get_rect('0', size=SCORE_SIZE).height
        h3 = self.font.get_rect('0', size=PLAY_AGAIN_SIZE).height
        s2 = 0.5 * h2
        s1 = 0.5 * (SCREEN_H - 2 * v - h1 - 2 * h2 - h3 - s2)
        y = v
        self.draw_text('game over', y, GAMEOVER_SIZE)
        y += h1 + s1
        self.draw_text('score {}'.format(self.score), y, SCORE_SIZE)
        y += h2 + s2
        self.draw_text('highscore {}'.format(self.highscore), y, SCORE_SIZE)
        y += h2 + s1
        self.draw_text('press space to play again', y, PLAY_AGAIN_SIZE)

    def key_down(self, event):
        """Process key down events."""
        if event.key == pg.K_ESCAPE:
            self.exit = True
        elif event.key == pg.K_LEFT:
            self.ship.rotate_direction -= 1
        elif event.key == pg.K_RIGHT:
            self.ship.rotate_direction += 1
        elif event.key == pg.K_UP:
            self.ship.boosting = True
        elif event.key == pg.K_SPACE:
            if self.lives > 0:
                self.ship.shoot()
            else:
                self.reset()

    def key_up(self, event):
        """Process key up events."""
        if event.key == pg.K_LEFT:
            self.ship.rotate_direction += 1
        elif event.key == pg.K_RIGHT:
            self.ship.rotate_direction -= 1
        elif event.key == pg.K_UP:
            self.ship.boosting = False

    def event_handler(self):
        """Process key up and key down events."""
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                self.key_down(event)
            elif event.type == pg.KEYUP:
                self.key_up(event)

    def respawn_ship(self):
        """
        Respawn ship after it collides with another object or has been
        shot.
        """
        self.lives -= 1
        self.ship.spawn()

    def check_collisions(self):
        """Check for collisions between asteroids/saucers/ship."""
        for asteroid in reversed(self.asteroids):
            if asteroid.hits(self.ship):
                self.destroy_asteroid(asteroid)
                self.respawn_ship()
            else:
                for saucer in reversed(self.saucers):
                    if asteroid.hits(saucer):
                        self.destroy_asteroid(asteroid)
                        self.destroy_saucer(saucer)
        for saucer in reversed(self.saucers):
            if saucer.hits(self.ship):
                self.destroy_saucer(saucer)
                self.respawn_ship()
            else:
                other_saucers = [x for x in self.saucers if x != saucer]
                for other_saucer in reversed(other_saucers):
                    if saucer.hits(other_saucer):
                        self.destroy_saucer(other_saucer)
                        self.destroy_saucer(saucer)

    def check_shots(self):
        """Check if any saucers/asteroids/ship have been shot."""
        for asteroid in reversed(self.asteroids):
            if self.ship.shoots(asteroid):
                self.destroy_asteroid(asteroid)
                self.score += ASTEROID_SCORE[asteroid.size]
            else:
                for saucer in self.saucers:
                    if saucer.shoots(asteroid):
                        self.destroy_asteroid(asteroid)
        for saucer in reversed(self.saucers):
            if saucer.shoots(self.ship):
                self.respawn_ship()
            if self.ship.shoots(saucer):
                self.destroy_saucer(saucer)
                self.score += SAUCER_SCORE[saucer.size]

    def update(self, dt):
        """Update game by dt seconds."""
        self.ship.update(dt)
        for asteroid in self.asteroids:
            asteroid.update(dt)
        for saucer in self.saucers:
            saucer.update(self.ship, dt)
        self.generate_saucer(dt)

        if self.asteroids or self.saucers:
            self.check_collisions()
            self.check_shots()
        else:
            self.start_of_round_timer += dt
            if self.start_of_round_timer > START_OF_ROUND_DELAY:
                self.start_new_round()

        if self.score > self.highscore:
            self.highscore = self.score
        # Player gets an extra life for every EXTRA_LIFE_SCORE points they get
        if self.score // EXTRA_LIFE_SCORE == self.extra_life_counter + 1:
            self.extra_life_counter += 1
            self.lives += 1

    def draw(self):
        """Draw game while playing."""
        self.surface.fill(BLACK)
        self.ship.draw(self.surface)
        for asteroid in self.asteroids:
            asteroid.draw(self.surface)
        for saucer in self.saucers:
            saucer.draw(self.surface)
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
                self.draw_game_over_screen()
            pg.display.update()
