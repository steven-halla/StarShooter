import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelOne(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0

        # -------------------------
        # APPEARANCE
        # -------------------------
        self.width = 40
        self.height = 40
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
        self.fire_interval_ms = 1000
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
        self.enemyHealth = 111
        self.exp = 5
        self.credits = 50

        # -------------------------
        # SPRITE
        # -------------------------
        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    # =====================================================
    # ORIGINAL SINGLE SHOT (UNCHANGED)
    # =====================================================
    def _shoot_bile(self) -> None:
        bullet_x = self.x + self.width // 2 - self.bulletWidth // 2
        bullet_y = self.y + self.height

        bullet = Bullet(bullet_x, bullet_y)
        bullet.color = self.bulletColor
        bullet.width = self.bulletWidth
        bullet.height = self.bulletHeight
        bullet.speed = self.weapon_speed
        bullet.damage = 10

        bullet.rect.width = bullet.width
        bullet.rect.height = bullet.height

        self.enemyBullets.append(bullet)

    # =====================================================
    # TRIPLE FIRE — SHOOTS AT PLAYER LAST POSITION
    # =====================================================
    def shoot_triple_line(self) -> None:
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

        perp_x = -dy
        perp_y = dx

        spacing = 30
        offsets = [-spacing, 0, spacing]

        for offset in offsets:
            bx = cx + perp_x * offset
            by = cy + perp_y * offset

            bullet = Bullet(bx, by)
            bullet.dx = dx * self.weapon_speed
            bullet.speed = dy * self.weapon_speed
            bullet.width = self.bulletWidth
            bullet.height = self.bulletHeight
            bullet.color = self.bulletColor
            bullet.damage = 10

            bullet.rect.width = bullet.width
            bullet.rect.height = bullet.height

            self.enemyBullets.append(bullet)

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

        # ORIGINAL FIRE
        if now - self.last_shot_time >= self.fire_interval_ms:
            self._shoot_bile()
            self.last_shot_time = now

        # TRIPLE FIRE
        if now - self.last_triple_shot_time >= self.triple_fire_interval_ms:
            self.shoot_triple_line()
            self.last_triple_shot_time = now

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
