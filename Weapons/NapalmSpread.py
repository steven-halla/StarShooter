import pygame
from Weapons.Bullet import Bullet
from Constants.Timer import Timer


class NapalmSpread(Bullet):

    napalm_active: bool = False

    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        print("[INIT] Napalm created")

        self.weapon_name: str = "Napalm Spread"

        self.width: int = 11
        self.height: int = 11

        self.damage: int = 75
        self.rate_of_fire: float = 1.0
        self.bullet_speed: float = 3.5

        self.napalm_timer: Timer = Timer(self.rate_of_fire)

        self.vx: float = 0.0
        self.vy: float = -1.0

        self.damage_tick_seconds: float = 1.0
        self.damage_timer: Timer = Timer(self.damage_tick_seconds)
        self.damage_timer.reset()

        self.duration: int = 3
        self.area_of_effect_x: int = 33
        self.area_of_effect_y: int = 33

        self.travel_time_seconds: float = 0.6
        self.travel_timer: Timer = Timer(self.travel_time_seconds)
        self.travel_timer.reset()

        self.explosion_time_seconds: float = 3.4
        self.explosion_timer: Timer = Timer(self.explosion_time_seconds)

        self.is_active: bool = True
        self.has_exploded: bool = False
        self.aoe_applied: bool = False

        self.explosion_unlock_processed: bool = False

        self.update_rect()

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self) -> None:

        # -----------------------
        # TRAVEL PHASE
        # -----------------------
        if not self.has_exploded:
            if not self.travel_timer.is_ready():
                super().update()
            else:
                print("[UPDATE] Trigger explosion")
                self.trigger_explosion()
            return

        # -----------------------
        # EXPLOSION PHASE
        # -----------------------
        if self.explosion_timer.is_ready() and not self.explosion_unlock_processed:

            print("[UPDATE] Explosion finished — unlocking napalm")

            self.is_active = False
            NapalmSpread.napalm_active = False
            print("[UPDATE] napalm_active:", NapalmSpread.napalm_active)

            self.napalm_timer.reset()
            print("[UPDATE] Cooldown reset")

            self.explosion_unlock_processed = True

    # --------------------------------------------------
    # FIRE METHOD (STAYS IN CLASS)
    # --------------------------------------------------
    def fire_napalm_spread(self):

        print("[FIRE] napalm_active:", NapalmSpread.napalm_active)
        print("[FIRE] cooldown ready:", self.napalm_timer.is_ready())

        # HARD LOCK
        if NapalmSpread.napalm_active:
            print("[BLOCKED] Napalm already active")
            return None

        # COOLDOWN CHECK
        if not self.napalm_timer.is_ready():
            print("[BLOCKED] Cooldown not ready")
            return None

        start_x = self.x + self.width / 2
        start_y = self.y

        napalm = NapalmSpread(start_x, start_y)

        NapalmSpread.napalm_active = True
        print("[FIRE] Napalm activated")

        self.napalm_timer.reset()
        print("[FIRE] Cooldown timer reset")

        return napalm

    # --------------------------------------------------
    # AOE HITBOX
    # --------------------------------------------------
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

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if not self.has_exploded:
            pygame.draw.rect(surface, (255, 120, 0), self.rect)
        else:
            aoe = self.getAoeHitbox()
            if aoe:
                pygame.draw.rect(surface, (255, 60, 0), aoe, 2)

    # --------------------------------------------------
    # TRIGGER EXPLOSION
    # --------------------------------------------------
    def trigger_explosion(self) -> None:
        if self.has_exploded:
            return

        print("[EXPLOSION] Explosion triggered")

        self.has_exploded = True
        self.vx = 0.0
        self.vy = 0.0

        self.explosion_timer.reset()
        self.damage_timer.reset()
