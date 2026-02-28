import math
import pygame
from Weapons.Bullet import Bullet


class MetalShield(Bullet):
    def __init__(self, x: float, y: float, damage: int = 50, max_hits: int = 3):
        super().__init__(x, y)

        # size
        self.width: int = 32
        self.height: int = 32

        # identity
        self.METAL_SHIELD: str = "Metal Shield"

        # stats
        self.damage: int = damage            # shield does not deal damage
        self.rate_of_fire: float = 0.0  # not applicable, but consistent
        self.bullet_speed: float = 0.0  # does not translate

        # orbit behavior
        self.orbit_radius: float = 40.0
        self.orbit_speed: float = 0.08  # radians per frame
        self.angle: float = 0.0
        self.ki_cost: int = 25

        # state
        self.is_active: bool = True
        self.has_blocked: bool = False
        self.hit_count: int = 0
        self.max_hits: int = max_hits
        self.damage_cooldown_ms: int = 500  # 0.5 second cooldown
        self.last_damage_time: int = 0

        self.update_rect()

    def can_damage(self) -> bool:
        """Checks if the shield can deal damage based on cooldown."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time >= self.damage_cooldown_ms:
            return True
        return False

    def apply_damage(self) -> int:
        """Updates damage state and returns the damage to deal."""
        if self.can_damage():
            self.last_damage_time = pygame.time.get_ticks()
            self.hit_count += 1
            if self.hit_count >= self.max_hits:
                self.is_active = False
            return self.damage
        return 0

    def update_orbit(self, center_x: float, center_y: float) -> None:
        if not self.is_active:
            return

        self.angle += self.orbit_speed
        self.x = center_x + math.cos(self.angle) * self.orbit_radius
        self.y = center_y + math.sin(self.angle) * self.orbit_radius
        self.update_rect()

    def update(self):
        # orbit-only movement; external code supplies center via update_orbit
        pass


    def fire_metal_shield(self, damage: int = 20, max_hits: int = 3):
        """
        Activates the Metal Shield spell and returns the shield instance.
        """

        # Use the current position as the center for the new shield
        # The shield will orbit around this position
        shield = MetalShield(self.x, self.y, damage, max_hits)
        shield.weapon_name = "Metal Shield"
        return shield

    def absorb_hit(self) -> bool:
        if self.is_active and not self.has_blocked:
            self.has_blocked = True
            self.is_active = False
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (160, 160, 160), self.rect)
