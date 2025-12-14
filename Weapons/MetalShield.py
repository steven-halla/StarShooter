import math

from Weapons.Weapon import Weapon


class MetalShield(Weapon):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        self.width = 32
        self.height = 32

        self.orbit_radius: float = 40.0
        self.orbit_speed: float = 0.08   # radians per frame
        self.angle: float = 0.0

        self.is_active: bool = True
        self.has_blocked: bool = False

        self.METAL_SHIELD: str = "Metal Shield"

    def update_orbit(self, player_x: float, player_y: float) -> None:
        """
        Keeps the shield orbiting around the player.
        Call once per frame.
        """

        if not self.is_active:
            return

        self.angle += self.orbit_speed

        self.x = player_x + math.cos(self.angle) * self.orbit_radius
        self.y = player_y + math.sin(self.angle) * self.orbit_radius

    def absorb_hit(self) -> bool:
        """
        Returns True if the hit was absorbed.
        """
        if self.is_active and not self.has_blocked:
            self.has_blocked = True
            self.is_active = False
            return True
        return False
