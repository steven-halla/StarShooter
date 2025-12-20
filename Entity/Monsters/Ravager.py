from __future__ import annotations

import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class Ravager(Enemy):
    def __init__(self) -> None:
        super().__init__()

        self.width = 16
        self.height = 16
        self.color = GlobalConstants.RED

        self.camera = None
        self.target_player = None

        self.move_speed = 2.5
        self.flee_distance = 200
        self.edge_buffer = 40

        self.weapon_speed = 1.0
        self.fire_interval_ms = 2000
        self.last_shot_time = pygame.time.get_ticks()

        self.enemyHealth = 200
        self.enemyBullets: list[Bullet] = []

        self.ravager_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def shoot(self) -> None:
        if self.target_player is None:
            return

        # ONLY FIRE IF ON SCREEN
        cam_top = self.camera.y
        cam_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        if self.y + self.height < cam_top or self.y > cam_bottom:
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
        bullet.dx = dx * self.weapon_speed
        bullet.speed = dy * self.weapon_speed

        bullet.width = 20
        bullet.height = 20
        bullet.color = GlobalConstants.SKYBLUE
        bullet.damage = 10

        self.enemyBullets.append(bullet)

        print(
            "RAVAGER BULLET CREATED",
            "world:", cx, cy,
            "screen:",
            self.camera.world_to_screen_x(cx),
            self.camera.world_to_screen_y(cy),
        )

    def update(self) -> None:
        super().update()
        self.update_hitbox()

        move_x = 0.0
        move_y = 0.0

        if self.target_player is not None:
            dx = self.x - self.target_player.x
            dy = self.y - self.target_player.y
            dist = math.hypot(dx, dy)

            if dist < self.flee_distance and dist != 0:
                move_x += (dx / dist) * self.move_speed
                move_y += (dy / dist) * self.move_speed

        if self.camera is not None:
            left = 0
            right = (self.camera.window_width / self.camera.zoom) - self.width
            top = self.camera.y
            bottom = self.camera.y + (self.camera.window_height / self.camera.zoom) - self.height

            if self.x < left + self.edge_buffer:
                move_x += self.move_speed
            elif self.x > right - self.edge_buffer:
                move_x -= self.move_speed

            if self.y < top + self.edge_buffer:
                move_y += self.move_speed
            elif self.y > bottom - self.edge_buffer:
                move_y -= self.move_speed

        self.x += move_x
        self.y += move_y
        self.update_hitbox()

        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.fire_interval_ms:
            self.shoot()
            self.last_shot_time = now

        for bullet in self.enemyBullets:
            bullet.update()

    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.ravager_image.subsurface(sprite_rect)

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
