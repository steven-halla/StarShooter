import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class ShootingUpBlock(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.edge_padding: int = 30
        # __init__
        self.shoot_timer = Timer(3.0)


        # appearance
        self.move_direction = 1  # start moving right
        self.width: int = 16
        self.height: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.RED
        self.name: str = "ShootingUpBlock"

        # gameplay
        self.enemyHealth: int = 1000
        self.moveSpeed: float = 1.4   # 🔑 REQUIRED OR IT WILL NOT MOVE'
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





    def update(self, state) -> None:
        super().update(state)

        if self.is_flashing:
            self.getting_shot = True
            # __init__

            # update
            if self.shoot_timer.is_ready():
                # print("yes")
                self.shoot_single_down_vertical_y(
                    bullet_speed=-4,
                    bullet_width=16,
                    bullet_height=16,
                    bullet_color=GlobalConstants.RED,
                    bullet_damage=10,
                    state=state
                )
                self.shoot_timer.reset()
            if self.enemyHealth < 1000:
                self.enemyHealth = 1000
            if pygame.time.get_ticks() - self.flash_start_time >= self.flash_duration_ms:
                self.is_flashing = False
        else:
            self.getting_shot = False

        if not self.is_active or not self.camera or not self.target_player:
            return

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
        self.moveAI()
        self.update_hitbox()
    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    def draw(self, surface: pygame.Surface, camera):
        if self.target_player and self.hitbox.colliderect(self.target_player.hitbox):
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
    def moveAI(self) -> None:
        # WORLD-SPACE camera bounds
        left_bound = self.camera.x + self.edge_padding
        right_bound = (
                self.camera.x
                + (self.camera.window_width / self.camera.zoom)
                - self.edge_padding
                - self.width
        )

        # EDGE CHECK FIRST (WORLD SPACE)
        if self.x <= left_bound:
            self.x = left_bound
            self.move_direction = 1

        elif self.x >= right_bound:
            self.x = right_bound
            self.move_direction = -1

        # MOVE AFTER DIRECTION IS CORRECT
        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)


