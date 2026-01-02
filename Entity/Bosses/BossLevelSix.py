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
        self.BARRAGE_COUNT = 5

    # =====================================================
    # BARRAGE SPAWN


    def call_barrage(self) -> None:
        # ⛔ DO NOT restart if already active
        if self.barrage_active:
            return

        self.barrage_active = True
        self.barrage_start_time = pygame.time.get_ticks()

        self.barrage_rect = pygame.Rect(
            int(self.x + self.width // 2 - 32),
            int(self.y + self.height),
            64,
            64
        )

    # =====================================================
    # BARRAGE UPDATE
    # =====================================================
    def update_barrage(self) -> None:
        if not self.barrage_active:
            return

        if pygame.time.get_ticks() - self.barrage_start_time >= 2000:
            self.barrage_active = False
            self.barrage_rect = None

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
        if not self.barrage_active or self.barrage_rect is None:
            return

        x = camera.world_to_screen_x(self.barrage_rect.x)
        y = camera.world_to_screen_y(self.barrage_rect.y)

        pygame.draw.rect(
            surface,
            (255, 0, 0),
            (x, y, 64, 64)
        )
