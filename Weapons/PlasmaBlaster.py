from Weapons.Weapon import Weapon


class PlasmaBlaster(Weapon):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.width = 12
        self.height = 60
        self.damage = 10

        self.speed = 5

        self.is_active = True

        self.WIND_SLICER: str = "Plasma Blaster"


    def update(self) -> None:

        self.y -= self.speed
