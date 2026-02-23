import pygame
from Weapons.Bullet import Bullet
from Constants.Timer import Timer

# CHIPS WE CAN USE FOR UPGRades
# Chip 1: Increase Width/Height of bullets by 1
# Chip 2: incease damage. 1
# Chip 3: incease damage. 1
# Chip 4: incease damage. 1
#Chip 5: double barrel
#Chip 7 : reduced heat
#Chip 8 : reduced heat
#Chip 9 : reduced heat
#chip 6: bullet speed UP + 2
#chip 10: bullet speed UP + 2

class MachineGun(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # identity
        self.weapon_name: str = "Machine Gun"

        # projectile size
        self.width: int = 4
        self.height: int = 4

        # stats
        self.damage: float = 0.5
        self.rate_of_fire: float = .1
        self.bullet_speed: float = 3.5

        # firing config
        self.bullets_per_shot: int = 1
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

    def fire_machine_gun(self, damage: float, width: int, height: int, rate_of_fire: float, bullet_speed: float, bullets_per_shot: int) -> list:
        # update stats if they were passed in
        self.damage = damage
        self.width = width
        self.height = height
        self.rate_of_fire = rate_of_fire
        self.bullet_speed = bullet_speed
        self.bullets_per_shot = bullets_per_shot

        # update timer interval if rate_of_fire changed
        new_interval_ms = int(self.rate_of_fire * Timer.MS_PER_SECOND)
        if self.bullet_timer.interval_ms != new_interval_ms:
            self.bullet_timer.interval_ms = new_interval_ms

        if not self.bullet_timer.is_ready():
            return []

        bullets = []

        center_x = self.x + self.width + self.center_bullet_x
        bullet_y = self.y

        count = self.bullets_per_shot
        spread = self.bullet_spread_offset

        # center it on player ship if not double_barrel or if double_barrel upgrade
        if count == 1:
            center_x = self.x + 8
        elif count == 2:
            center_x = self.x + 14
            spread = 8

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
