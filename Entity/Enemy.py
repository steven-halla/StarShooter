import pygame

from Constants.GlobalConstants import GlobalConstants
from Movement.MoveRectangle import MoveRectangle


class Enemy():
    def __init__(self):
        self.height: int = 0
        self.width: int = 0
        self.color: tuple = GlobalConstants.RED
        self.x: int = 0
        self.y: int = 0
        self.moveEnemy = MoveRectangle()
        self.speed: float = 0.0
        self.enemyHealth: int = 0
        self.enemySpecialMoves: list = []
        self.enemyBullets: list = []
        self.exp: int = 0
        self.credits: int = 0



    def update(self):
       pass

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))


