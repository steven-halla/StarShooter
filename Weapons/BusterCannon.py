import pygame
from Weapons.Bullet import Bullet


class BusterCanon(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # -----------------
        # BASE SHOT STATS
        # -----------------
        self.ki_cost = 1
        self.charged_ki_cost = 10
        self.base_damage = 2
        self.base_speed = 4
        self.base_width = 12
        self.base_height = 12

        # RATE OF FIRE (HERE)
        self.rate_of_fire = 0.4      # seconds
        self.last_fire_time = 0.0

        # -----------------
        # CHARGED SHOT STATS
        # -----------------
        self.charged_damage = 35
        self.charged_speed = 3.0
        self.charged_width = self.base_width * 2
        self.charged_height = self.base_height * 2
        self.charge_time_required = 3.0  # seconds

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
        # BURST PATTERN (3 shots in 2s -> lockout 2s)
        # -----------------
        self.burst_window_s: float = 2.3
        self.burst_max_shots: int = 3
        self.burst_lockout_s: float = 2.0

        self.burst_window_start: float | None = None
        self.burst_shots_in_window: int = 0
        self.lockout_until: float = 0.0
        self.is_locked_out: bool = False
        # -----------------
    # RATE OF FIRE CHECK
    # -----------------
    def can_fire(self) -> bool:
        now = pygame.time.get_ticks() / 1000.0

        # NEW: burst lockout gate (after 3 shots in 2.0s)
        if self.is_locked_out:
            return False

        # existing ROF gate
        return (now - self.last_fire_time) >= self.rate_of_fire
    # def can_fire(self) -> bool:
    #     now = pygame.time.get_ticks() / 1000.0
    #     return (now - self.last_fire_time) >= self.rate_of_fire

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

    def register_shot_for_burst_pattern(self) -> None:
        now = pygame.time.get_ticks() / 1000.0

        # start / reset burst window
        if self.burst_window_start is None or (now - self.burst_window_start) > self.burst_window_s:
            self.burst_window_start = now
            self.burst_shots_in_window = 0

        self.burst_shots_in_window += 1

        # if 3 shots happened inside the window -> lockout
        if self.burst_shots_in_window >= self.burst_max_shots:
            self.is_locked_out = True
            self.lockout_until = self.burst_window_start + self.burst_window_s
    # -----------------
    # FIRE
    # -----------------
    def fire_buster_cannon(self) -> tuple[list, int]:
        if not self.can_fire():
            return [], 0

        self.last_fire_time = pygame.time.get_ticks() / 1000.0

        # ✅ NEW: count this shot toward the 3-in-2.0s burst pattern
        self.register_shot_for_burst_pattern()

        projectile = Bullet(0, 0)

        cost = 0
        if self.is_fully_charged():
            projectile.width = self.charged_width
            projectile.height = self.charged_height
            projectile.damage = self.charged_damage
            projectile.bullet_speed = self.charged_speed
            cost = self.charged_ki_cost
        else:
            projectile.width = self.base_width
            projectile.height = self.base_height
            projectile.damage = self.base_damage
            projectile.bullet_speed = self.base_speed
            cost = self.ki_cost

        # Center the projectile on the cannon's position (which is the ship's center)
        projectile.x = self.x - (projectile.width // 2)
        projectile.y = self.y

        projectile.vx = 0.0
        projectile.vy = -1.0
        projectile.camera = self.camera
        projectile.update_rect()

        self.stop_charge()
        return [projectile], cost

    # -----------------
    # UPDATE
    # -----------------
    def check_burst_timer(self) -> None:
        """recurring timer that should live in update as a function"""
        if self.burst_window_start is None:
            return

        now = pygame.time.get_ticks() / 1000.0
        # if the 2-second window has passed, reset everything
        if now >= (self.burst_window_start + self.burst_window_s):
            self.is_locked_out = False
            self.burst_shots_in_window = 0
            self.burst_window_start = None

    def update(self):
        self.check_burst_timer()
        self.update_rect()

    # -----------------
    # DRAW
    # -----------------
    def draw(self, surface: pygame.Surface) -> None:
        color = (255, 64, 64) if self.is_fully_charged() else (0, 128, 255)
        pygame.draw.rect(surface, color, self.rect)
