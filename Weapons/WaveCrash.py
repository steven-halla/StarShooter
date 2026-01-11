import pygame

from Constants.Timer import Timer
from Weapons.Bullet import Bullet


class WaveCrash(Bullet):
    # CHANGE 1 — make direction optional
    def __init__(self, x: float, y: float, direction: int = 0):
        super().__init__(x, y)


        self.damage: int = 6
        self.speed: int = 6
        self.width: int = 12
        self.height: int = 12
        self.wave_crash_cooldown_seconds: float = 0.4
        self.wave_crash_timer: Timer = Timer(self.wave_crash_cooldown_seconds)

        # identity
        self.weapon_name: str = "Wave Crash"

        # stats
        self.damage: int = 6
        self.rate_of_fire: float = 0.5
        self.last_fire_time = 0.0

        self.bullet_speed: float = 6.0

        # movement vector (horizontal only)
        self.vx: float = float(direction)   # -1 left, +1 right
        self.vy: float = 0.0


        # state
        self.is_active: bool = True

        self.update_rect()

    def update(self) -> None:
        # movement handled by Bullet using vx/vy and bullet_speed
        super().update()

    def can_fire(self) -> bool:
        now = pygame.time.get_ticks() / 1000.0
        return (now - self.last_fire_time) >= self.rate_of_fire

    # CHANGE 3 — REPLACE fire_wave_crash ENTIRELY
    def fire_wave_crash(self) -> list:
        if not self.wave_crash_timer.is_ready():
            return []

        bullets = []

        spawn_x = self.x + self.width // 2
        spawn_y = self.y

        # LEFT wave
        left = Bullet(spawn_x, spawn_y)
        left.width = self.width
        left.height = self.height
        left.damage = self.damage
        left.vx = -1
        left.vy = 0
        left.bullet_speed = self.bullet_speed
        left.update_rect()

        # RIGHT wave
        right = Bullet(spawn_x, spawn_y)
        right.width = self.width
        right.height = self.height
        right.damage = self.damage
        right.vx = 1
        right.vy = 0
        right.bullet_speed = self.bullet_speed
        right.update_rect()

        bullets.extend([left, right])
        self.wave_crash_timer.reset()
        return bullets


    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (0, 200, 255), self.rect)
