import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy


class BileSpitter(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.width: int = 30
        self.height: int = 30
        self.color: tuple[int, int, int] = GlobalConstants.RED



        self.speed: float = 1.0
        self.enemyHealth: int = 10
        self.exp: int = 1
        self.credits: int = 5

    def update(self) -> None:
        # For now, no movement / AI. Hook for future logic.
        pass

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))


