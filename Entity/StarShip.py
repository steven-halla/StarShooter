import pygame
from Constants.GlobalConstants import GlobalConstants
from Movement.MoveRectangle import MoveRectangle


class StarShip():
    def __init__(self):
        self.height: int = 50
        self.width: int = 50
        self.color: str = GlobalConstants.BLUE
        self.x: int = 0
        self.y: int = 0
        self.moveStarShip = MoveRectangle()
        self.speed: float = 5.0

    def update(self):
       print(self.speed)

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
