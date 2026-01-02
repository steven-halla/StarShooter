import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelSix(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()

        # -------------------------
        # APPEARANCE
        # -------------------------
        self.width = 40
        self.height = 40
        self.color = GlobalConstants.RED

        # -------------------------
        # BULLETS
        # -------------------------
        self.enemyBullets: list[Bullet] = []

        # -------------------------
        # STATS
        # -------------------------
        self.enemyHealth = 400

        # -------------------------
        # BARRAGE TIMING
        # -------------------------
        self.barrage_interval_ms = 1500
        self.last_barrage_time = pygame.time.get_ticks()

        self.barrage_active = False
        self.barrage_start_time = 0
        self.barrage_rect: pygame.Rect | None = None

        # -------------------------
        # SPRITE
        # -------------------------
        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

        self.barrage_active = False
        self.barrage_start_time = 0


        self.barrage_rects: list[pygame.Rect] = []
        self.BARRAGE_SIZE = 64
        self.BARRAGE_SPACING = 96  # > 64 guarantees NO overlap
        self.BARRAGE_COUNT = 64

    # =====================================================
    # BARRAGE SPAWN

    def call_barrage(self) -> None:
        self.barrage_rects.clear()

        SIZE = 64

        # Base offsets RELATIVE TO CAMERA (screen layout)
        BASE_COORDS = [
            # Row 1 (y = 60)
            (30, 60), (56, 60), (82, 60), (108, 60),
            (134, 60), (160, 60), (186, 60), (212, 60),
            (238, 60), (264, 60),

            # Row 2 (y = 86)
            (30, 86), (56, 86), (82, 86), (108, 86),
            (134, 86), (160, 86), (186, 86), (212, 86),
            (238, 86), (264, 86),

            # Row 3 (y = 112)
            (30, 112), (56, 112), (82, 112), (108, 112),
            (134, 112), (160, 112), (186, 112), (212, 112),
            (238, 112), (264, 112),

            # Row 4 (y = 138)
            (30, 138), (56, 138), (82, 138), (108, 138),
            (134, 138), (160, 138), (186, 138), (212, 138),
            (238, 138), (264, 138),

            # Row 5 (y = 164)
            (30, 164), (56, 164), (82, 164), (108, 164),
            (134, 164), (160, 164), (186, 164), (212, 164),
            (238, 164), (264, 164),

            # Row 6 (y = 190)
            (30, 190), (56, 190), (82, 190), (108, 190),
            (134, 190), (160, 190), (186, 190), (212, 190),
            (238, 190), (264, 190),
        ]
        # Convert screen-relative → WORLD space
        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)

        for sx, sy in BASE_COORDS:
            world_x = cam_x + sx
            world_y = cam_y + sy

            self.barrage_rects.append(
                pygame.Rect(world_x, world_y, SIZE, SIZE)
            )

        self.barrage_active = True
        self.barrage_start_time = pygame.time.get_ticks()
    # =====================================================
    # BARRAGE UPDATE
    # =====================================================
    def update_barrage(self) -> None:
        if not self.barrage_active:
            return

        if pygame.time.get_ticks() - self.barrage_start_time >= 2000:
            self.barrage_active = False
            self.barrage_rects.clear()

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self) -> None:
        super().update()
        if not self.is_active or self.camera is None:
            return

        self.update_hitbox()

        now = pygame.time.get_ticks()

        # 🔴 Spawn barrage on interval
        if now - self.last_barrage_time >= self.barrage_interval_ms:
            self.call_barrage()
            self.last_barrage_time = now

        # 🔴 Maintain barrage lifetime
        self.update_barrage()

        # Update bullets (unchanged behavior)
        for bullet in self.enemyBullets:
            bullet.update()

    # =====================================================
    # DRAW
    # =====================================================
    def draw(self, surface: pygame.Surface, camera):
        # Draw boss sprite
        sprite_rect = pygame.Rect(65, 130, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        sprite = pygame.transform.scale(
            sprite,
            (int(self.width * camera.zoom), int(self.height * camera.zoom))
        )

        surface.blit(
            sprite,
            (
                camera.world_to_screen_x(self.x),
                camera.world_to_screen_y(self.y),
            ),
        )

        # 🔴 Draw barrage LAST so it overlays
        self.draw_barrage(surface, camera)

    # =====================================================
    # BARRAGE DRAW
    # =====================================================
    def draw_barrage(self, surface, camera) -> None:
        if not self.barrage_active:
            return

        for rect in self.barrage_rects:
            x = camera.world_to_screen_x(rect.x)
            y = camera.world_to_screen_y(rect.y)

            pygame.draw.rect(
                surface,
                (255, 0, 0),
                (x, y, rect.width, rect.height)
            )
