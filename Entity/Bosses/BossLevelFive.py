import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelFive(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0
        name = "BossLevelFive"

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
        self.fire_interval_ms = 1500
        self.last_shot_time = pygame.time.get_ticks()

        self.triple_fire_interval_ms = 3200
        self.last_triple_shot_time = pygame.time.get_ticks()

        # -------------------------
        # MOVEMENT
        # -------------------------
        self.moveSpeed = 3.4
        self.move_interval_ms = 1000
        self.last_move_toggle = pygame.time.get_ticks()
        self.move_direction = random.choice([-1, 1])

        # -------------------------
        # STATS
        # -------------------------
        self.enemyHealth = 400
        self.maxHealth = 400
        self.exp = 5
        self.credits = 50

        self.target_update_interval_ms = 3500
        self.last_target_update = pygame.time.get_ticks()
        self.target_x = self.x

        # -------------------------
        # SPRITE
        # -------------------------
        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    # =====================================================
    # ORIGINAL SINGLE SHOT (UNCHANGED)
    # =====================================================




    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, state) -> None:
        super().update(state)
        if not self.is_active:
            return
        self.update_hitbox()

        if self.camera is None:
            return

        self.moveAI()
        now = pygame.time.get_ticks()

        # # ORIGINAL FIRE
        # if now - self.last_shot_time >= self.fire_interval_ms:
        #     self._shoot_bile()
        #     self.last_shot_time = now

        # TRIPLE FIRE
        if now - self.last_triple_shot_time >= self.triple_fire_interval_ms:
            self.splatter_cannon(
                bullet_speed=1.3,
                bullet_width=20,
                bullet_height=20,
                bullet_color=self.bulletColor,
                bullet_damage=40,
                low_rand_range=-0.40,
                high_rand_range=0.80,
                bullet_count=10,
                state=state
            )

            self.last_triple_shot_time = now

        for bullet in self.enemyBullets:
            bullet.update()

    # =====================================================
    # MOVEMENT
    # =====================================================
    def moveAI(self) -> None:
        if self.camera is None or self.target_player is None:
            return

        now = pygame.time.get_ticks()
        window_width = self.camera.window_width / self.camera.zoom

        # -------------------------------------------------
        # RETARGET ONLY ON INTERVAL (NO PER-FRAME FLIPS)
        # -------------------------------------------------
        if now - self.last_target_update >= self.target_update_interval_ms:
            self.last_target_update = now

            # lock a new direction toward player
            if self.target_player.x > self.x:
                self.move_direction = 1
            else:
                self.move_direction = -1

        # -------------------------------------------------
        # ALWAYS MOVE — NO CONDITIONS
        # -------------------------------------------------
        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        # -------------------------------------------------
        # HARD CLAMP (ONLY PLACE DIRECTION MAY FLIP)
        # -------------------------------------------------
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
        sprite_rect = pygame.Rect(65, 130, 32, 32)
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
