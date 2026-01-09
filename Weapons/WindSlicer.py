import pygame
from Weapons.Bullet import Bullet


class WindSlicer(Bullet):
    def __init__(self, x: float, y: float, vx: float, vy: float):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 12

        # identity
        self.weapon_name: str = "Wind Slicer"

        # stats
        self.damage: int = 5
        self.rate_of_fire: float = 0.0
        self.bullet_speed: float = 3.0

        # movement vector
        self.vx: float = vx
        self.vy: float = vy

        # state
        self.is_active: bool = True

        self.update_rect()

    def update(self) -> None:
        # movement handled by Bullet using vx/vy
        super().update()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (180, 220, 255), self.rect)
