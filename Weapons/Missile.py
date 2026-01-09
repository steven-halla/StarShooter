import pygame
import math
from Weapons.Bullet import Bullet


class Missile(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 12

        # identity
        self.weapon_name: str = "Missile"

        # stats
        self.damage: int = 3
        self.rate_of_fire: float = 0.5
        self.bullet_speed: float = 2.5

        # movement vector (default straight up)
        self.vx: float = 0.0
        self.vy: float = -1.0

        # homing
        self.target_enemy = None

        self.update_rect()

    def update(self) -> None:
        # clear invalid target
        if self.target_enemy is not None and self.target_enemy.enemyHealth <= 0:
            self.target_enemy = None

        # homing logic — vx/vy ONLY
        if self.target_enemy is not None:
            vx = self.target_enemy.x - self.x
            vy = self.target_enemy.y - self.y
            length = math.hypot(vx, vy)

            if length != 0:
                self.vx = vx / length
                self.vy = vy / length

        # movement handled by Bullet via vx/vy
        super().update()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 165, 0), self.rect)
