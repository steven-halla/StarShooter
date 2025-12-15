from Weapons.Weapon import Weapon
from Constants.Timer import Timer

class NapalmSpread(Weapon):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # VISUAL SIZE (projectile phase)
        self.width: int = 11
        self.height: int = 11

        # DAMAGE / EFFECT
        self.damage: int = 10
        self.duration: int = 1

        # AOE size (used after explosion)
        self.area_of_effect_x: int = 33
        self.area_of_effect_y: int = 33

        # MOVEMENT
        self.speed: float = 3.5
        self.dy: float = -self.speed  # forward (up)

        # STATE
        self.is_active: bool = True
        self.has_exploded: bool = False

        # MOVE FOR 2 SECONDS
        self.travel_time_seconds: float = .6
        self.travel_timer: Timer = Timer(self.travel_time_seconds)
        self.travel_timer.reset()
        self.NAPALM_SPREAD: str = "Napalm Spread"


    def update(self) -> None:
        # If already exploded, do nothing here
        if self.has_exploded:
            return

        # While travel timer is active → keep moving
        if not self.travel_timer.is_ready():
            self.y += self.dy
        else:
            # Stop moving and explode
            self.has_exploded = True
            self.is_active = False
