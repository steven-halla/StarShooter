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
        self.duration: int = 3
        self.explosion_active: bool = False
        self.aoe_applied: bool = False

        # AOE size (used after explosion)
        self.area_of_effect_x: int = 33
        self.area_of_effect_y: int = 33
        # EXPLOSION VISUAL TIMER
        self.explosion_time_seconds: float = 3.4
        self.explosion_timer: Timer = Timer(self.explosion_time_seconds)

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
        self.aoe_applied: bool = False


    def update(self) -> None:
        # -------------------------
        # MOVING PHASE
        # -------------------------
        if not self.has_exploded:
            if not self.travel_timer.is_ready():
                self.y += self.dy
            else:
                self.has_exploded = True
                self.explosion_active = True
                self.explosion_timer.reset()
            return

        # -------------------------
        # EXPLOSION PHASE
        # -------------------------
        if self.explosion_active:
            print("🔥 NAPALM EXPLODING")

            if self.explosion_timer.is_ready():
                self.explosion_active = False
                self.is_active = False
