

import pygame

class Bullet:
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
        self.weapon_name = ""

        self.width = 8
        self.height = 8

        self.vx = 0.0
        self.vy = 0.0
        self.bullet_speed = 0.0

        self.damage = 1
        self.is_active = True

        self.camera = None

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # type 0 for projectile bullets, 1 is for bullets that persist like flamers
        self.remove_type: int = 0

    def update(self) -> None:
        # -------------------------
        # VECTOR-BASED MOVEMENT
        # -------------------------
        self.x += self.vx * self.bullet_speed
        self.y += self.vy * self.bullet_speed

        self.rect.topleft = (int(self.x), int(self.y))

        # -------------------------
        # DESPAWN OFF CAMERA
        # -------------------------
        if self.camera is not None:
            visible_top = self.camera.y - 100
            visible_bottom = (
                self.camera.y
                + (self.camera.window_height / self.camera.zoom)
                + 100
            )

            if self.y + self.height < visible_top or self.y > visible_bottom:
                self.is_active = False

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.is_active:
            return

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            pygame.Rect(
                screen_x,
                screen_y,
                int(self.width * camera.zoom),
                int(self.height * camera.zoom),
            ),
        )

    def collide_with_rect(self, other: pygame.Rect) -> bool:
        """
        Returns True if this weapon hits `other`.
        Also sets is_active = False so the owner can remove it.
        """
        if self.rect.colliderect(other):
            self.is_active = False
            return True
        return False



    def update_rect(self) -> None:
        """Updates the hitbox rectangle to match the weapon's position and size."""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.rect.width = self.width
        self.rect.height = self.height
