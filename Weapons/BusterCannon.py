import pygame
from Weapons.Bullet import Bullet


class BusterCanon(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # -----------------
        # SHOT MODES
        # -----------------
        self.SHOT_NORMAL = "NORMAL"
        self.SHOT_CHARGED = "CHARGED"
        self.shot_type = self.SHOT_NORMAL

        # -----------------
        # NORMAL SHOT STATS
        # -----------------
        self.normal_damage = 10
        self.normal_bullet_speed = 5.0
        self.normal_rate_of_fire = 1.0
        self.normal_width = 12
        self.normal_height = 12

        # -----------------
        # CHARGED SHOT STATS
        # -----------------
        self.charged_damage = 40
        self.charged_bullet_speed = 3.0
        self.charged_rate_of_fire = 0.25
        self.charged_width = 48
        self.charged_height = 48

        # -----------------
        # ACTIVE STATS
        # -----------------
        self.damage = self.normal_damage
        self.bullet_speed = self.normal_bullet_speed
        self.rate_of_fire = self.normal_rate_of_fire
        self.width = self.normal_width
        self.height = self.normal_height

        # -----------------
        # DIRECTION
        # -----------------
        self.vx = 0.0
        self.vy = -1.0

        # -----------------
        # CHARGING
        # -----------------
        self.mp_cost = 10
        self.weapon_name = "Buster Cannon"
        self.is_charging = False
        self.fully_charged = False
        self.charge_time = 0.0
        self.required_charge = 2.0

        # self.update_rect()

    # -----------------
    # CHARGE CONTROL
    # -----------------
    def start_charge(self):
        self.is_charging = True
        self.charge_time = 0.0
        self.fully_charged = False
        self.set_normal_shot()

    def stop_charge(self):
        self.is_charging = False

    # -----------------
    # SHOT MODE SETTERS
    # -----------------
    def set_normal_shot(self):
        self.shot_type = self.SHOT_NORMAL
        self.damage = self.normal_damage
        self.bullet_speed = self.normal_bullet_speed
        self.rateOfFire = self.normal_rate_of_fire
        self.width = self.normal_width
        self.height = self.normal_height

    def set_charged_shot(self):
        self.shot_type = self.SHOT_CHARGED
        self.damage = self.charged_damage
        self.bullet_speed = self.charged_bullet_speed
        self.rateOfFire = self.charged_rate_of_fire
        self.width = self.charged_width
        self.height = self.charged_height

    # -----------------
    # FIRE
    # -----------------
    def fire(self) -> int:
        if self.fully_charged:
            self.set_charged_shot()
        else:
            self.set_normal_shot()

        self.fully_charged = False
        self.charge_time = 0.0
        return self.damage

    # -----------------
    # UPDATE
    # -----------------
    def update(self):
        super().update()

        if self.is_charging:
            self.charge_time += 1 / 60.0
            if self.charge_time >= self.required_charge:
                self.charge_time = self.required_charge
                self.fully_charged = True
        else:
            self.charge_time = 0.0
            self.fully_charged = False

        self.update_rect()

    # -----------------
    # DRAW
    # -----------------
    def draw(self, surface: pygame.Surface) -> None:
        if self.shot_type == self.SHOT_CHARGED:
            color = (0, 255, 255)   # cyan for charged
        else:
            color = (0, 128, 255)   # blue for normal

        pygame.draw.rect(surface, color, self.rect)
