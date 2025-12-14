from Weapons.Weapon import Weapon

class WaveCrash(Weapon):
    def __init__(self, x: float, y: float, direction: int):
        super().__init__(x, y)

        self.width = 12
        self.height = 22
        self.rateOfFire = 0.5
        self.speed = 0          # no vertical movement
        self.dx = 6 * direction # -1 = left, +1 = right
        self.damage = 6
        self.WAVE_CRASH: str = "Wave Crash"

