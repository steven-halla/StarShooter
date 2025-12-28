# import pygame
# from Constants.GlobalConstants import GlobalConstants
# from Constants.Timer import Timer
# from Movement.MoveRectangle import MoveRectangle
import random

import math

import pygame
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet
from Weapons.BusterCannon import BusterCanon
from Weapons.EnergyBall import EnergyBall
from Weapons.HyperLaser import HyperLaser
from Weapons.MetalShield import MetalShield
from Weapons.Missile import Missile
from Weapons.NapalmSpread import NapalmSpread
from Weapons.PlasmaBlaster import PlasmaBlaster
from Weapons.WindSlicer import WindSlicer


class StarShip:
    def __init__(self):
        self.height: int = 16

        self.width: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.BLUE
        self.x: int = 0
        self.y: int = 0
        self.moveStarShip: MoveRectangle = MoveRectangle()
        self.speed: float = 3.0
        self.buster_cannon_cooldown = Timer(0.25)
        # the weapon itself manages charge status
        self.buster_cannon = BusterCanon(self.x, self.y)

        self.shipHealthMax: int = 150

        # firing stats for machien gun
        self.bullet_fire_interval_seconds: float = 0.05
        self.bullet_timer: Timer = Timer(self.bullet_fire_interval_seconds)
        self.bullet_spread_offset: int = 18
        self.bullets_per_shot: int = 2
        self.bulletDamage: int = 1
        # missile stats
        self.missile_fire_interval_seconds: float = 3.0
        self.missile_timer: Timer = Timer(self.missile_fire_interval_seconds)
        self.hyper_laser_fire_interval_seconds: float = .1
        self.hyper_laser_timer: Timer = Timer(self.hyper_laser_fire_interval_seconds)
        self.energy_ball_fire_interval_seconds: float = 1.2
        self.energy_ball_timer: Timer = Timer(self.energy_ball_fire_interval_seconds)
        self.missileDamage: int = 100
        self.missileSpeed: int = 10
        self.missile_spread_offset: int = 20
        self.equipped_magic: list = ["Buster Cannon", None]
        self.hyper_laser_damage: int = 100
        self.napalm_fire_interval_seconds: float = 3.5
        self.napalm_timer: Timer = Timer(self.napalm_fire_interval_seconds)

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

        # -------------------------
        # WAVE CRASHER STATS
        # -------------------------
        self.wave_crash_cooldown_seconds: float = 0.4
        self.wave_crash_timer: Timer = Timer(self.wave_crash_cooldown_seconds)

        self.wave_crash_damage: int = 6
        self.wave_crash_speed: int = 6
        self.wave_crash_width: int = 12
        self.wave_crash_height: int = 12

        # -------------------------
        # DAMAGE VISUAL EFFECT
        # -------------------------
        self.is_electrocuted: bool = False
        self.electric_start_time: int = 0
        self.electric_duration_ms: int = 180

    def start_invincibility(self) -> None:
        # Begin a 10-second invincibility period
        self.invincible = True
        self.invincibility_timer.reset()



    def fire_napalm_spread(self):
        """
        Fires a Napalm Spread grenade forward.
        Returns a NapalmSpread instance or None if on cooldown.
        """

        # Rate-of-fire gate
        if not self.napalm_timer.is_ready():
            return None

        # Spawn slightly in front of the ship
        start_x = self.x + self.width / 2
        start_y = self.y

        napalm = NapalmSpread(start_x, start_y)

        # Reset cooldown
        self.napalm_timer.reset()

        return napalm

    def fire_buster_cannon(self):
        """Use the BusterCanon’s own state to determine projectile size/damage."""
        if not self.buster_cannon_cooldown.is_ready():
            return []

        # ask the weapon what kind of shot to fire; this resets its charge state
        damage = self.buster_cannon.fire()
        # the weapon’s width/height have been set by its own fire() method
        projectile = Bullet(self.x + self.width // 2, self.y)

        projectile.shot_type = (
            self.buster_cannon.CHARGED_BUSTER_SHOT
            if self.buster_cannon.fully_charged
            else self.buster_cannon.NORMAL_BUSTER_SHOT
        )

        projectile.width = self.buster_cannon.width
        projectile.height = self.buster_cannon.height
        projectile.speed = self.buster_cannon.speed
        projectile.damage = damage
        projectile.update_rect()
        # projectile = Bullet(self.x + self.width // 2, self.y)
        # projectile.width = self.buster_cannon.width
        # projectile.height = self.buster_cannon.height
        # projectile.speed = self.buster_cannon.speed
        # projectile.damage = damage

        self.buster_cannon_cooldown.reset()
        return [projectile]

    def fire_plasma_blaster(self):
        """
        Fires a Plasma Blaster beam straight upward.
        """

        # Spawn at center-top of ship
        start_x = self.x + self.width / 2
        start_y = self.y - 50

        plasma = PlasmaBlaster(start_x, start_y)
        return plasma

    def fire_wind_slicer(self) -> list:
        bullets = []

        # fire rate gate (reuse napalm timer or add a new one later)
        if not self.napalm_timer.is_ready():
            return bullets

        center_x = self.x + self.width / 2
        start_y = self.y

        bullet_count = 8
        cone_angle_deg = 60  # total cone width
        start_angle = -90 - cone_angle_deg / 2  # straight up = -90°
        angle_step = cone_angle_deg / (bullet_count - 1)
        speed = 3

        for i in range(bullet_count):
            angle = math.radians(start_angle + i * angle_step)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            bullet = WindSlicer(center_x, start_y, dx, dy)
            bullets.append(bullet)

        self.napalm_timer.reset()  # reuse cooldown for now
        return bullets

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

    def fire_hyper_laser(self):
        # Only fire if timer is ready
        if not self.hyper_laser_timer.is_ready():
            return None

        # Create the laser ATTACHED to the ship
        hyper_laser = HyperLaser(self)

        # Reset cooldown
        self.hyper_laser_timer.reset()

        return hyper_laser

    def fire_metal_shield(self):
        """
        Activates the Metal Shield spell and returns the shield instance.
        """

        # Center of the ship in world space
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        shield = MetalShield(center_x, center_y)
        return shield

    def fire_wave_crash(self) -> list:
        print("yah")

        """
        Fires Wave Crash shots simultaneously to the left and right.
        """
        if not self.wave_crash_timer.is_ready():
            return []

        bullets = []

        spawn_x = self.x + self.width // 2
        spawn_y = self.y

        # LEFT shot
        left = Bullet(spawn_x, spawn_y)
        left.width = self.wave_crash_width
        left.height = self.wave_crash_height
        left.damage = self.wave_crash_damage
        left.speed = 0
        left.dx = -self.wave_crash_speed
        left.update_rect()

        # RIGHT shot
        right = Bullet(spawn_x, spawn_y)
        right.width = self.wave_crash_width
        right.height = self.wave_crash_height
        right.damage = self.wave_crash_damage
        right.speed = 0
        right.dx = self.wave_crash_speed
        right.update_rect()

        bullets.append(left)
        bullets.append(right)

        self.wave_crash_timer.reset()
        return bullets

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

    def fire_energy_ball(self, dx: float, dy: float):
        # Rate-of-fire gate
        if not self.energy_ball_timer.is_ready():
            return None

        # Spawn at center of ship
        start_x = self.x + self.width / 2
        start_y = self.y + self.height / 2

        energy_ball = EnergyBall(start_x, start_y, dx, dy)

        # Reset cooldown
        self.energy_ball_timer.reset()

        return energy_ball

    def update(self) -> None:
        self.update_hitbox()

        # --------------------------------
        # DETECT DAMAGE (HEALTH DROP)
        # --------------------------------
        if self.shipHealth < self.last_health and not self.invincible:
            # trigger invincibility
            self.invincible = True
            self.invincibility_timer.reset()

            # trigger electric visual
            self.is_electrocuted = True
            self.electric_start_time = pygame.time.get_ticks()

            # lock health
            self.last_health = self.shipHealth

        # --------------------------------
        # INVINCIBILITY TIMER
        # --------------------------------
        if self.invincible:
            if self.invincibility_timer.is_ready():
                self.invincible = False
            else:
                # freeze health during invincibility
                self.shipHealth = self.last_health

        if not self.invincible:
            self.last_health = self.shipHealth

        # --------------------------------
        # ELECTRIC VISUAL TIMER (GRAPHICS ONLY)
        # --------------------------------
        if self.is_electrocuted:
            if pygame.time.get_ticks() - self.electric_start_time >= self.electric_duration_ms:
                self.is_electrocuted = False

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

        if self.is_electrocuted:
            self.draw_electric_effect(surface, camera)

    def update_hitbox(self) -> None:
        self.hitbox.topleft = (int(self.x), int(self.y))

    def on_hit(self) -> None:
        if self.invincible:
            return

        self.was_hit = True
        self.is_electrocuted = True
        self.electric_start_time = pygame.time.get_ticks()

    def draw_electric_effect(self, surface: pygame.Surface, camera) -> None:
        cx = camera.world_to_screen_x(self.x + self.width / 2)
        cy = camera.world_to_screen_y(self.y + self.height / 2)
        scale = camera.zoom

        for _ in range(6):
            points = [(cx, cy)]
            angle = random.uniform(0, math.tau)
            length = random.randint(int(10 * scale), int(24 * scale))

            x, y = cx, cy
            for _ in range(random.randint(4, 7)):
                angle += random.uniform(-0.6, 0.6)
                x += math.cos(angle) * (length / 6)
                y += math.sin(angle) * (length / 6)
                points.append((x, y))

            pygame.draw.lines(
                surface,
                (120, 200, 255),
                False,
                points,
                2
            )
