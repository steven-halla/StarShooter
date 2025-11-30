import pygame
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Movement.MoveRectangle import MoveRectangle


class StarShip():
    def __init__(self):
        self.height: int = 50
        self.width: int = 50
        self.color: tuple = GlobalConstants.BLUE
        self.x: int = 0
        self.y: int = 0
        self.moveStarShip = MoveRectangle()
        self.speed: float = 5.0
        self.bullet_fire_interval_seconds: float = 1.0
        self.bullet_timer: Timer = Timer(self.bullet_fire_interval_seconds)

    def update(self):
       pass

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
