
# HyperLaser.py

import pygame
from Weapons.Bullet import Bullet


class HyperLaser(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # -----------------
        # SIZE
        # -----------------
        self.width: int = 10
        self.height: int = 30

        # -----------------
        # IDENTITY
        # -----------------
        self.weapon_name: str = "Hyper Laser"

        # -----------------
        # DAMAGE
        # -----------------
        self.damage: int = 100

        # -----------------
        # RATE OF FIRE
        # -----------------
        self.rate_of_fire: float = 0.10
        self.last_fire_time: float = 0.0

        # -----------------
        # MOVEMENT (STATIC)
        # -----------------
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.bullet_speed: float = 0.0

        # -----------------
        # CAMERA
        # -----------------
        self.camera = None

        self.update_rect()

    # -----------------
    # RATE OF FIRE CHECK
    # -----------------
    def can_fire(self) -> bool:
        now = pygame.time.get_ticks() / 1000.0
        return (now - self.last_fire_time) >= self.rate_of_fire

    # -----------------
    # FIRE (RETURNS OBJECT, NOT LIST)
    # -----------------
    def fire_hyper_laser(self):
        if not self.can_fire():
            return None

        self.last_fire_time = pygame.time.get_ticks() / 1000.0

        # SAME PATTERN AS BUSTER CANNON
        bullet_x = self.x + self.width // 2
        bullet_y = self.y - 20

        laser = HyperLaser(bullet_x, bullet_y)

        laser.damage = self.damage
        laser.camera = self.camera

        # MOVEMENT (MATCH BUSTER CANNON)
        laser.vx = 0.0
        laser.vy = -1.0

        laser.update_rect()

        print(
            f"[HyperLaser SPAWN] "
            f"x={laser.x:.2f} y={laser.y:.2f} "
            f"rect={laser.rect}"
        )


        return laser
    # -----------------
    # UPDATE
    # -----------------
    def update(self) -> None:
        self.update_rect()

    # -----------------
    # DRAW
    # -----------------
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 0, 255), self.rect)

