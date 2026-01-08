import pygame
from Weapons.Bullet import Bullet


class WaveCrash(Bullet):
    def __init__(self, x: float, y: float, direction: int):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 22

        # identity
        self.magic_name: str = "Wave Crash"

        # stats
        self.damage: int = 6
        self.rate_of_fire: float = 0.5
        self.bullet_speed: float = 6.0

        # movement vector (horizontal only)
        self.vx: float = float(direction)   # -1 left, +1 right
        self.vy: float = 0.0

        # state
        self.is_active: bool = True

        self.update_rect()

    def update(self) -> None:
        # movement handled by Bullet using vx/vy and bullet_speed
        super().update()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (0, 200, 255), self.rect)
