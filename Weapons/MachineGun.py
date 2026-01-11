import pygame
from Weapons.Bullet import Bullet
from Constants.Timer import Timer


class MachineGun(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # identity
        self.weapon_name: str = "Machine Gun"

        # projectile size
        self.width: int = 4
        self.height: int = 4

        # stats
        self.damage: int = 1
        self.rate_of_fire: float = 0.1
        self.bullet_speed: float = 12.0

        # firing config
        self.bullets_per_shot: int = 2
        self.bullet_spread_offset: int = 18
        self.center_bullet_x: int = 18

        # cooldown
        self.bullet_timer: Timer = Timer(self.rate_of_fire)

        # movement vector (unused for spawner, but safe)
        self.vx: float = 0.0
        self.vy: float = -1.0

        # injected externally
        self.camera = None

        self.update_rect()

    def fire_machine_gun(self) -> list:
        if not self.bullet_timer.is_ready():
            return []

        bullets = []

        center_x = self.x + self.width + self.center_bullet_x
        bullet_y = self.y

        count = self.bullets_per_shot
        spread = self.bullet_spread_offset
        start_index = -(count // 2)

        for i in range(count):
            offset = (start_index + i) * spread
            bullet_x = center_x + offset - self.width // 2

            bullet = Bullet(bullet_x, bullet_y)

            # bullet size comes ONLY from weapon width/height
            bullet.width = self.width
            bullet.height = self.height

            bullet.vx = 0.0
            bullet.vy = -1.0
            bullet.bullet_speed = self.bullet_speed
            bullet.damage = self.damage
            bullet.camera = self.camera

            bullet.update_rect()
            bullets.append(bullet)

        self.bullet_timer.reset()
        return bullets

    def update(self) -> None:
        super().update()

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 255, 0), self.rect)
