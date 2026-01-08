import pygame
from Weapons.Bullet import Bullet


class EnergyBall(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 60

        # identity
        self.magic_name: str = "Energy Ball"

        # stats
        self.damage: int = 5
        self.rate_of_fire: float = 0.0
        self.bullet_speed: float = 0.0

        # movement vector (stationary unless set externally)
        self.vx: float = 0.0
        self.vy: float = 0.0

        # state
        self.is_active: bool = True

        self.update_rect()

    def update(self) -> None:
        # movement handled by Bullet using vx/vy (no owner logic)
        super().update()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 0, 255), self.rect)
