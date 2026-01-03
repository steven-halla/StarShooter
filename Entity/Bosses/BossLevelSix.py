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
        # SPRITE
        # -------------------------
        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

        # -------------------------
        # BARRAGE DATA
        # -------------------------
        self.barrage_rects: list[pygame.Rect] = []
        self.BARRAGE_SIZE = 64

        # -------------------------
        # BARRAGE PHASES
        # -------------------------
        self.PHASE_RED = 0
        self.PHASE_ORANGE = 1
        self.PHASE_OFF = 2

        self.barrage_phase = self.PHASE_OFF
        self.barrage_timer = pygame.time.get_ticks()

        self.RED_MS = 2000
        self.ORANGE_MS = 1000
        self.OFF_MS = 2000

    # =====================================================
    # BARRAGE SPAWN (UNCHANGED GRID)
    # =====================================================
    def call_barrage(self) -> None:
        self.barrage_rects.clear()
        SIZE = self.BARRAGE_SIZE

        BASE_COORDS = [
            (30, 60), (56, 60), (82, 60), (108, 60),
            (134, 60), (160, 60), (186, 60), (212, 60),
            (238, 60), (264, 60),

            (30, 86), (56, 86), (82, 86), (108, 86),
            (134, 86), (160, 86), (186, 86), (212, 86),
            (238, 86), (264, 86),

            (30, 112), (56, 112), (82, 112), (108, 112),
            (134, 112), (160, 112), (186, 112), (212, 112),
            (238, 112), (264, 112),

            (30, 138), (56, 138), (82, 138), (108, 138),
            (134, 138), (160, 138), (186, 138), (212, 138),
            (238, 138), (264, 138),

            (30, 164), (56, 164), (82, 164), (108, 164),
            (134, 164), (160, 164), (186, 164), (212, 164),
            (238, 164), (264, 164),

            (30, 190), (56, 190), (82, 190), (108, 190),
            (134, 190), (160, 190), (186, 190), (212, 190),
            (238, 190), (264, 190),
        ]

        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)

        for sx, sy in BASE_COORDS:
            self.barrage_rects.append(
                pygame.Rect(cam_x + sx, cam_y + sy, SIZE, SIZE)
            )

    # =====================================================
    # BARRAGE PHASE CONTROLLER
    # =====================================================
    def update_barrage(self) -> None:
        now = pygame.time.get_ticks()
        elapsed = now - self.barrage_timer

        # 🔴 RED
        if self.barrage_phase == self.PHASE_RED:
            if elapsed >= self.RED_MS:
                self.barrage_phase = self.PHASE_ORANGE
                self.barrage_timer = now

        # 🟧 ORANGE FLASH
        elif self.barrage_phase == self.PHASE_ORANGE:
            if elapsed >= self.ORANGE_MS:
                self.barrage_phase = self.PHASE_OFF
                self.barrage_rects.clear()
                self.barrage_timer = now

        # ❌ OFF
        elif self.barrage_phase == self.PHASE_OFF:
            if elapsed >= self.OFF_MS:
                self.barrage_phase = self.PHASE_RED
                self.call_barrage()
                self.barrage_timer = now

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self) -> None:
        super().update()
        if not self.is_active or self.camera is None:
            return

        self.update_hitbox()
        self.update_barrage()

        for bullet in self.enemyBullets:
            bullet.update()

    # =====================================================
    # DRAW (BOSS ONLY)
    # =====================================================
    def draw(self, surface: pygame.Surface, camera):
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

    # =====================================================
    # BARRAGE DRAW (CALLED FROM BATTLE SCREEN)
    # =====================================================
    def draw_barrage(self, surface, camera) -> None:
        if self.barrage_phase == self.PHASE_OFF:
            return

        color = (255, 0, 0) if self.barrage_phase == self.PHASE_RED else (255, 165, 0)

        for rect in self.barrage_rects:
            pygame.draw.rect(
                surface,
                color,
                (
                    camera.world_to_screen_x(rect.x),
                    camera.world_to_screen_y(rect.y),
                    rect.width,
                    rect.height,
                ),
            )
