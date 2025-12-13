import pygame
from Weapons.Weapon import Weapon

class BusterCanon(Weapon):
    def __init__(self, x, y):
        super().__init__(x, y)

        # Damage values
        self.mp_cost: int = 10
        self.base_damage: int = 10
        self.charge_shot_damage: int = 40
        self.magic_name: str = "Buster Cannon"

        # Default projectile size (small shot)
        self.small_w: int = 12
        self.small_h: int = 12

        # Charged projectile size (4× bigger)
        self.big_w: int = self.small_w * 4
        self.big_h: int = self.small_h * 4

        self.width: int = self.small_w
        self.height: int = self.small_h

        self.speed: float = -5
        self.rateOfFire: float = 0.5

        # Charging system
        self.fully_charged: bool = False
        self.is_charging: bool = False
        self.charge_time: float = 0.0
        self.required_charge: float = 2.0  # seconds to charge fully

    # ------------------------
    # CHARGING CONTROL METHODS
    # ------------------------
    def start_charge(self):
        """Player begins holding the fire button."""
        self.is_charging = True
        self.charge_time = 0.0
        self.fully_charged = False
        self.width = self.small_w
        self.height = self.small_h

    def stop_charge(self):
        """Player releases the fire button."""
        self.is_charging = False

    def fire(self):
        """
        Returns the damage the projectile should have.
        Screen class will spawn a projectile using the correct size.
        """
        if self.fully_charged:
            dmg = self.charge_shot_damage
            # projectile should be big when fired
            self.width = self.big_w
            self.height = self.big_h
        else:
            dmg = self.base_damage
            # revert to small bullet size
            self.width = self.small_w
            self.height = self.small_h

        # After firing, reset charge state
        self.fully_charged = False
        self.charge_time = 0.0

        return dmg

    # ------------------------
    # UPDATE LOGIC
    # ------------------------
    def update(self):
        # Apply normal movement from Weapon base class
        super().update()

        # If charging, build charge
        if self.is_charging:

            self.charge_time += 1 / 60.0  # assuming 60 FPS
            print(self.charge_time)
            if self.charge_time >= self.required_charge:
                print("dfj;alsj;lfa")
                # Only announce the fully-charged state the first time we reach it
                if not self.fully_charged:
                    print("Buster Cannon: not fully charged!")
                self.charge_time = self.required_charge
                self.fully_charged = True
                self.width = self.big_w
                self.height = self.big_h
        else:
            # Reset charge and size when not charging
            self.charge_time = 0.0
            self.fully_charged = False
            self.width = self.small_w
            self.height = self.small_h

        self.update_rect()
