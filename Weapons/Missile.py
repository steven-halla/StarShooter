import pygame



class Missile:
    def __init__(self,x,y):
        self.x: float = x
        self.y: float = y
        self.width: int = 12
        self.height: int = 12
        self.speed: float = -5
        self.rateOfFire: float = .5
        self.missileNumber: int = 1

        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.diag_speed_x: float = 0.0
        self.diag_speed_y: float = 3
        self.dx = 0

    def update_rect(self) -> None:
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.rect.width = self.width
        self.rect.height = self.height

    def update(self) -> None:

        # If target is gone, dead, or off-screen → clear target
        if (self.target_enemy is None or
                self.target_enemy.enemyHealth <= 0):
            self.target_enemy = None
        # --- HOMING LOGIC ---
        if getattr(self, "target_enemy", None) is not None:
            dx = self.target_enemy.x - self.x
            dy = self.target_enemy.y - self.y
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            print(f"Homing → Target at ({self.target_enemy.x}, {self.target_enemy.y})")

            # normalized direction
            self.direction_x = dx / dist
            self.direction_y = dy / dist

            # apply missile speed toward target
            speed = abs(self.speed)
            self.x += self.direction_x * speed
            self.y += self.direction_y * speed

        else:
            # --- DEFAULT (non-homing) MOVEMENT ---
            self.x += self.dx
            self.y += self.speed


        # Keep hitbox matched to position
        self.update_rect()


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
