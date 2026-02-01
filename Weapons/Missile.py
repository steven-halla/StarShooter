import pygame
import math

from Constants.Timer import Timer
from Weapons.Bullet import Bullet


class Missile(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 12

        # identity
        self.weapon_name: str = "Missile"

        # stats
        self.damage: int = 343
        self.rate_of_fire: float = 0.5
        self.bullet_speed: float = 1.5

        # movement vector (default straight up)
        self.vx: float = 0.0
        self.vy: float = -1.0

        # homing
        self.target_enemy = None

        self.update_rect()

        # self.missileSpeed: int = 10 # 10 original
        self.missile_spread_offset: int = 20
        self.max_missiles: int = 1
        self.current_missiles: int = 1

        # missile stats
        self.missile_fire_interval_seconds: float = 3.0
        self.missile_timer: Timer = Timer(self.missile_fire_interval_seconds)
        self.missile_regen_interval_seconds: float = 3.0
        self.missile_regen_timer: Timer = Timer(self.missile_regen_interval_seconds)

    def update(self) -> None:
        if self.target_enemy is not None and self.target_enemy.enemyHealth <= 0:
            self.target_enemy = None

        # homing logic — vx/vy ONLY
        if self.target_enemy is not None:
            vx = self.target_enemy.x - self.x
            vy = self.target_enemy.y - self.y
            length = math.hypot(vx, vy)

            if length != 0:
                self.vx = vx / length
                self.vy = vy / length

        # movement handled by Bullet via vx/vy
        super().update()
        self.update_rect()

    def fire_missile(
        self,
        missile_damage: int = None,
        bullet_speed: float = None,
        rate_of_fire: float = None,
        max_missiles: int = None,
    ):
        # Only fire if timer is ready and we have missiles
        if not self.missile_timer.is_ready() or self.current_missiles <= 0:
            return None

        # Spawn position (center of ship)
        missile_x = self.x + self.width // 2
        missile_y = self.y

        # Create the missile
        missile = Missile(missile_x, missile_y)

        # Apply passed-in stats if provided
        if missile_damage is not None:
            missile.damage = missile_damage
        if bullet_speed is not None:
            missile.bullet_speed = bullet_speed
        if rate_of_fire is not None:
            missile.rate_of_fire = rate_of_fire
        if max_missiles is not None:
            self.max_missiles = max_missiles  # Update launcher's max

        # Reset cooldown and decrease missile count
        self.missile_timer.reset()
        self.current_missiles -= 1
        # Reset the regeneration timer to ensure a 3-second delay before recovery
        self.missile_regen_timer.reset()

        return missile

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.is_active:
            return

        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        pygame.draw.rect(
            surface,
            (255, 165, 0),
            pygame.Rect(
                screen_x,
                screen_y,
                int(self.width * camera.zoom),
                int(self.height * camera.zoom),
            ),
        )

    # Missile class

    def reload_missiles(self) -> None:
        if self.current_missiles < self.max_missiles and self.missile_regen_timer.is_ready():
            self.current_missiles += 1
            self.missile_regen_timer.reset()
