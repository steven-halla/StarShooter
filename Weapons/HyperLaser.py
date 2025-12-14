from Weapons.Weapon import Weapon


class HyperLaser:
    def __init__(self, owner):
        self.owner = owner

        self.width = 12
        self.height = 60

        # Initial position (will be corrected every frame later)
        self.x = owner.x + owner.width / 2 - self.width / 2
        self.y = owner.y - self.height

        self.HYPER_LASER: str = "Hyper Laser"

    def update(self):
        self.x = self.owner.x + self.owner.width / 2 - self.width / 2
        self.y = self.owner.y - self.height
