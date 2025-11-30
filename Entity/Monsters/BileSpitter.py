import pygame

from Constants.GlobalConstants import GlobalConstants
from Entity.Enemy import Enemy
from Weapons.Bullet import Bullet


class BileSpitter(Enemy):
    def __init__(self) -> None:
        super().__init__()

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

        # bullets held locally until battle screen copies them
        self.enemyBullets: list[Bullet] = []

    def _shoot_bile(self) -> None:
        """Create a Bullet object and add it to local bullet list."""
        bullet_x = self.x + self.width // 2 - self.bulletWidth // 2
        bullet_y = self.y + self.height

        bullet = Bullet(bullet_x, bullet_y)
        bullet.color = self.bulletColor
        bullet.width = self.bulletWidth
        bullet.height = self.bulletHeight
        bullet.speed = self.bileSpeed   # positive — travels downward

        self.enemyBullets.append(bullet)

    def update(self) -> None:
        """Handle firing every 3 seconds + move bullets."""
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
