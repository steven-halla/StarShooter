import pygame
from Weapons.Bullet import Bullet


class HyperLaser(Bullet):
    def __init__(self, owner):
        super().__init__(owner.x, owner.y)

        self.owner = owner

        # size
        self.width: int = 12
        self.height: int = 60

        # identity
        self.magic_name: str = "Energy Ball"

        # laser does NOT travel forward
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.bullet_speed: float = 0.0

        # damage / ROF (correct naming)
        self.damage: int = 5
        self.rate_of_fire: float = 0.0

        self.update_rect()

    def update(self):
        self.x = self.owner.x + self.owner.width / 2 - self.width / 2
        self.y = self.owner.y - self.height
        self.update_rect()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 0, 255), self.rect)
