from Weapons.Weapon import Weapon

from Weapons.Weapon import Weapon

class WindSlicer(Weapon):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        self.width = 12
        self.height = 12
        self.damage = 10

        self.speed = 3          # slow-moving
        self.is_active = True

        self.WIND_SLICER: str = "Wind Slicer"

    def update(self) -> None:
        # move upward toward top of screen
        self.y -= self.speed





