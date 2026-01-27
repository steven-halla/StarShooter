import random
import math
import pygame
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Movement.MoveRectangle import MoveRectangle
from Weapons.Bullet import Bullet
from Weapons.BusterCannon import BusterCanon
from Weapons.EnergyBall import EnergyBall
from Weapons.BeamSaber import BeamSaber
from Weapons.MachineGun import MachineGun
from Weapons.MetalShield import MetalShield
from Weapons.Missile import Missile
from Weapons.NapalmSpread import NapalmSpread
from Weapons.PlasmaBlaster import PlasmaBlaster
from Weapons.WaveCrash import WaveCrash
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
        self.shipHealthMax: int = 150
        self.camera = None
        self.equipped_magic: list = ["Napalm Spread", None]
        self.napalm_fire_interval_seconds: float = 3.5
        self.napalm_timer: Timer = Timer(self.napalm_fire_interval_seconds)
        self.hitbox: pygame.Rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )
        # -------------------------
        # DAMAGE VISUAL EFFECT
        # -------------------------
        self.is_electrocuted: bool = False
        self.electric_start_time: int = 0
        self.electric_duration_ms: int = 180
        self.was_hit: bool = False
        self.shipHealth: int = 150

        self.player_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

        # the below handles post hit invinciblity
        self.invincible: bool = False
        self.last_health: int = self.shipHealth
        self.invincibility_timer: Timer = Timer(2.0)
        # ------------------------
        # machine gun
        # -------------------------
        self.machine_gun = MachineGun(self.x, self.y)
        # -------------------------
        # Missile
        # -------------------------
        self.missile = Missile(self.x, self.y)
        # -------------------------
        # Buster cannon
        # -------------------------
        self.buster_cannon = BusterCanon(self.x, self.y)
        # -------------------------
        # Energy ball
        # -------------------------
        self.energy_ball = EnergyBall(self.x, self.y)
        # -------------------------
        # Beam saber
        # -------------------------
        self.beam_saber = BeamSaber(self.x, self.y)
        # -------------------------
        # Metal Shield
        # -------------------------
        self.metal_shield = MetalShield(self.x, self.y)
        # -------------------------
        # Plasma Blaster
        # -------------------------
        self.plasma_blaster = PlasmaBlaster(self.x, self.y)
        # -------------------------
        # Wave Crash
        # -------------------------
        self.wave_crash = WaveCrash(self.x, self.y)

        # -------------------------
        # Wind Slicer
        # -------------------------
        self.wind_slicer = WindSlicer(self.x, self.y)
        # -------------------------
        # Napalm Spread
        # -------------------------
        self.napalm_spread = NapalmSpread(self.x, self.y)

    def start_invincibility(self) -> None:
        # Begin a 10-second invincibility period
        self.invincible = True
        self.invincibility_timer.reset()

    def update(self) -> None:
        print(self.shipHealth)
        self.update_hitbox()
        # -------------------------
        # Machine Gun
        # -------------------------
        self.machine_gun.x = self.x
        self.machine_gun.y = self.y
        self.machine_gun.update()
        # -------------------------
        # Missile
        # -------------------------
        self.missile.reload_missiles()
        # -------------------------
        # buster cannon
        # -------------------------
        self.buster_cannon.x = self.x + self.width // 2
        self.buster_cannon.y = self.y
        self.buster_cannon.update()
        # -------------------------
        # enegy ball
        # -------------------------
        self.energy_ball.x = self.x + self.width / 2
        self.energy_ball.y = self.y + self.height / 2
        self.energy_ball.update()
        # ------------------------
        # Beam Saber
        # -------------------------
        self.beam_saber.x = self.x + self.width // 2
        self.beam_saber.y = self.y
        self.beam_saber.update()
        # -------------------------
        # Metal Shield
        # -------------------------
        self.metal_shield.x = self.x + self.width // 2
        self.metal_shield.y = self.y
        self.metal_shield.update()
        # -------------------------
        # Plasma blaster
        # -------------------------
        self.plasma_blaster.x = self.x + self.width // 2
        self.plasma_blaster.y = self.y
        self.plasma_blaster.update()
        # -------------------------
        # Wave Crash
        # -------------------------
        self.wave_crash.x = self.x + self.width // 2
        self.wave_crash.y = self.y
        self.wave_crash.update()
        # -------------------------
        # Wind Slicr
        # -------------------------
        self.wind_slicer.x = self.x + self.width // 2
        self.wind_slicer.y = self.y
        self.wind_slicer.update()
        # -------------------------
        # Napalm Spread
        # -------------------------
        self.napalm_spread.x = self.x + self.width // 2
        self.napalm_spread.y = self.y
        self.napalm_spread.update()
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
