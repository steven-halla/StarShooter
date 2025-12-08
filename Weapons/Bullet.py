import pygame

class Bullet:
    DEFAULT_WIDTH: int = 5
    DEFAULT_HEIGHT: int = 5
    DEFAULT_SPEED: float = -9.0
    DEFAULT_DAMAGE: int = 1
    DEFAULT_VERTICAL_SPEED: float = 3.0


    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = self.DEFAULT_WIDTH
        self.height: int = self.DEFAULT_HEIGHT
        self.speed: float = self.DEFAULT_SPEED
        self.damage: int = self.DEFAULT_DAMAGE
        self.rateOfFire: float = 1.0

        # HITBOX RECT — matches position + size
        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # --- Explicit diagonal movement names ---
        self.diag_speed_x: float = 0.0  # left/right diagonal velocity
        self.diag_speed_y: float = self.DEFAULT_VERTICAL_SPEED  # downward velocity
        self.dx = 0   # horizontal movement per frame

    # 🔸 NEW helper (keeps hitbox synced)
    def update_rect(self) -> None:
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.rect.width = self.width
        self.rect.height = self.height

    def update(self) -> None:
        self.x += self.dx  # horizontal drift
        self.y += self.speed
        self.update_rect()      # <-- ALWAYS keep hitbox matched

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, (128, 0, 128), self.rect)  # or GlobalConstants.PURPLE

    def collide_with_rect(self, other: pygame.Rect) -> bool:
        """
        Returns True if this bullet hits `other`.
        Also sets is_active = False so the owner can remove it.
        """
        if self.rect.colliderect(other):
            self.is_active = False
            return True
        return False
