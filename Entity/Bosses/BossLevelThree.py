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
        self.arm_height = 120
        self.arm_color = GlobalConstants.PURPLE
        self.fire_state = False
        self.fire_pause_ms = 2000
        self.fire_end_time = 0

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
        self.fire_interval_ms = 5000
        self.last_shot_time = pygame.time.get_ticks()

        self.triple_fire_interval_ms = 3000
        self.last_triple_shot_time = pygame.time.get_ticks()

        # -------------------------
        # MOVEMENT
        # -------------------------
        self.moveSpeed = 0.8
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

    def moveAI(self) -> None:
        if self.camera is None or self.target_player is None:
            return

        now = pygame.time.get_ticks()

        # -------------------------
        # FIRE STATE — LOCK MOVEMENT
        # -------------------------
        if getattr(self, "fire_state", False):
            if now - self.last_shot_time >= 2000:
                self.fire_state = False
            return

        # -------------------------
        # CHASE PLAYER (X + Y)
        # -------------------------
        px = self.target_player.x + self.target_player.width / 2
        py = self.target_player.y + self.target_player.height / 2

        bx = self.x + self.width / 2
        by = self.y + self.height / 2

        dx = px - bx
        dy = py - by

        dist = (dx * dx + dy * dy) ** 0.5
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        speed = self.moveSpeed

        self.x += dx * speed
        self.y += dy * speed

        # -------------------------
        # SCREEN CLAMP (X + Y)
        # -------------------------
        window_width = self.camera.window_width / self.camera.zoom
        window_height = self.camera.window_height / self.camera.zoom

        if self.x < 0:
            self.x = 0
        elif self.x + self.width > window_width:
            self.x = window_width - self.width

        if self.y < self.camera.y:
            self.y = self.camera.y
        elif self.y + self.height > self.camera.y + window_height:
            self.y = self.camera.y + window_height - self.height
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
            boss_cy - self.arm_height / 2 + 15,
            self.arm_width,
            self.arm_height
        )

        # RIGHT ARM (vertical, right side)
        right_arm = pygame.Rect(
            boss_cx + 12,
            boss_cy - self.arm_height / 2 + 15,
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

    def check_arm_damage(self, player):
        if player is None:
            return
        print(player.shipHealth)

        player_rect = player.melee_hitbox  # 🔑 THIS IS THE FIX

        boss_cx = self.x + self.width / 2
        boss_cy = self.y + self.height / 2

        left_arm = pygame.Rect(
            boss_cx - self.arm_width - 12,
            boss_cy - self.arm_height / 2,
            self.arm_width,
            self.arm_height
        )

        right_arm = pygame.Rect(
            boss_cx + 12,
            boss_cy - self.arm_height / 2 ,
            self.arm_width,
            self.arm_height
        )

        if player_rect.colliderect(left_arm) or player_rect.colliderect(right_arm):
            print("ARM HIT")
            player.shipHealth -= 10
            player.on_hit()
