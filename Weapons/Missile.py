import pygame

from Weapons.Weapon import Weapon


class Missile(Weapon):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 12
        self.height = 12
        self.speed = -2.5 # -5 original value
        self.rateOfFire = .5
        self.missileNumber = 1
        self.damage = 3  # Adding damage property that was missing

        # Set Missile-specific diagonal movement
        self.diag_speed_y = 3

        # Initialize target_enemy to None (used in update method)
        self.target_enemy = None

    # update_rect() method is inherited from Weapon class

    def update(self) -> None:
        # If target is gone, dead, or off-screen → clear target
        if (self.target_enemy is None or
                self.target_enemy.enemyHealth <= 0):
            self.target_enemy = None

        # --- HOMING LOGIC ---
        if self.target_enemy is not None:
            dx = self.target_enemy.x - self.x
            dy = self.target_enemy.y - self.y
            dist = max(1, (dx * dx + dy * dy) ** 0.5)
            print(f"Homing → Target at ({self.target_enemy.x}, {self.target_enemy.y})")

            # normalized direction
            self.direction_x = dx / dist
            self.direction_y = dy / dist

            # apply missile speed toward target
            speed = abs(self.speed)
            self.x += self.direction_x * speed
            self.y += self.direction_y * speed

            # Keep hitbox matched to position
            self.update_rect()
        else:
            # --- DEFAULT (non-homing) MOVEMENT ---
            super().update()  # Use parent class update for non-homing movement


    # draw() and collide_with_rect() methods are inherited from Weapon class
