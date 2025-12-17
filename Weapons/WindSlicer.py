from Weapons.Weapon import Weapon

class WindSlicer(Weapon):
    def __init__(self, x: float, y: float, dx: float, dy: float):
        super().__init__(x, y)

        self.width = 12
        self.height = 12
        self.damage = 10

        self.speed = 3
        self.dx = dx
        self.dy = dy
        self.is_active = True

        self.WIND_SLICER: str = "Wind Slicer"

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy



