import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelFour(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0

        # -------------------------
        # SHIELD STATE
        # -------------------------
        self.shield_active: bool = True
        self.shield_toggle_interval_ms = 3000
        self.last_shield_toggle_time = pygame.time.get_ticks()

        # -------------------------
        # APPEARANCE
        # -------------------------
        self.width = 40
        self.height = 40

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
        self.triple_fire_interval_ms = 2000
        self.last_triple_shot_time = pygame.time.get_ticks()

        # -------------------------
        # STATS
        # -------------------------
        self.enemyHealth = 300
        self.exp = 5
        self.credits = 50

    # =====================================================
    # TRIPLE FIRE
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

        for offset in (-30, 0, 30):
            bullet = Bullet(cx + perp_x * offset, cy + perp_y * offset)
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
        if not self.is_active or self.camera is None:
            return

        self.update_hitbox()
        now = pygame.time.get_ticks()

        # 🔁 SHIELD TOGGLE
        if now - self.last_shield_toggle_time >= self.shield_toggle_interval_ms:
            self.shield_active = not self.shield_active
            self.last_shield_toggle_time = now

        # 🟣 ONLY FIRE WHEN SHIELD IS DOWN (PURPLE)
        if not self.shield_active:
            if now - self.last_triple_shot_time >= self.triple_fire_interval_ms:
                self.shoot_triple_line()
                self.last_triple_shot_time = now

        for bullet in self.enemyBullets:
            bullet.update()

    # =====================================================
    # DRAW
    # =====================================================
    def draw(self, surface: pygame.Surface, camera):
        scale = camera.zoom
        rect = pygame.Rect(
            camera.world_to_screen_x(self.x),
            camera.world_to_screen_y(self.y),
            int(self.width * scale),
            int(self.height * scale),
        )

        # 🔵 Shield UP
        # 🟣 Shield DOWN
        color = (0, 120, 255) if self.shield_active else (160, 0, 200)
        pygame.draw.rect(surface, color, rect)
