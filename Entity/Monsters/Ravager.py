from __future__ import annotations

import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Entity.Monsters.MonsterAttacks.Napalm import Napalm
from Weapons.Bullet import Bullet


class Ravager(Enemy):
    def __init__(self) -> None:
        super().__init__()
        # napalm storage
        self.napalm_list = []
        self.width = 16
        self.pending_napalm = None
        self.napalm_damage = 10
        self.height = 16
        self.color = GlobalConstants.RED

        self.camera = None
        self.target_player = None

        self.move_speed = 2.5
        self.flee_distance = 200
        self.edge_buffer = 40

        # NORMAL FIRE (DO NOT TOUCH)
        self.weapon_speed = 1.0
        self.fire_interval_ms = 2000
        self.last_shot_time = pygame.time.get_ticks()

        # NAPALM FIRE
        self.napalm_interval_ms = 1000
        self.last_napalm_time = pygame.time.get_ticks()

        self.enemyHealth = 200
        self.maxHealth = 200
        self.enemyBullets: list[Bullet] = []

        self.ravager_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.ravager_image  # 🔑 REQUIRED

    # =========================
    # NORMAL FIRE (UNCHANGED)
    # =========================
    def shoot(self) -> None:
        if self.target_player is None:
            return

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

    # =========================
    # NAPALM FIRE
    def spawn_napalm(self) -> None:
        if self.target_player is None:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        px = self.target_player.hitbox.centerx
        py = self.target_player.hitbox.centery

        napalm = Napalm(
            start_x=cx,
            start_y=cy,
            target_x=px,
            target_y=py
        )

        self.pending_napalm = napalm
        napalm.damage = self.napalm_damage  # ← THIS WAS MISSING

        # print("NAPALM SPAWNED", cx, cy)

    def update(self, state) -> None:
        # ⛔ DO NOTHING unless player is on screen
        if self.camera is None or self.target_player is None:
            return

        player_screen_y = self.camera.world_to_screen_y(self.target_player.y)

        if player_screen_y < 0 or player_screen_y > self.camera.window_height:
            return
        ravager_screen_y = self.camera.world_to_screen_y(self.y)

        if ravager_screen_y + self.height < 0 or ravager_screen_y > self.camera.window_height:
            return
        super().update(state)

        self.update_hitbox()

        # -----------------
        # MOVEMENT (unchanged)
        # -----------------
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

        # -----------------
        # FIRING TIMERS
        # -----------------
        now = pygame.time.get_ticks()

        if now - self.last_shot_time >= self.fire_interval_ms:
            self.shoot()
            self.last_shot_time = now
        # TEMP TEST — remove later
        if pygame.time.get_ticks() % 3000 < 16:
            self.spawn_napalm()

        # if now - self.last_napalm_time >= self.napalm_interval_ms:
        #     self.shoot_napalm()
        #     self.last_napalm_time = now

        # -----------------
        # BULLET UPDATE
        # -----------------
        now = pygame.time.get_ticks()

        now = pygame.time.get_ticks()

        for bullet in list(self.enemyBullets):

            if getattr(bullet, "is_napalm", False):

                if not bullet.has_stopped:
                    dx = bullet.x - bullet.start_x
                    dy = bullet.y - bullet.start_y
                    traveled = math.hypot(dx, dy)

                    if traveled >= bullet.travel_distance:
                        bullet.dx = 0
                        bullet.speed = 0
                        bullet.has_stopped = True
                        bullet.stop_time = now
                        # print("NAPALM STOPPED at", bullet.x, bullet.y)
                    else:
                        bullet.update()

                else:
                    if now - bullet.stop_time >= 3000:
                        # print("NAPALM EXPIRED")
                        self.enemyBullets.remove(bullet)

                continue

            # normal bullets ONLY
            bullet.update()
        napalm = self.pending_napalm
        self.pending_napalm = None
        return napalm


    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)  # 🔑 REQUIRED

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
