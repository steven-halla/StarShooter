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
        # appearance
        self.move_direction = 1  # start moving right
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.name: str = "ObjectiveBlock"
        # gameplay
        self.enemyHealth: int = 1000
        self.moveSpeed: float = 1.9   # 🔑 REQUIRED OR IT WILL NOT MOVE'
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
        self.getting_shot: bool = False
        self.hit_by_shooting_up_block: bool = False




    def update(self, state) -> None:
        super().update(state)
        # print(self.enemyHealth)
        if self.is_flashing:
            self.getting_shot = True
            if self.enemyHealth < 1000:
                self.enemyHealth = 1000
            if pygame.time.get_ticks() - self.flash_start_time >= self.flash_duration_ms:
                self.is_flashing = False
        else:
            self.getting_shot = False

        if not self.is_active or not self.camera or not self.target_player:
            return

        # -----------------------------
        # COLLISION WITH ENEMY BULLETS
        # -----------------------------
        for bullet in list(state.enemy_bullets):
            if bullet.rect.colliderect(self.hitbox):
                if getattr(bullet, "owner", "") == "ShootingUpBlock":
                    self.hit_by_shooting_up_block = True
                bullet.is_active = False # consume bullet
                if bullet in state.enemy_bullets:
                    state.enemy_bullets.remove(bullet)

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
            pass

        for bullet in state.player_bullets:
            if bullet.hitbox.colliderect(self.hitbox):
                print("I am hit")

        # -----------------------------
        # MOVEMENT
        # -----------------------------
        self.update_hitbox()
    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if getattr(self, "hit_by_shooting_up_block", False):
            color = (0, 0, 255)  # BLUE when hit by ShootingUpBlock
            self.enemyHealth = 0
            print(self.enemyHealth)
        elif self.target_player and self.hitbox.colliderect(self.target_player.hitbox):
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



