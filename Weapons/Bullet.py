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

    # All methods (update_rect, update, draw, collide_with_rect) are inherited from Weapon class
