import pygame

class Beam:
    DEFAULT_WIDTH: int = 5
    DEFAULT_HEIGHT: int = 5
    DEFAULT_SPEED: float = -9.0
    DEFAULT_DAMAGE: int = 1

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = self.DEFAULT_WIDTH
        self.height: int = self.DEFAULT_HEIGHT
        self.speed: float = self.DEFAULT_SPEED
        self.damage: int = self.DEFAULT_DAMAGE
        self.rateOfFire: float = 1.0

        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self) -> None:
        self.y += self.speed
        self.rect.y = int(self.y)

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, (128, 0, 128), self.rect)  # or GlobalConstants.PURPLEf
