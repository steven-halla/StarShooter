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
from ShipEngine.Shield import Shield

class StarShip:
    def __init__(self):
        self.height: int = 16
        self.width: int = 16
        self.color: tuple[int, int, int] = GlobalConstants.BLUE
        self.x: int = 0
        self.y: int = 0
        self.moveStarShip: MoveRectangle = MoveRectangle()

        self.camera = None
        self.equipped_magic: list = ["", None]
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

        self.player_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()

        # the below handles post hit invinciblity
        self.invincible: bool = False
        # ------------------------
        # machine gun
        # -------------------------
        self.machine_gun = MachineGun(self.x, self.y)

        self.machine_gun_damage = self.machine_gun.damage
        self.machine_gun_width = self.machine_gun.width
        self.machine_gun_height = self.machine_gun.height
        self.machine_gun_rate_of_fire = self.machine_gun.rate_of_fire
        self.machine_gun_bullet_speed = self.machine_gun.bullet_speed
        self.machine_gun_bullets_per_shot = self.machine_gun.bullets_per_shot


        # -------------------------
        # Missile
        # -------------------------
        self.missile = Missile(self.x, self.y)

        # -------------------------
        # MISSILE STATS (PLAYER-OWNED)
        # -------------------------
        self.missile_damage = self.missile.damage
        self.missile_bullet_speed = self.missile.bullet_speed
        self.missile_rate_of_fire = self.missile.rate_of_fire

        self.missile_max = self.missile.max_missiles
        self.missile_current = self.missile.current_missiles

        self.missile_fire_interval_seconds = self.missile.missile_fire_interval_seconds
        self.missile_timer = Timer(self.missile_fire_interval_seconds)

        self.missile_regen_interval_seconds = self.missile.missile_regen_interval_seconds
        self.missile_regen_timer = Timer(self.missile_regen_interval_seconds)
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

        # -------------------------
        # Player Data that needs to be saved,
        # the below can get UPGRADED
        # -------------------------
        self.speed: float = 3.0
        self.shipHealth: int = 150
        self.shipHealthMax: int = 150
        self.invincibility_timer: Timer = Timer(2.0)
        self.upgrade_chips: list = [""]
        self.upgrade_chips = [
            "max_missiles_plus_two"
        ]
        self.player_ki: int = 50
        self.player_max_ki: int = 50
        self.current_heat: int = 100
        self.max_heat: int = 100
        self.shield_system = Shield(100, 1.1, 3000)
        self.shield_system.owner = self
        self.current_shield: int = 100
        self.max_shield: int = 100

        # -------------------------
        # DO NOT SAVE BELOW TO PLAYER SAVE FILE
        # -------------------------
        self.frozen_health = self.shipHealth
        self.last_health = self.shipHealth




    def start_invincibility(self) -> None:
        # Begin a 10-second invincibility period
        self.invincible = True
        self.invincibility_timer.reset()

    def update(self) -> None:
        # print(self.shipHealth)
        self.update_hitbox()
        self.shield_system.update()
        self.current_shield = int(self.shield_system.current_shield_points)
        self.max_shield = self.shield_system.max_shield_points
        print(self.current_shield)
        ############
        # Be sure to change the below to use as an for loop to check what you ahve equiped so we dont update all the time
        #############
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
        self.missile_current = self.missile.current_missiles
        self.missile_max = self.missile.max_missiles
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
            self.on_hit()

            # trigger invincibility
            self.invincible = True
            self.invincibility_timer.reset()

            # lock health to current health (after taking damage)
            self.frozen_health = self.shipHealth
            self.last_health = self.shipHealth

        # --------------------------------
        # INVINCIBILITY TIMER
        # --------------------------------
        if self.invincible:
            if self.invincibility_timer.is_ready():
                self.invincible = False
                # Update last_health and frozen_health when invincibility ends
                self.last_health = self.shipHealth
                self.frozen_health = self.shipHealth
            else:
                self.shipHealth = self.frozen_health

        if not self.invincible:
            self.last_health = self.shipHealth
            self.frozen_health = self.shipHealth

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

        self.shield_system.reset_recharge_timer()
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

    def apply_upgrades(self) -> None:
        """
        Apply all upgrade chips to player-owned weapon stats.
        This should be called ONCE per level start or after loading a save.
        """

        # -------------------------
        # UPGRADE DEFINITIONS
        # -------------------------
        upgrade_effects = {
            "bullet_attack_up_plus_five": lambda: (
                setattr(self, "machine_gun_damage", self.machine_gun_damage + 5),
                setattr(self.machine_gun, "damage", self.machine_gun.damage + 5)
            ),

            "bullet_width_height_plus_one": lambda: (
                setattr(self, "machine_gun_width", self.machine_gun_width + 1),
                setattr(self.machine_gun, "width", self.machine_gun.width + 1),
                setattr(self, "machine_gun_height", self.machine_gun_height + 1),
                setattr(self.machine_gun, "height", self.machine_gun.height + 1),
            ),

            "machine_gun_rate_of_fire_up": lambda: (
                setattr(self, "machine_gun_rate_of_fire", max(0.01, self.machine_gun_rate_of_fire - 0.02)),
                setattr(self.machine_gun, "rate_of_fire", max(0.01, self.machine_gun.rate_of_fire - 0.02))
            ),

            "machine_gun_bullet_speed_up": lambda: (
                setattr(self, "machine_gun_bullet_speed", self.machine_gun_bullet_speed + 1.5),
                setattr(self.machine_gun, "bullet_speed", self.machine_gun.bullet_speed + 1.5)
            ),

            "machine_gun_extra_bullet": lambda: (
                setattr(self, "machine_gun_bullets_per_shot", self.machine_gun_bullets_per_shot + 1),
                setattr(self.machine_gun, "bullets_per_shot", self.machine_gun.bullets_per_shot + 1)
            ),
            # -------------------------
            # MISSILE UPGRADES
            # -------------------------
            "missile_attack_up_plus_ten": lambda: (
                setattr(self, "missile_damage", self.missile_damage + 10),
                setattr(self.missile, "damage", self.missile.damage + 10)
            ),

            "missile_bullet_speed_up": lambda: (
                setattr(self, "missile_bullet_speed", self.missile_bullet_speed + 1.0),
                setattr(self.missile, "bullet_speed", self.missile.bullet_speed + 1.0)
            ),

            "missile_rate_of_fire_up": lambda: (
                setattr(self, "missile_rate_of_fire", max(0.1, self.missile_rate_of_fire - 0.25)),
                setattr(self.missile, "rate_of_fire", max(0.1, self.missile.rate_of_fire - 0.25))
            ),

            "max_missiles_plus_two": lambda: (
                setattr(self, "missile_max", self.missile_max + 2),
                setattr(self, "missile_current", self.missile_current + 2),
                setattr(self.missile, "max_missiles", self.missile.max_missiles + 2),
                setattr(self.missile, "current_missiles", self.missile.current_missiles + 2),
            ),

            "missile_regen_faster": lambda: (
                setattr(self, "missile_regen_interval_seconds", max(0.5, self.missile_regen_interval_seconds - 0.5)),
                setattr(self.missile, "missile_regen_interval_seconds", max(0.5, self.missile.missile_regen_interval_seconds - 0.5))
            ),
        }

        # -------------------------
        # APPLY CHIPS
        # -------------------------
        for chip in self.upgrade_chips:
            effect = upgrade_effects.get(chip)
            if effect:
                effect()
