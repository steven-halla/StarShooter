import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class FireLauncher(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.has_retreat_triggered = False

        # -------------------------
        # BILE BURST FIRE
        # -------------------------
        self.bile_burst_count = 0
        self.bile_burst_max = 3
        self.bile_burst_delay_ms = 500
        self.last_bile_shot_time = 0
        self.is_bile_bursting = False

        self.burst_cooldown_ms = 3500
        self.last_burst_time = pygame.time.get_ticks() - self.burst_cooldown_ms

        # -------------------------
        # ENEMY APPEARANCE
        # -------------------------
        self.width: int = 40
        self.height: int = 40
        self.color = GlobalConstants.RED

        # -------------------------
        # BULLET APPEARANCE
        # -------------------------
        self.bulletColor = GlobalConstants.SKYBLUE
        self.bulletWidth = 20
        self.bulletHeight = 20

        # -------------------------
        # BULLET MOVEMENT
        # -------------------------
        self.bileSpeed = 3

        # -------------------------
        # GAMEPLAY STATS
        # -------------------------
        self.speed: float = 1.0
        self.enemyHealth: int = 5
        self.exp: int = 1
        self.credits: int = 5
        self.is_retreating = False
        self.retreat_start_y = None

        self.enemyBullets: list[Bullet] = []

        # -------------------------
        # AI MOVEMENT STATE (DO NOT TOUCH)
        # -------------------------
        self.moveSpeed: float = 2.0
        self.edge_padding: int = 30
        self.move_direction: int = random.choice([-1, 1])

        self.move_interval_ms: int = 3000
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True

        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def _shoot_bile(self) -> None:
        if self.target_player is None:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        px = self.target_player.hitbox.centerx
        py = self.target_player.hitbox.centery

        dx = px - cx
        dy = py - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        bullet = Bullet(cx, cy)
        bullet.color = self.bulletColor
        bullet.width = self.bulletWidth
        bullet.height = self.bulletHeight

        bullet.dx = dx * self.bileSpeed
        bullet.speed = -dy * self.bileSpeed  # ✅ FIX

        bullet.rect.width = bullet.width
        bullet.rect.height = bullet.height
        bullet.damage = 10

        self.enemyBullets.append(bullet)
    # -------------------------
    # # FIRE BILE (TARGET PLAYER)
    # # -------------------------
    # def _shoot_bile(self) -> None:
    #     if self.target_player is None:
    #         return
    #
    #     cx = self.x + self.width / 2
    #     cy = self.y + self.height
    #
    #     px = self.target_player.hitbox.centerx
    #     py = self.target_player.hitbox.centery
    #
    #     dx = px - cx
    #     dy = py - cy
    #     dist = math.hypot(dx, dy)
    #     if dist == 0:
    #         return
    #
    #     dx /= dist
    #     dy /= dist
    #
    #     bullet = Bullet(cx, cy)
    #     bullet.color = self.bulletColor
    #     bullet.width = self.bulletWidth
    #     bullet.height = self.bulletHeight
    #     bullet.dx = dx * self.bileSpeed
    #     bullet.speed = dy * self.bileSpeed
    #     bullet.rect.width = bullet.width
    #     bullet.rect.height = bullet.height
    #     bullet.damage = 10
    #
    #     self.enemyBullets.append(bullet)

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self) -> None:
        super().update()
        if not self.is_active:
            return
        self.update_hitbox()

        # ⚠️ MOVEMENT LOGIC — UNCHANGED
        self.moveAI()

        now = pygame.time.get_ticks()

        # -------------------------
        # START BURST (COOLDOWN GATED)
        # -------------------------
        if (
            not self.is_bile_bursting
            and now - self.last_burst_time >= self.burst_cooldown_ms
        ):
            self.is_bile_bursting = True
            self.bile_burst_count = 0
            self.last_bile_shot_time = now
            self.last_burst_time = now
            print("BILE BURST START")

        # -------------------------
        # HANDLE BURST
        # -------------------------
        if self.is_bile_bursting:
            if now - self.last_bile_shot_time >= self.bile_burst_delay_ms:
                self._shoot_bile()
                self.bile_burst_count += 1
                self.last_bile_shot_time = now
                print(f"BILE SHOT {self.bile_burst_count}")

                if self.bile_burst_count >= self.bile_burst_max:
                    self.is_bile_bursting = False
                    print("BILE BURST END")

        # -------------------------
        # MOVE BULLETS
        # -------------------------
        for bullet in self.enemyBullets:
            bullet.x += bullet.dx
            bullet.y += bullet.speed

    # -------------------------
    # AI MOVEMENT (UNCHANGED)
    # -------------------------
    def moveAI(self) -> None:
        if not self.mover.enemy_on_screen(self, self.camera):
            return

        # One-time init
        if not hasattr(self, "base_y"):
            self.base_y = self.y
            self.move_direction_y = 1

        screen_bottom_world = (
                self.camera.y
                + (self.camera.window_height / self.camera.zoom)
        )

        # -------------------------
        # START RETREAT
        # -------------------------
        if (
                not self.is_retreating
                and self.y + self.height >= screen_bottom_world - 50
        ):
            self.is_retreating = True
            self.retreat_start_y = self.y
            print(f"[RETREAT START] y={self.y:.2f}")

        # -------------------------
        # RETREAT MOVEMENT (UP 200px)
        # -------------------------
        if self.is_retreating:
            self.mover.enemy_move_up(self)

            moved = self.retreat_start_y - self.y
            print(f"[RETREAT MOVE] y={self.y:.2f} moved={moved:.2f}")

            # Stop retreat after 200px
            if moved >= 200:
                self.is_retreating = False
                self.base_y = self.y  # reset patrol center
                print("[RETREAT END]")
            return

        # -------------------------
        # NORMAL PATROL (UNCHANGED)
        # -------------------------
        desired_top = self.base_y - 100
        desired_bottom = self.base_y + 100

        cam_top = self.camera.y
        cam_bottom = (
                self.camera.y
                + (self.camera.window_height / self.camera.zoom)
                - self.height
        )

        patrol_top = max(desired_top, cam_top)
        patrol_bottom = min(desired_bottom, cam_bottom)

        if self.move_direction_y > 0:
            self.mover.enemy_move_down(self)
        else:
            self.mover.enemy_move_up(self)

        if self.y <= patrol_top:
            self.y = patrol_top
            self.move_direction_y = 1
        elif self.y >= patrol_bottom:
            self.y = patrol_bottom
            self.move_direction_y = -1

        print(f"[AI MOVE] y={self.y:.2f} dir={self.move_direction_y}")

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

        scale = camera.zoom
        sprite = pygame.transform.scale(
            sprite, (int(self.width * scale), int(self.height * scale))
        )

        surface.blit(
            sprite,
            (
                camera.world_to_screen_x(self.x),
                camera.world_to_screen_y(self.y),
            ),
        )

        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)
