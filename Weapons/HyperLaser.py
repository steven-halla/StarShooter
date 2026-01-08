import pygame
from Weapons.Bullet import Bullet


class HyperLaser(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 60

        # identity
        self.magic_name: str = "Hyper Laser"

        # laser does not move
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.bullet_speed: float = 0.0

        # damage / ROF
        self.damage: int = 5
        self.rate_of_fire: float = 0.0

        self.update_rect()

    def update(self):
        # stationary laser
        self.update_rect()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 0, 255), self.rect)
