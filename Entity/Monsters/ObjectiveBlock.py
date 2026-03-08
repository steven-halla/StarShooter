import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class ObjectiveBlock(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.edge_padding: int = 30
        self.move_direction = 1
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.name: str = "ObjectiveBlock"
        self.enemyHealth: int = 1000
        self.moveSpeed: float = 1.9
        self.bullet_damage = 0

        self.player_hit: bool = False
        self.player_hit_timer_start: int = 0
        self.player_hit_immunity_ms: int = 3000

        self.spore_flower_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()
        self.enemy_image = self.spore_flower_image
        self.is_active = True
        self.timer_vanish_enemy_ms: int = 20000
        self.time_bomb_timer_start: int = 0
        self.time_needed_to_diffuse: int = 10000
        self.diffuse_time_bomb_timer: int = 0
        self.getting_shot: bool = False
        self.hit_by_shooting_up_block: bool = False

    def get_bullet_collision_rect(self, bullet) -> pygame.Rect | None:
        if hasattr(bullet, "hitbox") and bullet.hitbox is not None:
            return bullet.hitbox
        if hasattr(bullet, "rect") and bullet.rect is not None:
            return bullet.rect
        return None

    def update(self, state) -> None:
        super().update(state)
        print(self.player_hit)

        now = pygame.time.get_ticks()

        if self.player_hit and now - self.player_hit_timer_start >= self.player_hit_immunity_ms:
            self.player_hit = False

        if self.is_flashing:
            self.getting_shot = True
            self.player_hit = True
            self.player_hit_timer_start = now
            print("I am hit by player bullet")

            if self.enemyHealth < 1000:
                self.enemyHealth = 1000

            if pygame.time.get_ticks() - self.flash_start_time >= self.flash_duration_ms:
                self.is_flashing = False
        else:
            self.getting_shot = False

        if not self.is_active or not self.camera or not self.target_player:
            return

        self.update_hitbox()

        for bullet in list(state.enemy_bullets):
            if getattr(bullet, "owner", "") != "ShootingUpBlock":
                continue

            bullet_rect = self.get_bullet_collision_rect(bullet)
            if bullet_rect is None:
                continue

            if not bullet_rect.colliderect(self.hitbox):
                continue

            if self.player_hit:
                continue

            self.hit_by_shooting_up_block = True
            bullet.is_active = False
            if bullet in state.enemy_bullets:
                state.enemy_bullets.remove(bullet)

        camera = self.camera
        player = self.target_player

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

        if enemy_fully_on_screen and player_fully_on_screen:
            pass

    def draw(self, surface: pygame.Surface, camera):
        if self.hit_by_shooting_up_block:
            color = (0, 0, 255)
            self.enemyHealth = 0
            print(self.enemyHealth)
        elif self.player_hit:
            color = (255, 255, 0)
        elif self.target_player and self.hitbox.colliderect(self.target_player.hitbox):
            color = (0, 0, 255)
        else:
            color = (255, 0, 0)

        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, color, (hb_x, hb_y, hb_w, hb_h), 2)
