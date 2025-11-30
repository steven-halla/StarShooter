import random

import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet


class BileSpitter(Enemy):
    def __init__(self) -> None:
        super().__init__()
        self.mover: MoveRectangle = MoveRectangle()
        self.id = 0

        # enemy appearance
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED

        # bullet appearance
        self.bulletColor: tuple[int, int, int] = GlobalConstants.YELLOW
        self.bulletWidth: int = 20
        self.bulletHeight: int = 20

        # firing + bullet movement
        self.bileSpeed: int = 15          # speed of bullet moving DOWN
        self.fire_interval_ms: int = 3000 # shoot every 3 seconds
        self.last_shot_time: int = pygame.time.get_ticks()

        # gameplay stats (not used yet)
        self.speed: float = 1.0
        self.enemyHealth: int = 10
        self.exp: int = 1
        self.credits: int = 5
        self.bileDamage: int = 100

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

    def update(self) -> None:
        super().update()
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



    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the enemy rectangle."""
        pygame.draw.rect(
            surface,
            self.color,
            (self.x, self.y, self.width, self.height)
        )

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
