# EnergyBall.py

import math
import pygame
from Weapons.Bullet import Bullet


class EnergyBall(Bullet):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

        self.width = 24
        self.height = 24

        self.weapon_name = "Energy Ball"
        self.damage = 5
        self.bullet_speed = 8.0

        self.rate_of_fire = 0.50
        self.last_fire_time = 0.0

        self.vx = 0.0
        self.vy = -1.0

        self.camera = None

        self.update_rect()

        # print(f"[EnergyBall INIT] x={self.x} y={self.y} rect={self.rect}")

    def can_fire(self) -> bool:
        now = pygame.time.get_ticks() / 1000.0
        can = (now - self.last_fire_time) >= self.rate_of_fire
        # print(f"[EnergyBall CAN_FIRE] can={can}")
        return can

    def try_fire(self, controller):
        if not self.can_fire():
            # print("[EnergyBall TRY_FIRE] blocked by ROF")
            return None

        vx = 0.0
        vy = 0.0

        if controller.left_button:
            vx -= 1.0
        if controller.right_button:
            vx += 1.0
        if controller.up_button:
            vy -= 1.0
        if controller.down_button:
            vy += 1.0

        if vx == 0.0 and vy == 0.0:
            vy = -1.0

        length = math.hypot(vx, vy)
        vx /= length
        vy /= length

        ball = EnergyBall(self.x, self.y)
        ball.vx = vx
        ball.vy = vy
        ball.bullet_speed = self.bullet_speed
        ball.camera = self.camera

        self.last_fire_time = pygame.time.get_ticks() / 1000.0

        # print(
        #     f"[EnergyBall SPAWN] "
        #     f"x={ball.x:.2f} y={ball.y:.2f} "
        #     f"vx={ball.vx:.2f} vy={ball.vy:.2f} "
        #     f"rect={ball.rect}"
        # )

        return ball

    def update(self) -> None:
        old_x, old_y = self.x, self.y

        self.x += self.vx * self.bullet_speed
        self.y += self.vy * self.bullet_speed
        self.update_rect()

        # print(
        #     f"[EnergyBall UPDATE] "
        #     f"from=({old_x:.2f},{old_y:.2f}) "
        #     f"to=({self.x:.2f},{self.y:.2f}) "
        #     f"rect={self.rect}"
        # )

        if self.camera is not None:
            visible_top = self.camera.y - 100
            visible_bottom = (
                self.camera.y
                + (self.camera.window_height / self.camera.zoom)
                + 100
            )

            if self.y + self.height < visible_top or self.y > visible_bottom:
                self.is_active = False
                # print("[EnergyBall CULL] went off-screen")

    @staticmethod
    def update_all(energy_balls: list["EnergyBall"]) -> None:
        for ball in list(energy_balls):
            ball.update()

            if not ball.is_active:
                # print(f"[EnergyBall REMOVE] x={ball.x} y={ball.y}")
                energy_balls.remove(ball)
