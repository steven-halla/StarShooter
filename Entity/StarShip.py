# import pygame
# from Constants.GlobalConstants import GlobalConstants
# from Constants.Timer import Timer
# from Movement.MoveRectangle import MoveRectangle


import pygame
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet
from Weapons.Missile import Missile


class StarShip():
    def __init__(self):
        self.height: int = 16
        self.width: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.BLUE
        self.x: int = 0
        self.y: int = 0
        self.moveStarShip: MoveRectangle = MoveRectangle()
        self.speed: float = 3.0

        # firing stats for machien gun
        self.bullet_fire_interval_seconds: float = 0.05
        self.bullet_timer: Timer = Timer(self.bullet_fire_interval_seconds)
        self.bullet_spread_offset: int = 18
        self.bullets_per_shot: int = 2
        self.bulletDamage: int = 1
        # missile stats
        self.missile_fire_interval_seconds: float = 3.0
        self.missile_timer: Timer = Timer(self.missile_fire_interval_seconds)
        self.missileDamage: int = 100
        self.missileSpeed: int = 10
        self.missile_spread_offset: int = 20
        self.equipped_magic: list = [None, None]





        self.hitbox: pygame.Rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )
        self.was_hit: bool = False
        self.shipHealth: int = 50

        self.player_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

        # the below handles post hit invinciblity
        self.invincible: bool = False
        self.last_health: int = self.shipHealth
        self.invincibility_timer: Timer = Timer(2.0)

    def start_invincibility(self) -> None:
        # Begin a 10-second invincibility period
        self.invincible = True
        self.invincibility_timer.reset()

    def fire_missile(self):
        # Only fire if timer is ready
        if not self.missile_timer.is_ready():
            return None

        # Spawn position (center of ship)
        missile_x = self.x + self.width // 2
        missile_y = self.y

        # Create the missile
        missile = Missile(missile_x, missile_y)

        # Reset cooldown
        self.missile_timer.reset()

        return missile

    def fire_twin_linked_machinegun(self) -> list:
        # If the weapon is not ready, return no bullets
        if not self.bullet_timer.is_ready():
            return []

        bullets = []

        center_x = self.x + self.width // 2 + 10
        bullet_y = self.y

        spread = self.bullet_spread_offset
        count = self.bullets_per_shot
        start_index = -(count // 2)

        for i in range(count):
            offset = (start_index + i) * spread
            bullet_x = center_x + offset - Bullet.DEFAULT_WIDTH // 2

            bullet_world_x = bullet_x
            bullet_world_y = bullet_y

            bullets.append(Bullet(bullet_world_x, bullet_world_y))

        # Reset cooldown after firing
        self.bullet_timer.reset()

        return bullets

    def update(self) -> None:
        self.update_hitbox()
        # print(self.shipHealth)

        # Detect health drop → trigger invincibility
        # Detect health drop → trigger invincibility AND lock in new health
        if self.shipHealth < self.last_health and not self.invincible:
            self.last_health = self.shipHealth  # lock in the new lower HP
            self.start_invincibility()

        # If invincible, check if timer has finished
        if self.invincible:
            if self.invincibility_timer.is_ready():
                # End invincibility
                self.invincible = False
            else:
                # Ignore any incoming damage (freeze HP)
                self.shipHealth = self.last_health

        # After invincibility ends, allow last_health to match current HP normally
        if not self.invincible:
            self.last_health = self.shipHealth

    def draw(self, surface: pygame.Surface, camera):
        sprite_rect = pygame.Rect(10, 220, 32, 32)
        sprite = self.player_image.subsurface(sprite_rect)

        # scale ship with zoom
        scale = camera.zoom
        scaled_sprite = pygame.transform.scale(
            sprite,
            (int(self.width * scale), int(self.height * scale))
        )

        # convert world → screen
        screen_x = camera.world_to_screen_x(self.x)
        screen_y = camera.world_to_screen_y(self.y)

        # draw ship
        surface.blit(scaled_sprite, (screen_x, screen_y))

        # ================================
        #  DRAW PLAYER HITBOX (DEBUG)
        # ================================
        hb_x = camera.world_to_screen_x(self.hitbox.x)
        hb_y = camera.world_to_screen_y(self.hitbox.y)
        hb_w = int(self.hitbox.width * camera.zoom)
        hb_h = int(self.hitbox.height * camera.zoom)

        pygame.draw.rect(surface, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 2)


    def update_hitbox(self) -> None:
        self.hitbox.topleft = (int(self.x), int(self.y))

    def on_hit(self) -> None:
        if not self.was_hit:
            self.was_hit = True
            self.color = GlobalConstants.YELLOW
