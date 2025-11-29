import math
import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy


class BileSpitter(Enemy):
    BULLET_WIDTH: int = 8
    BULLET_HEIGHT: int = 8

    def __init__(self) -> None:
        super().__init__()
        self.width: int = 40
        self.height: int = 40
        self.color: tuple[int, int, int] = GlobalConstants.RED

        self.speed: float = 1.0
        self.enemyHealth: int = 10
        self.exp: int = 1
        self.credits: int = 5
        self.bileSpeed: int = 15  # projectile speed


    def fire_at_player(
        self,
        player_x: float,
        player_y: float,
        player_width: int,
        player_height: int,
    ) -> None:
        """Snapshot-lock on to player and create one bile shot."""

        # enemy center
        enemy_center_x: float = self.x + self.width / 2
        enemy_center_y: float = self.y + self.height / 2

        # player center
        player_center_x: float = player_x + player_width / 2
        player_center_y: float = player_y + player_height / 2

        # direction enemy -> player
        dx: float = player_center_x - enemy_center_x
        dy: float = player_center_y - enemy_center_y

        length: float = math.hypot(dx, dy)
        if length == 0:
            length = 1.0  # avoid divide-by-zero if somehow overlapping

        vx: float = (dx / length) * self.bileSpeed
        vy: float = (dy / length) * self.bileSpeed

        bullet: dict[str, float] = {
            "x": enemy_center_x - self.BULLET_WIDTH / 2,
            "y": enemy_center_y - self.BULLET_HEIGHT / 2,
            "vx": vx,
            "vy": vy,
        }

        self.enemyBullets.append(bullet)

    def update_bullets(self) -> None:
        """Move all bile shots."""
        for bullet in self.enemyBullets:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]

    def draw_bullets(self, surface: "pygame.Surface") -> None:
        """Draw all bile shots."""
        for bullet in self.enemyBullets:
            pygame.draw.rect(
                surface,
                self.color,  # or a bile-specific color later
                (
                    bullet["x"],
                    bullet["y"],
                    self.BULLET_WIDTH,
                    self.BULLET_HEIGHT,
                ),
            )

    def update(self) -> None:
        # enemy movement / AI goes here later
        pass

    def draw(self, surface: "pygame.Surface") -> None:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
