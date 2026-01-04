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

        self.width = 40
        self.height = 40
        self.color = GlobalConstants.RED

        self.enemyBullets: list[Bullet] = []
        self.enemyHealth = 400

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

        # -------------------------
        # BARRAGE GRID
        # -------------------------
        self.BARRAGE_SIZE = 32
        self.BARRAGE_ROWS = 6
        self.BARRAGE_COLS = 10

        # MASTER GRID (never modified)
        self.barrage_rects: list[pygame.Rect] = []

        # TEMP GRID (ONLY thing draw/damage ever uses)
        self.active_barrage_rects: list[pygame.Rect] = []

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

        self._grid_built = False
        self._barrage_built_this_cycle = False
        self._barrage_drawn_this_frame = False  # 🔑 HARD DRAW GUARD
        self.may_fire_barrage: bool = True


    # =====================================================
    # BUILD FIXED MASTER GRID (ONCE)
    # =====================================================
    def build_barrage_grid(self) -> None:
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

        self._grid_built = True

    # =====================================================
    # TEMP GRID — KEEP EXACTLY ONE TOP ROW TILE
    # =====================================================
    def rebuild_active_barrage(self) -> None:
        self.active_barrage_rects.clear()

        top_row = self.barrage_rects[:self.BARRAGE_COLS]
        chosen_rect = random.choice(top_row)

        self.active_barrage_rects.append(
            pygame.Rect(
                chosen_rect.x,
                chosen_rect.y,
                chosen_rect.width,
                chosen_rect.height,
            )
        )

    # =====================================================
    # BARRAGE PHASE CONTROLLER
    # =====================================================
    def update_barrage(self) -> None:
        now = pygame.time.get_ticks()
        elapsed = now - self.barrage_timer
        if not self.may_fire_barrage:
            return

        if self.barrage_phase == self.PHASE_RED:
            if elapsed >= self.RED_MS:
                print("\n=== MASTER GRID (ALL COORDS) ===")
                for i, rect in enumerate(self.barrage_rects):
                    print(f"[{i:02d}] x={rect.x}, y={rect.y}")

                print("\n=== TEMP GRID (ACTIVE / DRAWN) ===")
                for i, rect in enumerate(self.active_barrage_rects):
                    print(f"[{i:02d}] x={rect.x}, y={rect.y}")

                self.barrage_phase = self.PHASE_ORANGE
                self.barrage_timer = now

        elif self.barrage_phase == self.PHASE_ORANGE:
            if elapsed >= self.ORANGE_MS:
                self.barrage_phase = self.PHASE_OFF
                self.barrage_timer = now
                self.active_barrage_rects.clear()
                self._barrage_built_this_cycle = False

        elif self.barrage_phase == self.PHASE_OFF:
            if elapsed >= self.OFF_MS:
                if not self._grid_built:
                    self.build_barrage_grid()

                if not self._barrage_built_this_cycle:
                    self.rebuild_active_barrage()
                    self._barrage_built_this_cycle = True

                self.barrage_phase = self.PHASE_RED
                self.barrage_timer = now

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self) -> None:
        super().update()

        self._barrage_drawn_this_frame = False  # 🔑 reset once per frame

        if not self.is_active or self.camera is None:
            return

        self.update_hitbox()
        self.update_barrage()

        for bullet in self.enemyBullets:
            bullet.update()

    # =====================================================
    # DRAW BOSS
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
    # DRAW BARRAGE — ONCE PER FRAME, TEMP GRID ONLY

    def draw_barrage(self, surface, camera) -> None:
        if self._barrage_drawn_this_frame:
            return
        self._barrage_drawn_this_frame = True
        if self.barrage_phase == self.PHASE_OFF:
            return

        if not hasattr(self, "_barrage_surface"):
            self._barrage_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        self._barrage_surface.fill((0, 0, 0, 0))

        color = (255, 0, 0) if self.barrage_phase == self.PHASE_RED else (255, 165, 0)

        z = camera.zoom

        for rect in self.active_barrage_rects:
            # ✅ FIX: scale rect size by camera.zoom
            screen_x = camera.world_to_screen_x(rect.x)
            screen_y = camera.world_to_screen_y(rect.y)
            screen_w = int(rect.width * z)
            screen_h = int(rect.height * z)

            pygame.draw.rect(
                self._barrage_surface,
                color,
                (screen_x, screen_y, screen_w, screen_h),
            )

        surface.blit(self._barrage_surface, (0, 0))
    # =====================================================
    # DAMAGE PLAYER — TEMP GRID ONLY
    # =====================================================
    def apply_barrage_damage(self, player) -> None:
        if self.barrage_phase != self.PHASE_ORANGE:
            return
        if player.invincible:
            return

        player_rect = player.hitbox

        for rect in self.active_barrage_rects:
            # 🔥 HALF-SIZE DAMAGE AREA (centered)
            damage_w = rect.width // 2
            damage_h = rect.height // 2

            damage_x = rect.x + (rect.width - damage_w) // 2
            damage_y = rect.y + (rect.height - damage_h) // 2

            damage_rect = pygame.Rect(
                damage_x,
                damage_y,
                damage_w,
                damage_h,
            )

            if player_rect.colliderect(damage_rect):
                player.shipHealth -= 30
                player.on_hit()
                return
