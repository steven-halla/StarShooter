from __future__ import annotations

import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class AcidLauncher(Enemy):
    def __init__(self) -> None:
        super().__init__()

        # appearance
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # player tracking
        self.target_player = None
        self.last_player_x: float | None = None
        self.last_player_y: float | None = None

        # bullet appearance
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20

        # firing
        self.weapon_speed: float = 6.0
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = pygame.time.get_ticks()

        # gameplay
        self.enemyHealth: int = 50
        self.maxHealth: int = 50

        # bullets owned by this enemy
        self.enemyBullets: list[Bullet] = []

        self.acid_launcher_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.acid_launcher_image  # 🔑 REQUIRED

    def shoot_spines(self, state=None) -> None:
        if self.last_player_x is None or self.last_player_y is None:
            return

        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        dx = self.last_player_x - cx
        dy = self.last_player_y - cy

        length = math.hypot(dx, dy)
        if length == 0:
            return

        dx /= length
        dy /= length

        bullet = Bullet(cx, cy)
        bullet.dx = dx * self.weapon_speed
        bullet.speed = dy * self.weapon_speed

        bullet.width = self.bulletWidth
        bullet.height = self.bulletHeight
        bullet.color = self.bulletColor
        bullet.damage = 10

        if state is not None:
            state.enemy_bullets.append(bullet)
        self.enemyBullets.append(bullet)

    def update(self, state) -> None:
        super().update(state)
        self.update_hitbox()

        # track player every frame
        if self.target_player is not None:
            self.last_player_x = self.target_player.x
            self.last_player_y = self.target_player.y

        now = pygame.time.get_ticks()

        if now - self.last_shot_time >= self.fire_interval_ms:
            self.shoot_single_bullet_aimed_at_player(
                bullet_speed=4.0,
                bullet_width=20,
                bullet_height=20,
                bullet_color=self.bulletColor,
                bullet_damage=10,
                state=state
            )

            self.last_shot_time = now

        for bullet in self.enemyBullets:
            bullet.update()

    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.acid_launcher_image.subsurface(sprite_rect)

        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)
        surface.blit(scaled_sprite, (screen_x, screen_y))

        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)
