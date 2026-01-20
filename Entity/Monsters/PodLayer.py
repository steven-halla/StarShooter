import random

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet

# this classs lays AOE abilites ont he field as a support unit
class PodLayer(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        self.freeze_start_time = None
        self.freeze_duration_ms = 2000  # 2 seconds

        # enemy appearance
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # bullet appearance
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 9
        self.bulletHeight: int = 9

        # firing + bullet movement
        self.bileSpeed: int = 3
        self.fire_interval_ms: int = 2000
        self.last_shot_time: int = pygame.time.get_ticks()

        # gameplay stats
        self.speed: float = 1.0
        self.enemyHealth: int = 20
        self.exp: int = 1
        self.credits: int = 5

        self.enemyBullets: list[Bullet] = []

        # AI movement
        self.moveSpeed: float = 2.0
        self.edge_padding: int = 30
        self.move_direction: int = random.choice([-1, 1])

        self.move_interval_ms: int = 3000
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True

        self.tri_spiter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.tri_spiter_image

    def shoot_triple_bullets(self) -> None:
        base_x = self.x + self.width // 2 - self.bulletWidth // 2
        bullet_y = self.y + self.height

        offsets = [-15, 0, 15]

        for offset in offsets:
            bullet_x = base_x + offset
            bullet = Bullet(bullet_x, bullet_y)

            bullet.color = self.bulletColor
            bullet.width = self.bulletWidth
            bullet.height = self.bulletHeight
            bullet.damage = 10

            # VECTOR-BASED MOTION
            bullet.vy = self.bileSpeed

            if offset < 0:
                bullet.vx = -3
            elif offset > 0:
                bullet.vx = 3
            else:
                bullet.vx = 0

            bullet.update_rect()
            self.enemyBullets.append(bullet)

    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return

        now = pygame.time.get_ticks()

        if self.freeze_start_time is not None:
            if now - self.freeze_start_time >= self.freeze_duration_ms:
                self.freeze_start_time = None
        else:
            if hasattr(self, "target_player") and self.target_player is not None:
                if self.target_player.x > self.x:
                    self.mover.enemy_move_right(self)
                elif self.target_player.x < self.x:
                    self.mover.enemy_move_left(self)

                aligned = abs(self.x - self.target_player.x) <= 5
                if aligned:
                    self.freeze_start_time = now

            self.moveAI()

        aligned = abs(self.x - self.target_player.x) <= 5
        if aligned and self.freeze_start_time is not None:
            if now - self.last_shot_time >= self.fire_interval_ms:
                self.shoot_triple_bullets()
                self.last_shot_time = now

        # VECTOR UPDATE
        for bullet in self.enemyBullets:
            bullet.x += bullet.vx
            bullet.y += bullet.vy
            bullet.update_rect()

        self.update_hitbox()

    def moveAI(self) -> None:
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        now = pygame.time.get_ticks()

        if now - self.last_move_toggle >= self.move_interval_ms:
            self.is_moving = not self.is_moving
            self.last_move_toggle = now
            if self.is_moving:
                self.move_direction = random.choice([-1, 1])

        if not self.is_moving:
            return

        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        if self.x <= self.edge_padding:
            self.x = self.edge_padding
            self.move_direction = 1
        elif self.x + self.width >= window_width - self.edge_padding:
            self.x = window_width - self.edge_padding - self.width
            self.move_direction = -1

    def draw(self, surface: pygame.Surface, camera):
        super().draw(surface, camera)

        sprite_rect = pygame.Rect(60, 128, 32, 32)
        sprite = self.tri_spiter_image.subsurface(sprite_rect)

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

    def _clamp_vertical(self) -> None:
        pass
