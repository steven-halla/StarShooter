import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelSeven(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.last_bile_shot_time: int | None = None
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0

        # -------------------------
        # APPEARANCE
        # -------------------------
        self.width = 90
        self.height = 16
        self.color = GlobalConstants.RED

        # -------------------------
        # BULLETS
        # -------------------------
        self.bulletColor = GlobalConstants.SKYBLUE
        self.bulletWidth = 15
        self.bulletHeight = 15
        self.weapon_speed = 5.0
        self.enemyBullets: list[Bullet] = []

        # -------------------------
        # FIRING TIMERS
        # -------------------------
        self.fire_interval_ms = 1000  # fires every second
        self.last_shot_time = pygame.time.get_ticks()

        self.triple_fire_interval_ms = 3000
        self.last_triple_shot_time = pygame.time.get_ticks()

        # -------------------------
        # MOVEMENT
        # -------------------------
        self.moveSpeed = 2.0
        self.move_interval_ms = 3000
        self.last_move_toggle = pygame.time.get_ticks()
        self.move_direction = random.choice([-1, 1])

        # -------------------------
        # STATS
        # -------------------------
        self.enemyHealth = 400
        self.exp = 5
        self.credits = 50

        # -------------------------
        # SPRITE
        # -------------------------
        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    # =====================================================
    # RADIAL BILE BURST (8–12 bullets, random directions)
    # =====================================================
    def _shoot_bile(self) -> None:
        now = pygame.time.get_ticks()

        if self.last_bile_shot_time is None:
            self.last_bile_shot_time = now
            return

        if now - self.last_bile_shot_time < 1000:
            return

        self.last_bile_shot_time = now

        bullet_x = self.x + self.width
        bullet_y = self.y + self.height // 2 - self.bulletHeight // 2

        bullet = Bullet(bullet_x, bullet_y)
        bullet.color = self.bulletColor
        bullet.width = self.bulletWidth
        bullet.height = self.bulletHeight
        bullet.damage = 10

        # 50% stage speed boost
        speed = self.weapon_speed * 1.5

        # 🔒 HARD OVERRIDE — RIGHT ONLY
        bullet.dx = speed
        bullet.dy = 0

        # KILL ANY OTHER MOTION PATHS
        if hasattr(bullet, "direction_x"):
            bullet.direction_x = 0
        if hasattr(bullet, "direction_y"):
            bullet.direction_y = 0
        if hasattr(bullet, "speed"):
            bullet.speed = 0  # Bullet.update must NOT use this

        bullet.rect.width = bullet.width
        bullet.rect.height = bullet.height

        self.enemyBullets.append(bullet)

        print(f"[BOSS FIRE TEST] dx={bullet.dx} dy={bullet.dy}")



    # =====================================================
    # UPDATE
    # =====================================================
    def update(self) -> None:
        super().update()
        if not self.is_active:
            return

        self.update_hitbox()

        if self.camera is None:
            return

        self.moveAI()
        now = pygame.time.get_ticks()

        # FIRE RADIAL BURST EVERY SECOND
        if now - self.last_shot_time >= self.fire_interval_ms:
            self._shoot_bile()
            self.last_shot_time = now

        for bullet in self.enemyBullets:
            bullet.update()

    # =====================================================
    # MOVEMENT
    # =====================================================
    def moveAI(self) -> None:
        if self.camera is None:
            return

        now = pygame.time.get_ticks()
        window_width = self.camera.window_width / self.camera.zoom

        if now - self.last_move_toggle >= self.move_interval_ms:
            self.last_move_toggle = now
            self.move_direction = random.choice([-1, 1])

        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        if self.x <= 0:
            self.x = 0
            self.move_direction = 1
        elif self.x + self.width >= window_width:
            self.x = window_width - self.width
            self.move_direction = -1

    # =====================================================
    # DRAW
    # =====================================================
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
