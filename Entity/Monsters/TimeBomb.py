import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class TimeBomb(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.name: str = "TimeBomb"

        # gameplay
        self.enemyHealth: int = 1
        self.moveSpeed: float = 0.4   # 🔑 REQUIRED OR IT WILL NOT MOVE'
        self.bullet_damage = 0

        self.spore_flower_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.spore_flower_image  # 🔑 REQUIRED
        self.is_active = True
        self.timer_vanish_enemy_ms: int = 20000
        self.time_bomb_timer_start: int = 0
        self.time_needed_to_diffuse: int = 10000
        self.diffuse_time_bomb_timer: int = 0


    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self, state) -> None:
        super().update(state)

        if not self.is_active or not self.camera or not self.target_player:
            return

        now = pygame.time.get_ticks()
        camera = self.camera
        player = self.target_player

        # -----------------------------
        # FULL RECT VISIBILITY CHECK
        # -----------------------------
        visible_top = camera.y
        visible_bottom = camera.y + (camera.window_height / camera.zoom)

        enemy_fully_on_screen = (
                self.y >= visible_top
                and self.y + self.height <= visible_bottom
        )

        player_fully_on_screen = (
                player.y >= visible_top
                and player.y + player.height <= visible_bottom
        )

        # -----------------------------
        # VANISH TIMER (ON SCREEN ONLY)
        # -----------------------------
        if enemy_fully_on_screen and player_fully_on_screen:
            if self.time_bomb_timer_start == 0:
                self.time_bomb_timer_start = now
                print("[TimeBomb] vanish timer started")

            vanish_elapsed = now - self.time_bomb_timer_start
            vanish_remaining = max(
                0, self.timer_vanish_enemy_ms - vanish_elapsed
            )

            print(
                f"[TimeBomb Vanish Timer] "
                f"elapsed={vanish_elapsed}ms "
                f"remaining={vanish_remaining}ms "
                f"limit={self.timer_vanish_enemy_ms}ms"
            )

            if vanish_elapsed >= self.timer_vanish_enemy_ms:
                print("[TimeBomb] vanished (timeout)")
                self.enemyHealth = 0
                self.is_active = False
                self.time_bomb_timer_start = 0
                self.diffuse_time_bomb_timer = 0
                return
        else:
            self.time_bomb_timer_start = 0

        # -----------------------------
        # DIFFUSE TIMER (INSIDE RECT ONLY)
        # -----------------------------
        if self.hitbox.colliderect(player.hitbox):
            if self.diffuse_time_bomb_timer == 0:
                self.diffuse_time_bomb_timer = now
                print("[TimeBomb] diffuse timer started")

            diffuse_elapsed = now - self.diffuse_time_bomb_timer
            diffuse_remaining = max(
                0, self.time_needed_to_diffuse - diffuse_elapsed
            )

            print(
                f"[TimeBomb Diffuse Timer] "
                f"elapsed={diffuse_elapsed}ms "
                f"remaining={diffuse_remaining}ms "
                f"limit={self.time_needed_to_diffuse}ms"
            )

            if diffuse_elapsed >= self.time_needed_to_diffuse:
                print("[TimeBomb] diffused successfully")
                self.enemyHealth = 0
                self.is_active = False
                self.time_bomb_timer_start = 0
                self.diffuse_time_bomb_timer = 0
                return
        else:
            self.diffuse_time_bomb_timer = 0

        # -----------------------------
        # MOVEMENT
        # -----------------------------
        self.enemy_move_random(interval_ms=3000)
        self.update_hitbox()
    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if self.target_player and self.hitbox.colliderect(self.target_player.hitbox):
            color = (0, 0, 255)  # blue when player inside
        else:
            color = (255, 0, 0)  # red otherwise

        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, color, (hb_x, hb_y, hb_w, hb_h), 2)

    # --------------------------------------------------
    # RANDOM MOVEMENT (3s INTERVAL)
    # --------------------------------------------------
    def enemy_move_random(self, interval_ms: int) -> None:
        now = pygame.time.get_ticks()

        # lazy init (no __init__ edits)
        if not hasattr(self, "_dir"):
            self._dir = random.randint(0, 3)  # 0=left, 1=right, 2=up, 3=down
            self._next_dir_time = now + interval_ms

        # change direction on timer
        if now >= self._next_dir_time:
            self._dir = random.randint(0, 3)
            self._next_dir_time = now + interval_ms

        # MOVE via MoveRectangle (normalized, correct)
        if self._dir == 0:
            self.mover.enemy_move_left(self)
        elif self._dir == 1:
            self.mover.enemy_move_right(self)
        elif self._dir == 2:
            self.mover.enemy_move_up(self)
        elif self._dir == 3:
            self.mover.enemy_move_down(self)


