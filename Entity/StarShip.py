import pygame
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Movement.MoveRectangle import MoveRectangle


class StarShip():
    def __init__(self):
        self.height: int = 50
        self.width: int = 50
        self.color: tuple[int, int, int] = GlobalConstants.BLUE
        self.x: int = 0
        self.y: int = 0
        self.moveStarShip: MoveRectangle = MoveRectangle()
        self.speed: float = 5.0

        # firing stats
        self.bullet_fire_interval_seconds: float = 1.0
        self.bullet_timer: Timer = Timer(self.bullet_fire_interval_seconds)

        # spread stats
        self.bullet_spread_offset: int = 30   # distance left/right from center
        self.bullets_per_shot: int = 2       # e.g. left, center, right
        self.bullet_vertical_spacing: int = 22  # how far apart they are vertically
        self.bullet_fire_interval_seconds = .05 # .05 is 20 bullets per second
        self.bullet_timer = Timer(self.bullet_fire_interval_seconds)

    def update(self) -> None:
        pass

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
