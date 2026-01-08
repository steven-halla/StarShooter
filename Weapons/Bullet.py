

import pygame

class Bullet:
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

        self.width = 8
        self.height = 8

        self.vx = 0.0
        self.vy = 0.0
        self.bullet_speed = 0.0

        self.damage = 1
        self.is_active = True

        self.camera = None

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

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
