import pygame
from Weapons.Bullet import Bullet
from Constants.Timer import Timer


class NapalmSpread(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        self.weapon_name: str = "Napalm Spread"

        # -----------------
        # SIZE (PROJECTILE)
        # -----------------
        self.width: int = 11
        self.height: int = 11

        # -----------------
        # STATS
        # -----------------
        self.damage: int = 75
        self.rate_of_fire: float = 0.0
        self.bullet_speed: float = 3.5
        self.napalm_timer: Timer = Timer(self.rate_of_fire)

        # -----------------
        # MOVEMENT VECTOR
        # -----------------
        self.vx: float = 0.0
        self.vy: float = -1.0

        # -----------------
        # AOE / DAMAGE TICKS
        # -----------------
        self.damage_tick_seconds: float = 1.0
        self.damage_timer: Timer = Timer(self.damage_tick_seconds)
        self.damage_timer.reset()

        self.duration: int = 3
        self.area_of_effect_x: int = 33
        self.area_of_effect_y: int = 33

        # -----------------
        # TIMERS
        # -----------------
        self.travel_time_seconds: float = 0.6
        self.travel_timer: Timer = Timer(self.travel_time_seconds)
        self.travel_timer.reset()

        self.explosion_time_seconds: float = 3.4
        self.explosion_timer: Timer = Timer(self.explosion_time_seconds)

        # -----------------
        # STATE
        # -----------------
        self.is_active: bool = True
        self.has_exploded: bool = False
        self.aoe_applied: bool = False

        self.update_rect()

    def update(self) -> None:
        # TRAVEL PHASE
        if not self.has_exploded:
            if not self.travel_timer.is_ready():
                super().update()
            else:
                self.has_exploded = True
                self.explosion_timer.reset()
                self.damage_timer.reset()
            return

        # EXPLOSION PHASE
        if self.explosion_timer.is_ready():
            self.is_active = False

    def fire_napalm_spread(self):
        """
        Fires a Napalm Spread grenade forward.
        Returns a NapalmSpread instance or None if on cooldown.
        """

        # Rate-of-fire gate
        if not self.napalm_timer.is_ready():
            return None

        # Spawn slightly in front of the ship
        start_x = self.x + self.width / 2
        start_y = self.y

        napalm = NapalmSpread(start_x, start_y)

        # Reset cooldown
        self.napalm_timer.reset()

        return napalm

    def getAoeHitbox(self):
        if not self.has_exploded:
            return None

        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        return pygame.Rect(
            center_x - self.area_of_effect_x // 2,
            center_y - self.area_of_effect_y // 2,
            self.area_of_effect_x,
            self.area_of_effect_y
        )

    def draw(self, surface: pygame.Surface) -> None:
        if not self.has_exploded:
            pygame.draw.rect(surface, (255, 120, 0), self.rect)
        else:
            aoe = self.getAoeHitbox()
            if aoe:
                pygame.draw.rect(surface, (255, 60, 0), aoe, 2)
