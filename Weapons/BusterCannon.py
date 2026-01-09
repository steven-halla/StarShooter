import pygame
from Weapons.Bullet import Bullet
from Constants.Timer import Timer


class BusterCanon(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # -----------------
        # SINGLE SHOT STATS
        # -----------------
        self.damage = 1044
        self.bullet_speed = 4.0
        self.rate_of_fire = .5
        self.width = 12
        self.height = 12

        # -----------------
        # FIRE RATE CONTROL (THIS WAS MISSING)
        # -----------------
        self.bullet_timer = Timer(self.rate_of_fire)

        # -----------------
        # MOVEMENT VECTOR
        # -----------------
        self.vx = 0.0
        self.vy = -1.0

        # -----------------
        # IDENTITY
        # -----------------
        self.weapon_name = "Buster Cannon"

        # injected
        self.camera = None

        self.update_rect()

    # -----------------
    # FIRE (ROF GATED)
    # -----------------
    def fire_buster_cannon(self) -> list:
        if not self.bullet_timer.is_ready():
            return []

        bullet_x = self.x + self.width // 2
        bullet_y = self.y

        projectile = Bullet(bullet_x, bullet_y)

        projectile.width = self.width
        projectile.height = self.height
        projectile.vx = 0.0
        projectile.vy = -1.0
        projectile.bullet_speed = self.bullet_speed
        projectile.damage = self.damage
        projectile.camera = self.camera

        projectile.update_rect()

        print(
            f"[BUSTER] FIRED bullet at x={projectile.x} y={projectile.y} "
            f"size=({projectile.width}x{projectile.height}) "
            f"damage={projectile.damage}"
        )

        self.bullet_timer.reset()
        return [projectile]

    # -----------------
    # UPDATE
    # -----------------
    def update(self):
        self.update_rect()

    # -----------------
    # DRAW
    # -----------------
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (0, 128, 255), self.rect)
