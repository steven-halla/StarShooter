import random

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BossLevelOne(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0

        # enemy appearance
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # bullet appearance
        self.bulletColor: tuple[int, int, int] = GlobalConstants.SKYBLUE
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20

        # firing + bullet movement
        self.bileSpeed: int = 3          # speed of bullet moving DOWN
        self.fire_interval_ms: int = 3000 # shoot every 3 seconds
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
        self.bile_spitter_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

    def _shoot_bile(self) -> None:
        """Create a Bullet object and add it to local bullet list."""
        bullet_x = self.x + self.width // 2 - self.bulletWidth // 2
        bullet_y = self.y + self.height

        bullet = Bullet(bullet_x, bullet_y)
        bullet.color = self.bulletColor
        bullet.width = self.bulletWidth
        bullet.height = self.bulletHeight
        bullet.speed = self.bileSpeed  # positive — travels downward

        # 🔹 keep the rect in sync with the new size
        bullet.rect.width = bullet.width
        bullet.rect.height = bullet.height

        self.enemyBullets.append(bullet)
        bullet.damage = 10  # 👈 THIS is your enemy damage

    def update(self) -> None:
        super().update()
        self.update_hitbox()

        # print("BILE:", self.y, "CAM:", self.camera.y,
        #       "SCREEN_Y:", self.camera.world_to_screen_y(self.y))

        """Handle firing every 3 seconds + move bullets."""
        self.moveAI()

        now = pygame.time.get_ticks()


        # Time to shoot?
        if now - self.last_shot_time >= self.fire_interval_ms:
            self._shoot_bile()
            self.last_shot_time = now

        # Move all bullets DOWN
        for bullet in self.enemyBullets:
            bullet.y += bullet.speed




    # def draw(self, surface: "pygame.Surface") -> None:
    #     """Draw the enemy rectangle."""
    #     pygame.draw.rect(
    #         surface,
    #         self.color,
    #         (self.x, self.y, self.width, self.height)
    #     )

    def moveAI(self) -> None:
        window_width, _ = GlobalConstants.WINDOWS_SIZE
        now = pygame.time.get_ticks()

        # init tracker
        if not hasattr(self, "_last_x"):
            self._last_x = self.x

        # toggle direction every interval
        if now - self.last_move_toggle >= self.move_interval_ms:
            self.last_move_toggle = now
            self.move_direction *= -1

        # move
        if self.move_direction > 0:
            self.mover.enemy_move_right(self)
        else:
            self.mover.enemy_move_left(self)

        # ---------- LEFT EDGE (REAL EDGE) ----------
        if self.x <= 0:
            self.x = 0
            self.move_direction = 1
            self.last_move_toggle = now

        # ---------- RIGHT EDGE (REAL EDGE) ----------
        elif self.x + self.width >= window_width:
            self.x = window_width - self.width
            self.move_direction = -1
            self.last_move_toggle = now

        # ---------- FAILSAFE ----------
        if self.x == self._last_x:
            self.move_direction *= -1
            if self.move_direction > 0:
                self.mover.enemy_move_right(self)
            else:
                self.mover.enemy_move_left(self)
            self.last_move_toggle = now

        self._last_x = self.x

    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(0, 344, 32, 32)
        sprite = self.bile_spitter_image.subsurface(sprite_rect)

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
