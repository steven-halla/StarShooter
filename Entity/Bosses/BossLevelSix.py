import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelSix(Enemy):
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

        self.triple_fire_interval_ms = 1500
        self.last_triple_shot_time = pygame.time.get_ticks()

        # -------------------------
        # MOVEMENT
        # -------------------------
        self.moveSpeed = 4.0
        self.move_interval_ms = 1200
        self.last_move_toggle = pygame.time.get_ticks()
        self.move_direction = random.choice([-1, 1])

        # -------------------------
        # STATS
        # -------------------------
        self.enemyHealth = 400
        self.exp = 5
        self.credits = 50

        self.target_update_interval_ms = 3000
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
    # barrage FIRE — SHOOTS AT PLAYER LAST POSITION
    # =====================================================
    def shoot_barrage(self) -> None:
        bullet_count = 15

        base_y = self.y + self.height

        # ⬅️➡️ extend 10px beyond boss width
        left_x = self.x - 40
        right_x = self.x + self.width + 40

        spacing = (right_x - left_x) / (bullet_count - 1)

        for i in range(bullet_count):
            bx = left_x + i * spacing

            # stagger Y so bullets don't align
            by = base_y + random.randint(-60, 60)

            bullet = Bullet(bx, by)
            bullet.dx = 0  # straight down
            bullet.speed = self.weapon_speed
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

        # # ORIGINAL FIRE
        # if now - self.last_shot_time >= self.fire_interval_ms:
        #     self._shoot_bile()
        #     self.last_shot_time = now

        # TRIPLE FIRE
        if now - self.last_triple_shot_time >= self.triple_fire_interval_ms:
            self.shoot_barrage()
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
