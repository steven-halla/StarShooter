import math

import pygame

from Weapons.Weapon import Weapon


class Bullet(Weapon):
    DEFAULT_WIDTH: int = 5
    DEFAULT_HEIGHT: int = 5
    DEFAULT_SPEED: float = -9.0
    DEFAULT_DAMAGE: int = 1
    DEFAULT_VERTICAL_SPEED: float = 3.0

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.speed = self.DEFAULT_SPEED
        self.damage = self.DEFAULT_DAMAGE
        self.rateOfFire = 1.0

        # Set Bullet-specific diagonal movement
        self.diag_speed_y = self.DEFAULT_VERTICAL_SPEED  # downward velocity

    def fire_in_8_directions(self, dx: float, dy: float, speed: float) -> None:
        length = math.hypot(dx, dy)
        if length == 0:
            return

        # Weapon.update() moves:
        #   y += self.speed
        #   x += self.diag_speed_y
        self.speed = (dy / length) * speed  # vertical
        self.diag_speed_y = (dx / length) * speed  # horizontal
