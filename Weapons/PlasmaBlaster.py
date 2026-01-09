import pygame
from Weapons.Bullet import Bullet


class PlasmaBlaster(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 60

        # identity
        self.weapon_name: str = "Plasma Blaster"

        # stats
        self.damage: int = 10
        self.rate_of_fire: float = 0.0
        self.bullet_speed: float = 5.0

        # movement vector (straight up)
        self.vx: float = 0.0
        self.vy: float = -1.0

        # state
        self.is_active: bool = True

        self.update_rect()

    def update(self) -> None:
        # movement handled by Bullet using vx/vy and bullet_speed
        super().update()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (0, 255, 255), self.rect)
