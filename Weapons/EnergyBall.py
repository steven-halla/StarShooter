from Weapons.Weapon import Weapon


class EnergyBall(Weapon):
    def __init__(self, x: float, y: float, dx: float, dy: float):
        super().__init__(x, y)

        self.width: int = 12
        self.height: int = 12
        self.damage: int = 10
        self.rateOfFire: float = 0.5

        self.dx: float = dx
        self.dy: float = dy

        self.is_active: bool = True

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy

