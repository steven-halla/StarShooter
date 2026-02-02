import math
import pygame

from Constants.Timer import Timer
from Weapons.Bullet import Bullet


class WindSlicer(Bullet):
    def __init__(self, x: float, y: float, vx: float = 0.0, vy: float = 0.0):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 6
        self.bullet_count: int = 8
        self.wind_slicer_timer_cooldown_seconds: float = 0.4

        self.wind_slicer_timer: Timer = Timer(self.wind_slicer_timer_cooldown_seconds)


        # self.bullet_count if you want to make it global
        # Look inside fire wind slicer function for this
        self.weapon_name: str = "Wind Slicer"


        self.damage: int = 5
        self.rate_of_fire: float = 0.0
        self.bullet_speed: float = 3.0

        # movement vector
        self.vx: float = vx
        self.vy: float = vy

        # state
        self.is_active: bool = True

        self.update_rect()

    def update(self) -> None:
        # movement handled by Bullet using vx/vy
        super().update()

    def fire_wind_slicer(self, damage: int = None, bullet_count: int = None) -> list:
        #  culd make bullet count self.bullet_coutn in init
        if not self.wind_slicer_timer.is_ready():
            return []

        bullets = []

        center_x = self.x + self.width / 2
        start_y = self.y

        # Use passed-in values or fallback to instance values
        current_damage = damage if damage is not None else self.damage
        current_bullet_count = bullet_count if bullet_count is not None else self.bullet_count

        cone_angle_deg = 60
        start_angle = -90 - cone_angle_deg / 2
        angle_step = cone_angle_deg / (max(1, current_bullet_count - 1))
        speed = 3

        for i in range(current_bullet_count):
            angle = math.radians(start_angle + i * angle_step)
            vx = math.cos(angle)
            vy = math.sin(angle)

            bullet = Bullet(center_x, start_y)
            bullet.width = self.width
            bullet.height = self.height
            bullet.damage = current_damage
            bullet.vx = vx
            bullet.vy = vy
            bullet.bullet_speed = speed
            bullet.update_rect()

            bullets.append(bullet)

        self.wind_slicer_timer.reset()
        return bullets

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (180, 220, 255), self.rect)
