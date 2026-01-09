import pygame
from Weapons.Bullet import Bullet


class BusterCanon(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # -----------------
        # BASE SHOT STATS
        # -----------------
        self.base_damage = 11
        self.base_speed = 3
        self.base_width = 12
        self.base_height = 12

        # RATE OF FIRE (HERE)
        self.rate_of_fire = 0.4      # seconds
        self.last_fire_time = 0.0

        # -----------------
        # CHARGED SHOT STATS
        # -----------------
        self.charged_damage = 40
        self.charged_speed = 3.0
        self.charged_width = self.base_width * 4
        self.charged_height = self.base_height * 4
        self.charge_time_required = 2.0  # seconds

        # -----------------
        # MOVEMENT VECTOR
        # -----------------
        self.vx = 0.0
        self.vy = -1.0

        # -----------------
        # CHARGE STATE
        # -----------------
        self.is_charging: bool = False
        self.charge_start_time: float | None = None

        # -----------------
        # IDENTITY
        # -----------------
        self.weapon_name = "Buster Cannon"

        # injected
        self.camera = None

        # active stats
        self.width = self.base_width
        self.height = self.base_height
        self.damage = self.base_damage
        self.bullet_speed = self.base_speed

        self.update_rect()

    # -----------------
    # RATE OF FIRE CHECK
    # -----------------
    def can_fire(self) -> bool:
        now = pygame.time.get_ticks() / 1000.0
        return (now - self.last_fire_time) >= self.rate_of_fire

    # -----------------
    # CHARGE CONTROL
    # -----------------
    def start_charge(self) -> None:
        if not self.is_charging:
            self.is_charging = True
            self.charge_start_time = pygame.time.get_ticks()

    def stop_charge(self) -> None:
        self.is_charging = False
        self.charge_start_time = None

    def is_fully_charged(self) -> bool:
        if not self.is_charging or self.charge_start_time is None:
            return False
        elapsed = (pygame.time.get_ticks() - self.charge_start_time) / 1000.0
        return elapsed >= self.charge_time_required

    # -----------------
    # FIRE
    # -----------------
    def fire_buster_cannon(self) -> list:
        if not self.can_fire():
            return []

        self.last_fire_time = pygame.time.get_ticks() / 1000.0

        bullet_x = self.x + self.width // 2
        bullet_y = self.y

        projectile = Bullet(bullet_x, bullet_y)

        if self.is_fully_charged():
            projectile.width = self.charged_width
            projectile.height = self.charged_height
            projectile.damage = self.charged_damage
            projectile.bullet_speed = self.charged_speed
        else:
            projectile.width = self.base_width
            projectile.height = self.base_height
            projectile.damage = self.base_damage
            projectile.bullet_speed = self.base_speed

        projectile.vx = 0.0
        projectile.vy = -1.0
        projectile.camera = self.camera
        projectile.update_rect()

        self.stop_charge()

        return [projectile]

    # -----------------
    # UPDATE
    # -----------------
    def update(self):
        self.update_rect()

    # -----------------
    # DRAW
    # -----------------
    def draw(self, surface: pygame.Surface) -> None:
        color = (255, 64, 64) if self.is_fully_charged() else (0, 128, 255)
        pygame.draw.rect(surface, color, self.rect)
