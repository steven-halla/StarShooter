import pygame

from Constants.GlobalConstants import GlobalConstants
from Movement.MoveRectangle import MoveRectangle


class Enemy:
    def __init__(self):
        self.height: int = 0
        self.width: int = 0
        self.mover: MoveRectangle = MoveRectangle()

        self.color: tuple = GlobalConstants.RED
        self.x: int = 0
        self.y: int = 0
        self.moveEnemy = MoveRectangle()
        self.moveSpeed: float = 0.0
        self.enemyHealth: int = 0
        self.enemySpecialMoves: list = []
        self.enemyBullets: list = []
        self.exp: int = 0
        self.credits: int = 0
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.camera = None





    def update(self):
        self.update_hitbox()
        self.is_on_screen = self.mover.enemy_on_screen(self, self.camera)



    # def draw(self, surface: "pygame.Surface") -> None:
    #     pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def update_hitbox(self) -> None:
        self.hitbox.update(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height),
        )

    def on_hit(self):
        # print("ENEMY HIT!")
        self.color = (255, 255, 0)  # yellow forever
