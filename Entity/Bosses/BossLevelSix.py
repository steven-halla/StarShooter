import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet

#NOTE NOTE NOTE
# We need to add more to this boss, it should have 3 phases to it

class BossLevelSix(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()

        self.width = 40
        self.height = 40
        self.color = GlobalConstants.RED

        self.enemyBullets: list[Bullet] = []
        self.enemyHealth = 400
        self.maxHealth = 400


        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

        # -------------------------
        # BARRAGE GRID
        # -------------------------
        self.BARRAGE_SIZE = 32
        self.BARRAGE_ROWS = 5
        self.BARRAGE_COLS = 8

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
        self.touch_damage: int = 10



    # =====================================================
    # BUILD FIXED MASTER GRID (ONCE)
    # =====================================================
    def build_barrage_grid(self) -> None:
        # Check if camera is properly initialized
        if self.camera is None:
            return

        self.barrage_rects.clear()
        SIZE = self.BARRAGE_SIZE

        BASE_COORDS = [
            # Row 1
            (30, 60), (64, 60), (98, 60), (132, 60),
            (166, 60), (200, 60), (234, 60), (268, 60),

            # Row 2
            (30, 94), (64, 94), (98, 94), (132, 94),
            (166, 94), (200, 94), (234, 94), (268, 94),

            # Row 3
            (30, 128), (64, 128), (98, 128), (132, 128),
            (166, 128), (200, 128), (234, 128), (268, 128),

            # Row 4
            (30, 162), (64, 162), (98, 162), (132, 162),
            (166, 162), (200, 162), (234, 162), (268, 162),

            # Row 5
            (30, 196), (64, 196), (98, 196), (132, 196),
            (166, 196), (200, 196), (234, 196), (268, 196),


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
    def rebuild_active_barrage(self) -> None:
        print(f"\n=== REBUILDING ACTIVE BARRAGE ===")

        # Check if master grid is built
        if not self._grid_built or len(self.barrage_rects) == 0:
            print(f"Cannot rebuild active barrage: master grid not built (grid_built={self._grid_built}, rects={len(self.barrage_rects)})")
            return

        self.active_barrage_rects.clear()

        cols = self.BARRAGE_COLS
        rows = self.BARRAGE_ROWS

        print(f"Rebuilding with {rows} rows and {cols} columns")

        for row_index in range(rows):
            start = row_index * cols
            end = start + cols

            # Safety check to prevent index errors
            if start >= len(self.barrage_rects) or end > len(self.barrage_rects):
                print(f"Warning: Invalid indices for row {row_index}: start={start}, end={end}, total rects={len(self.barrage_rects)}")
                continue

            row_rects = self.barrage_rects[start:end]

            # Safety check for random.sample
            num_to_choose = min(3, len(row_rects))
            if num_to_choose == 0:
                print(f"Warning: No rectangles available in row {row_index}")
                continue

            # pick 3 UNIQUE rects from this row
            chosen = random.sample(row_rects, num_to_choose)
            print(f"Row {row_index}: Selected {len(chosen)} rectangles")

            for rect in chosen:
                self.active_barrage_rects.append(
                    pygame.Rect(
                        rect.x,
                        rect.y,
                        rect.width,
                        rect.height,
                    )
                )

        print(f"Active barrage rebuilt with {len(self.active_barrage_rects)} rectangles")
    # =====================================================
    # BARRAGE PHASE CONTROLLER
    # =====================================================
    def update_barrage(self, player=None) -> None:
        print(f"\n=== UPDATE BARRAGE ===")
        print(f"Current phase: {self.barrage_phase}")
        print(f"May fire barrage: {self.may_fire_barrage}")
        print(f"Grid built: {self._grid_built}")
        print(f"Barrage built this cycle: {self._barrage_built_this_cycle}")

        now = pygame.time.get_ticks()
        elapsed = now - self.barrage_timer

        if not self.may_fire_barrage:
            print("Barrage not updated: may_fire_barrage is False")
            return

        # Ensure camera is available for grid building
        if self.camera is None:
            print("Barrage not updated: camera is None")
            return

        if self.barrage_phase == self.PHASE_RED:
            print(f"In RED phase, elapsed: {elapsed}ms, threshold: {self.RED_MS}ms")
            if elapsed >= self.RED_MS:
                print("\n=== MASTER GRID (ALL COORDS) ===")
                for i, rect in enumerate(self.barrage_rects):
                    print(f"[{i:02d}] x={rect.x}, y={rect.y}")

                print("\n=== TEMP GRID (ACTIVE / DRAWN) ===")
                for i, rect in enumerate(self.active_barrage_rects):
                    print(f"[{i:02d}] x={rect.x}, y={rect.y}")

                if player:
                    print("\n=== PLAYER POSITION ===")
                    print(f"Player x={player.x}, y={player.y}")
                    print(f"Player hitbox: x={player.hitbox.x}, y={player.hitbox.y}, width={player.hitbox.width}, height={player.hitbox.height}")

                print("Transitioning from RED to ORANGE phase")
                self.barrage_phase = self.PHASE_ORANGE
                self.barrage_timer = now

        elif self.barrage_phase == self.PHASE_ORANGE:
            print(f"In ORANGE phase, elapsed: {elapsed}ms, threshold: {self.ORANGE_MS}ms")
            if elapsed >= self.ORANGE_MS:
                print("Transitioning from ORANGE to OFF phase")
                self.barrage_phase = self.PHASE_OFF
                self.barrage_timer = now
                self.active_barrage_rects.clear()
                self._barrage_built_this_cycle = False

        elif self.barrage_phase == self.PHASE_OFF:
            print(f"In OFF phase, elapsed: {elapsed}ms, threshold: {self.OFF_MS}ms")
            if elapsed >= self.OFF_MS:
                # Always try to build the grid if it's not built yet
                if not self._grid_built:
                    print("Grid not built yet, building now...")
                    self.build_barrage_grid()

                # If grid building failed, we can't proceed
                if not self._grid_built:
                    print("Grid building failed, staying in OFF phase")
                    self.barrage_timer = now  # Reset timer to try again later
                    return

                if not self._barrage_built_this_cycle:
                    print("Rebuilding active barrage...")
                    self.rebuild_active_barrage()
                    self._barrage_built_this_cycle = True

                print("Transitioning from OFF to RED phase")
                self.barrage_phase = self.PHASE_RED
                self.barrage_timer = now

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, state, player=None) -> None:


        super().update(state)

        self._barrage_drawn_this_frame = False  # 🔑 reset once per frame

        if not self.is_active:
            print("Boss not updated: not active")
            return

        if self.camera is None:
            print("Boss not updated: camera is None")
            return

        self.update_hitbox()

        # Force initial grid building if needed
        if not self._grid_built and self.camera is not None:
            self.build_barrage_grid()

        self.update_barrage(player)

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
        print(f"\n=== DRAW BARRAGE STATUS ===")
        print(f"Barrage phase: {self.barrage_phase}")
        print(f"May fire barrage: {self.may_fire_barrage}")
        print(f"Active barrage rects count: {len(self.active_barrage_rects)}")

        if self._barrage_drawn_this_frame:
            print("Barrage not drawn: already drawn this frame")
            return
        self._barrage_drawn_this_frame = True

        if self.barrage_phase == self.PHASE_OFF:
            print("Barrage not drawn: phase is OFF")
            return

        if not hasattr(self, "_barrage_surface"):
            self._barrage_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        self._barrage_surface.fill((0, 0, 0, 0))

        color = (255, 0, 0) if self.barrage_phase == self.PHASE_RED else (255, 165, 0)
        print(f"Drawing barrage with color: {color}")

        z = camera.zoom

        for rect in self.active_barrage_rects:
            # ✅ FIX: scale rect size by camera.zoom
            screen_x = camera.world_to_screen_x(rect.x)
            screen_y = camera.world_to_screen_y(rect.y)
            screen_w = int(rect.width * z)
            screen_h = int(rect.height * z)

            print(f"Drawing rect at screen coords: x={screen_x}, y={screen_y}, w={screen_w}, h={screen_h}")

            pygame.draw.rect(
                self._barrage_surface,
                color,
                (screen_x, screen_y, screen_w, screen_h),
            )

        surface.blit(self._barrage_surface, (0, 0))
        print("Barrage drawn successfully")
    # =====================================================
    # DAMAGE PLAYER — TEMP GRID ONLY
    # =====================================================
    def apply_barrage_damage(self, player) -> None:
        print(f"\n=== APPLY BARRAGE DAMAGE ===")
        if self.barrage_phase != self.PHASE_ORANGE:
            print(f"No damage applied: barrage phase is {self.barrage_phase}, not ORANGE")
            return
        if player.invincible:
            print(f"No damage applied: player is invincible")
            return

        player_rect = player.hitbox
        print(f"Player hitbox: x={player_rect.x}, y={player_rect.y}, w={player_rect.width}, h={player_rect.height}")

        for i, rect in enumerate(self.active_barrage_rects):
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

            print(f"Damage rect {i}: x={damage_rect.x}, y={damage_rect.y}, w={damage_rect.width}, h={damage_rect.height}")

            collision = player_rect.colliderect(damage_rect)
            print(f"Collision with damage rect {i}: {collision}")

            if collision:
                print(f"Player hit by barrage! Damage applied: 30")
                # player.shipHealth -= 30

                player.shield_system.take_damage(75)
                player.on_hit()
                return
