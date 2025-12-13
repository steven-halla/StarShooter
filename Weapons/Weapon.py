import pygame

class Weapon:
    """
    Base class for all weapons in the game.
    This class contains common functionality shared by Bullet, Missile, and other weapon types.
    """
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = 0  # To be overridden by subclasses
        self.height: int = 0  # To be overridden by subclasses
        self.speed: float = 0.0  # To be overridden by subclasses
        self.damage: int = 0  # To be overridden by subclasses
        self.rateOfFire: float = 1.0  # To be overridden by subclasses

        # HITBOX RECT — matches position + size
        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Movement variables
        self.diag_speed_x: float = 0.0  # left/right diagonal velocity
        self.diag_speed_y: float = 0.0  # downward velocity
        self.dx = 0  # horizontal movement per frame

        # Active state
        self.is_active: bool = True

    def update_rect(self) -> None:
        """Updates the hitbox rectangle to match the weapon's position and size."""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.rect.width = self.width
        self.rect.height = self.height

    def update(self) -> None:
        """
        Updates the weapon's position.
        This method should be overridden by subclasses to implement specific movement patterns.
        """
        self.x += self.dx  # horizontal drift
        self.y += self.speed
        self.update_rect()  # ALWAYS keep hitbox matched

    def draw(self, surface: "pygame.Surface") -> None:
        """
        Draws the weapon on the given surface.
        This method can be overridden by subclasses to implement specific visual appearances.
        """
        pygame.draw.rect(surface, (128, 0, 128), self.rect)  # Default purple color

    def collide_with_rect(self, other: pygame.Rect) -> bool:
        """
        Returns True if this weapon hits `other`.
        Also sets is_active = False so the owner can remove it.
        """
        if self.rect.colliderect(other):
            self.is_active = False
            return True
        return False
