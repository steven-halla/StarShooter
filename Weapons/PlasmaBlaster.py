import pygame
from Weapons.Bullet import Bullet


class PlasmaBlaster(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        # size
        self.width: int = 12
        self.height: int = 60

        # identity
        self.weapon_name: str = "Plasma Blaster"

        # stats
        self.damage: int = 10
        self.bullet_speed: float = 5.0

        # movement vector (straight up)
        self.vx: float = 0.0
        self.vy: float = -1.0

        # state
        self.is_active: bool = True

        # -----------------
        # RATE OF FIRE
        # -----------------
        self.rate_of_fire: float = 0.10
        self.last_fire_time: float = 0.0
        self.update_rect()
        self.camera = None



    def update(self) -> None:
        # movement handled by Bullet using vx/vy and bullet_speed
        super().update()


    def can_fire(self) -> bool:
        now = pygame.time.get_ticks() / 1000.0
        return (now - self.last_fire_time) >= self.rate_of_fire

    def fire_plasma_blaster(self):
        """
        Fires a Plasma Blaster beam straight upward.
        """
        if not self.can_fire():
            return None

        # Spawn at center-top of ship
        start_x = self.x + self.width / 2
        start_y = self.y - 50

        plasma = PlasmaBlaster(start_x, start_y)
        print(
            f"[BeamSaber SPAWN] "
            f"x={plasma.x:.2f} y={plasma.y:.2f} "
            f"rect={plasma.rect}"
        )

        return plasma

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (0, 255, 255), self.rect)
