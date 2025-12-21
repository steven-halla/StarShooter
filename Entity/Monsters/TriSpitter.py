import random

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class TriSpitter(Enemy):
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
        self.bileSpeed: int = 3          # speed of bullet moving DOWN
        self.fire_interval_ms: int = 2000 # shoot every 3 seconds
        self.last_shot_time: int = pygame.time.get_ticks()

        # gameplay stats (not used yet)
        self.speed: float = 1.0
        self.enemyHealth: int = 10
        self.exp: int = 1
        self.credits: int = 5

        # bullets held locally until battle screen copies them
        self.enemyBullets: list[Bullet] = []

        # --- AI movement state ---
        self.moveSpeed: float = 2.0      # how fast BileSpitter moves horizontally
        self.edge_padding: int = 30      # distance from screen edge before turning
        self.move_direction: int = 1     # 1 = right, -1 = left

        self.move_interval_ms: int = 3000        # 3 seconds
        self.last_move_toggle: int = pygame.time.get_ticks()
        self.is_moving: bool = True      # move for 3 seconds, then pause 3 seconds, etc.

        self.move_direction = random.choice([-1, 1])
        self.enemyHealth: int = 5
        self.tri_spiter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def shoot_triple_bullets(self):
        base_x = self.x + self.width // 2 - self.bulletWidth // 2
        bullet_y = self.y + self.height

        offsets = [-15, 0, 15]  # left, center, right

        for offset in offsets:
            bullet_x = base_x + offset
            bullet = Bullet(bullet_x, bullet_y)

            bullet.color = self.bulletColor
            bullet.width = self.bulletWidth
            bullet.height = self.bulletHeight
            bullet.damage = 10

            # Vertical speed (always same)
            bullet.speed = self.bileSpeed

            # 🔥 YOUR PATTERN: “offset[0] x + 5”
            # Translation: drift sideways by 5
            if offset < 0:
                bullet.dx = -3  # left diagonal
            elif offset > 0:
                bullet.dx = 3  # right diagonal
            else:
                bullet.dx = 0  # center straight

            bullet.update_rect()
            self.enemyBullets.append(bullet)
    def update(self) -> None:
        super().update()
        if not self.is_active:
            return

        now = pygame.time.get_ticks()

        # -------------------------------
        # 🔥 If frozen, stay frozen
        # -------------------------------
        if self.freeze_start_time is not None:
            if now - self.freeze_start_time < self.freeze_duration_ms:
                # Still frozen → don't move
                # (still update bullets + hitbox)
                pass
            else:
                # Freeze complete
                self.freeze_start_time = None

        else:
            # -------------------------------
            # 🔥 Not frozen → move normally
            # -------------------------------
            if hasattr(self, "target_player") and self.target_player is not None:
                # Move toward player's X only if NOT frozen
                if self.target_player.x > self.x:
                    self.mover.enemy_move_right(self)
                elif self.target_player.x < self.x:
                    self.mover.enemy_move_left(self)

                # ----------------------------------
                # 🔥 Check if aligned → start freeze
                # ----------------------------------
                aligned = abs(self.x - self.target_player.x) <= 5
                if aligned:
                    self.freeze_start_time = now

            # Keep using the horizontal AI movement when not locked
            self.moveAI()

        # -------------------------------
        # Shooting only allowed if aligned
        # -------------------------------
        aligned = abs(self.x - self.target_player.x) <= 5
        if aligned and self.freeze_start_time is not None:
            if now - self.last_shot_time >= self.fire_interval_ms:
                self.shoot_triple_bullets()
                self.last_shot_time = now

        # Move all bullets
        for bullet in self.enemyBullets:
            bullet.y += bullet.speed

        self.update_hitbox()

    # def update(self) -> None:
    #     super().update()
    #
    #     # self.mover.player_x_cordinate_lock_on()
    #
    #     """Handle firing every 3 seconds + move bullets."""
    #     self.moveAI()
    #     if hasattr(self, "target_player") and self.target_player is not None:
    #         if self.target_player.x > self.x:
    #             self.mover.enemy_move_right(self)
    #         elif self.target_player.x < self.x:
    #             self.mover.enemy_move_left(self)
    #     now = pygame.time.get_ticks()
    #
    #
    #     # Time to shoot?
    #     if now - self.last_shot_time >= self.fire_interval_ms:
    #         self.shoot_triple_bullets()
    #         self.last_shot_time = now
    #
    #     # Move all bullets DOWN
    #     for bullet in self.enemyBullets:
    #         bullet.y += bullet.speed
    #
    #     self.update_hitbox()
    #


    # def draw(self, surface: "pygame.Surface") -> None:
    #     """Draw the enemy rectangle."""
    #     pygame.draw.rect(
    #         surface,
    #         self.color,
    #         (self.x, self.y, self.width, self.height)
    #     )

    def moveAI(self) -> None:
        """Simple AI: move left/right using MoveRectangle helpers."""
        window_width, _ = GlobalConstants.WINDOWS_SIZE
        now = pygame.time.get_ticks()

        # every 3 seconds, toggle moving / not moving
        if now - self.last_move_toggle >= self.move_interval_ms:
            self.is_moving = not self.is_moving
            self.last_move_toggle = now

            # when we start moving, pick left/right (50/50)
            if self.is_moving:
                self.move_direction = random.choice([-1, 1])

        if not self.is_moving:
            return


        # 🔹 use YOUR helpers instead of touching x directly
        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        # edge check: if within 30px of left/right edge, flip direction
        if self.x <= self.edge_padding:
            self.x = self.edge_padding
            self.move_direction = 1  # go right
        elif self.x + self.width >= window_width - self.edge_padding:
            self.x = window_width - self.edge_padding - self.width
            self.move_direction = -1  # go left

    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(60, 128, 32, 32)
        sprite = self.tri_spiter_image.subsurface(sprite_rect)

        # scale ship with zoom
        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        # convert world → screen
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        # draw ship
        surface.blit(scaled_sprite, (screen_x, screen_y))

        # ================================
        #  DRAW PLAYER HITBOX (DEBUG)
        # ================================
        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)

    def _clamp_vertical(self) -> None:
        pass
