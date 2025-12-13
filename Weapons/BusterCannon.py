import pygame


class BusterCanon:
    def __init__(self,x,y):
        self.x: float = x
        self.y: float = y
        self.mp_cost: int = 10
        self.base_damage: int = 10
        self.charge_shot_damage: int = 40
        self.x: float = x
        self.y: float = y
        self.width: int = 12
        self.height: int = 12
        self.speed: float = -5
        self.rateOfFire: float = .5
        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.dx = 0   # horizontal movement per frame



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
        pygame.draw.rect(surface, (128, 0, 128), self.rect)

    def collide_with_rect(self, other: pygame.Rect) -> bool:
        """
        Returns True if this bullet hits `other`.
        Also sets is_active = False so the owner can remove it.
        """
        if self.rect.colliderect(other):
            self.is_active = False
            return True
        return False
