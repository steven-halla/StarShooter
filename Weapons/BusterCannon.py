import pygame

from Weapons.Weapon import Weapon


class BusterCanon(Weapon):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.mp_cost: int = 10
        self.base_damage: int = 10
        self.charge_shot_damage: int = 40
        self.width: int = 12
        self.height: int = 12
        self.speed: float = -5
        self.rateOfFire: float = .5



    # All methods inherited from Weapon class
