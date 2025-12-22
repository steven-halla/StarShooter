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
        self.id = 0
        # -------------------------
        # MELEE ARMS (RENDER ONLY)
        # -------------------------
        self.arm_width = 16
        self.arm_height = 150
        self.arm_color = GlobalConstants.PURPLE

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
        self.weapon_speed = 3.0
        self.enemyBullets: list[Bullet] = []

        # -------------------------
        # FIRING TIMERS
        # -------------------------
        self.fire_interval_ms = 3000
        self.last_shot_time = pygame.time.get_ticks()

        self.triple_fire_interval_ms = 9000
        self.last_triple_shot_time = pygame.time.get_ticks()

        # -------------------------
        # MOVEMENT
        # -------------------------
        self.moveSpeed = 2.0
        self.move_interval_ms = 3000
        self.last_move_toggle = pygame.time.get_ticks()
        self.move_direction = random.choice([-1, 1])

        # -------------------------
        # STATS
        # -------------------------
        self.enemyHealth = 1000
        self.exp = 5
        self.credits = 50

        # -------------------------
        # SPRITE
        # -------------------------
        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    # =====================================================
    # ORIGINAL SINGLE SHOT (UNCHANGED)
    # =====================================================
    def _shoot_bile(self) -> None:
        bullet_x = self.x + self.width // 2 - self.bulletWidth // 2
        bullet_y = self.y + self.height

        bullet = Bullet(bullet_x, bullet_y)
        bullet.color = self.bulletColor
        bullet.width = self.bulletWidth + 30
        bullet.height = self.bulletHeight + 100
        bullet.speed = self.weapon_speed
        bullet.damage = 10

        bullet.rect.width = bullet.width
        bullet.rect.height = bullet.height

        self.enemyBullets.append(bullet)

    def shoot_triple_line(self) -> None:
        bullet_count = 20
        arc_degrees = 180  # full downward arc
        min_spacing_px = 40  # desired spread
        spawn_radius = 60  # distance where spacing matters

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        # Convert pixel spacing to angular spacing
        min_angle_spacing = math.degrees(
            math.atan(min_spacing_px / spawn_radius)
        )

        # Divide arc into slots
        total_slots = bullet_count
        slot_angle = arc_degrees / total_slots

        start_angle = 90 + arc_degrees / 2  # left edge of downward arc

        for i in range(bullet_count):
            # Base angle for this slot
            base_angle = start_angle - i * slot_angle

            # Random jitter inside slot (but not overlapping neighbors)
            jitter = random.uniform(
                -slot_angle / 2 + min_angle_spacing / 2,
                slot_angle / 2 - min_angle_spacing / 2
            )

            angle_deg = base_angle + jitter
            angle_rad = math.radians(angle_deg)

            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)

            bullet = Bullet(cx, cy)
            bullet.dx = dx * self.weapon_speed
            bullet.speed = dy * self.weapon_speed
            bullet.width = self.bulletWidth - 10
            bullet.height = self.bulletHeight - 10
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

        # ORIGINAL FIRE
        if now - self.last_shot_time >= self.fire_interval_ms:
            self._shoot_bile()
            self.last_shot_time = now

        # TRIPLE FIRE
        if now - self.last_triple_shot_time >= self.triple_fire_interval_ms:
            self.shoot_triple_line()
            self.last_triple_shot_time = now

        for bullet in self.enemyBullets:
            bullet.update()

    # =====================================================
    # MOVEMENT
    # =====================================================
    def moveAI(self) -> None:
        if self.camera is None:
            return

        now = pygame.time.get_ticks()
        window_width = self.camera.window_width / self.camera.zoom

        if now - self.last_move_toggle >= self.move_interval_ms:
            self.last_move_toggle = now
            self.move_direction = random.choice([-1, 1])

        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

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
        sprite_rect = pygame.Rect(0, 344, 32, 32)
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
        self.draw_arms(surface, camera)

    def draw_arms(self, surface: pygame.Surface, camera):
        zoom = camera.zoom

        boss_cx = self.x + self.width / 2
        boss_cy = self.y + self.height / 2

        # LEFT ARM (vertical, left side)
        left_arm = pygame.Rect(
            boss_cx - self.arm_width - 12,
            boss_cy - self.arm_height / 2 + 30,
            self.arm_width,
            self.arm_height
        )

        # RIGHT ARM (vertical, right side)
        right_arm = pygame.Rect(
            boss_cx + 12,
            boss_cy - self.arm_height / 2 + 30,
            self.arm_width,
            self.arm_height
        )

        for arm in (left_arm, right_arm):
            screen_x = camera.world_to_screen_x(arm.x)
            screen_y = camera.world_to_screen_y(arm.y)
            screen_w = int(arm.width * zoom)
            screen_h = int(arm.height * zoom)

            pygame.draw.rect(
                surface,
                self.arm_color,
                (screen_x, screen_y, screen_w, screen_h)
            )
