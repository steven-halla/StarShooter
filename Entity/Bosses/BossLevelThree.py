import math
import random
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelThree(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.name: str = "level_3_boss"

        # -------------------------
        # BODY
        # -------------------------
        self.width = 40
        self.height = 20
        self.color = GlobalConstants.RED
        self.enemyHealth = 1000
        self.maxHealth = 1000
        # -------------------------
        # BILE ATTACK TIMER
        # -------------------------
        self.bile_interval_ms = 10000
        self.bile_windup_ms = 3000
        self.bile_recovery_ms = 2000
        # -------------------------
        # BILE PROJECTILE CONFIG
        # -------------------------
        self.bulletWidth = 12
        self.bulletHeight = 30
        self.bulletColor = GlobalConstants.SKYBLUE
        self.weapon_speed = 3.0
        self.enemyBullets = []

        self.last_bile_time = pygame.time.get_ticks()
        self.bile_state = False
        self.bile_shot_fired = False
        self.bile_end_time = 0

        # -------------------------
        # ARM CONFIG
        # -------------------------
        self.arm_width = 14
        self.arm_length = 100
        self.arm_color = GlobalConstants.PURPLE

        self.arm_angle = 0.0
        self.arm_target_angle = 0.0
        self.arm_angle_speed = 0.09

        self.arm_extend = 0.0           # 0 → 1
        self.arm_extend_speed = 0.04

        self.arm_attack_cooldown = 2500
        self.last_arm_attack = pygame.time.get_ticks()

        # -------------------------
        # STATE
        # -------------------------
        self.fire_state = False
        self.fire_pause_ms = 2000
        self.fire_end_time = 0

        # -------------------------
        # MOVEMENT
        # -------------------------
        self.moveSpeed = 0.8

        # -------------------------
        # SPRITE
        # -------------------------
        self.sprite_sheet = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def _shoot_bile(self) -> None:
        bullet_x = self.x + self.width // 2 - self.bulletWidth // 2
        bullet_y = self.y + self.height - 50

        bullet = Bullet(bullet_x, bullet_y)
        bullet.color = self.bulletColor
        bullet.width = self.bulletWidth + 30
        bullet.height = self.bulletHeight + 50
        bullet.speed = self.weapon_speed
        bullet.damage = 10

        bullet.rect.width = bullet.width
        bullet.rect.height = bullet.height

        self.enemyBullets.append(bullet)

    # =====================================================
    # ARM ATTACK PREP
    # =====================================================
    def arm_attack_prepare(self) -> None:
        if self.target_player is None:
            return

        now = pygame.time.get_ticks()
        if now - self.last_arm_attack < self.arm_attack_cooldown:
            return

        self.last_arm_attack = now
        self.fire_state = True
        self.fire_end_time = now + self.fire_pause_ms

        bx = self.x + self.width / 2
        by = self.y + self.height / 2

        px = self.target_player.x + self.target_player.width / 2
        py = self.target_player.y + self.target_player.height / 2

        dx = px - bx
        dy = py - by

        self.arm_target_angle = math.atan2(dy, dx)



    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, state) -> None:
        super().update(state)
        # print(self.enemyHealth)
        if not self.is_active or self.camera is None:
            return

        self.update_hitbox()
        now = pygame.time.get_ticks()

        # =================================================
        # BILE ATTACK STATE MACHINE
        # =================================================
        if self.bile_state:
            # Freeze movement completely
            if not self.bile_shot_fired and now >= self.bile_end_time - self.bile_recovery_ms:
                self._shoot_bile()
                self.bile_shot_fired = True

            if now >= self.bile_end_time:
                self.bile_state = False
            return  # ⛔ stop everything else during bile

        # Start bile attack every 15s
        if now - self.last_bile_time >= self.bile_interval_ms:
            self.bile_state = True
            self.bile_shot_fired = False
            self.last_bile_time = now
            self.bile_end_time = now + self.bile_windup_ms + self.bile_recovery_ms
            return

        # =================================================
        # ARM SWING LOGIC (unchanged)
        # =================================================
        angle_diff = self.arm_target_angle - self.arm_angle
        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
        self.arm_angle += angle_diff * self.arm_angle_speed

        if self.fire_state:
            self.arm_extend = min(1.0, self.arm_extend + self.arm_extend_speed)
            if now >= self.fire_end_time:
                self.fire_state = False
        else:
            self.arm_extend = max(0.0, self.arm_extend - self.arm_extend_speed)

        # =================================================
        # MOVEMENT (CHASE PLAYER)
        # =================================================
        if not self.fire_state and self.target_player is not None:
            px = self.target_player.x + self.target_player.width / 2
            py = self.target_player.y + self.target_player.height / 2

            bx = self.x + self.width / 2
            by = self.y + self.height / 2

            dx = px - bx
            dy = py - by
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
                self.x += dx * self.moveSpeed
                self.y += dy * self.moveSpeed

        # Trigger arm attack
        self.arm_attack_prepare()
    # =====================================================
    # DRAW
    # =====================================================
    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.sprite_sheet.subsurface(sprite_rect)

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

        self.draw_arms(surface, camera)

    # =====================================================
    # ARM DRAW (ROTATING, ANCHORED)
    # =====================================================
    def draw_arms(self, surface: pygame.Surface, camera):
        bx = self.x + self.width / 2
        by = self.y + self.height / 2

        length = self.arm_length * self.arm_extend

        dx = math.cos(self.arm_angle)
        dy = math.sin(self.arm_angle)

        end_x = bx + dx * length
        end_y = by + dy * length

        pygame.draw.line(
            surface,
            self.arm_color,
            (
                camera.world_to_screen_x(bx),
                camera.world_to_screen_y(by),
            ),
            (
                camera.world_to_screen_x(end_x),
                camera.world_to_screen_y(end_y),
            ),
            int(self.arm_width * camera.zoom),
        )

    # =====================================================
    # ARM DAMAGE
    def check_arm_damage(self, player):
        if player is None:
            return

        # Boss center (arm anchor)
        bx = self.x + self.width / 2
        by = self.y + self.height / 2

        # Arm vector
        length = self.arm_length * self.arm_extend
        dx = math.cos(self.arm_angle)
        dy = math.sin(self.arm_angle)

        end_x = bx + dx * length
        end_y = by + dy * length

        # Build arm hitbox as a thick rect along the arm
        arm_thickness = self.arm_width * 1.5

        arm_rect = pygame.Rect(
            min(bx, end_x) - arm_thickness / 2,
            min(by, end_y) - arm_thickness / 2,
            abs(end_x - bx) + arm_thickness,
            abs(end_y - by) + arm_thickness,
        )

        # DEBUG (optional)
        # print("ARM RECT:", arm_rect)

        if player.melee_hitbox.colliderect(arm_rect):
            # print("ARM HIT (FULL ARM)")
            player.shipHealth -= 10
            player.on_hit()
