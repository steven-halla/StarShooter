import pygame
from pygame import Surface
import pytmx
import math

from Assets.Images.SpriteSheetExtractor import SpriteSheetExtractor
from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Controller.KeyBoardControls import KeyBoardControls
from Entity.Bosses.BossLevelFive import BossLevelFive
from Entity.Bosses.BossLevelFour import BossLevelFour
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelSix import BossLevelSix
from Entity.Bosses.BossLevelThree import BossLevelThree
from Entity.Bosses.BossLevelTwo import BossLevelTwo
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.SpinalRaptor import SpinalRaptor
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TransportWorm import TransportWorm
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.Monsters.WaspStinger import WaspStinger
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle
from SaveStates.SaveState import SaveState
from ScreenClasses.Camera import Camera
from ScreenClasses.TextBox import TextBox
from Weapons.Bullet import Bullet
# from game_state import GameState


class VerticalBattleScreen:
    def __init__(self, textbox):
        # self.isStart: bool = True
        self.playerDead: bool = False
        self.textbox = textbox
        self.tiled_map = pytmx.load_pygame("")
        self.tile_size: int = self.tiled_map.tileheight


        # enemy groups
        self.bileSpitterGroup: list[BileSpitter] = []
        self.kamikazeDroneGroup: list[KamikazeDrone] = []
        self.triSpitterGroup: list[TriSpitter] = []
        self.waspStingerGroup: list[WaspStinger] = []
        self.bladeSpinnerGroup: list[BladeSpinner] = []
        self.sporeFlowerGroup: list[SporeFlower] = []
        self.spineLauncherGroup: list[SpineLauncher] = []
        self.acidLauncherGroup: list[AcidLauncher] = []
        self.ravagerGroup: list[Ravager] = []
        self.fireLauncherGroup: list[FireLauncher] = []
        self.transportWormGroup: list[TransportWorm] = []
        self.spinalRaptorGroup: list[SpinalRaptor] = []
        self.slaverGroup: list[Slaver] = []



        self.bossLevelOneGroup: list[BossLevelOne] = []
        self.bossLevelTwoGroup: list[BossLevelTwo] = []
        self.bossLevelThreeGroup: list[BossLevelThree] = []
        self.bossLevelFourGroup: list[BossLevelFour] = []
        self.bossLevelFiveGroup: list[BossLevelFive] = []
        self.bossLevelSixGroup: list[BossLevelSix] = []

        #boss



        self.mover: MoveRectangle = MoveRectangle()
        self.controller: KeyBoardControls = KeyBoardControls()

        self.STARSHIP_HORIZONTAL_CENTER_DIVISOR: int = 2
        self.STARSHIP_BOTTOM_OFFSET: int = 100
        self.MIN_X: int = 0
        self.MIN_Y: int = 0
        self.map_scroll_speed_per_frame: float = 4334.33


        self.was_q_pressed_last_frame: bool = False

        self.plasma_blaster_bullets: list = []
        self.hyper_laser_bullets: list = []
        self.wind_slicer_bullets: list = []
        self.napalm_spread_bullets: list = []
        self.napalm_explosions: list = []
        self.energy_balls: list = []
        self.buster_cannon_bullets: list = []
        self.metal_shield_bullets: list = []
        self.wave_crash_bullets: list = []
        self.player_bullets: list = []
        self.player_missiles: list = []
        self.enemy_bullets: list = []     # LevelOne can append to this list

        self.WORLD_HEIGHT: int = GlobalConstants.GAMEPLAY_HEIGHT * 3
        self.SCROLL_SPEED_PER_SECOND: float = 55.0
        self.camera_y: float = 0.0
        self.SCROLL_SPEED_PER_FRAME: float = 55.0
        window_width: int = GlobalConstants.BASE_WINDOW_WIDTH
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT

        self.window_width = window_width
        self.window_height = window_height

        self.camera = Camera(
            window_width=window_width,
            window_height=window_height,
            world_height=self.WORLD_HEIGHT,
            scroll_speed_per_frame=self.SCROLL_SPEED_PER_FRAME,
            initial_zoom=2.5,   # DO NOT TOUCH CAMERA SETTINGS
        )
        self.save_state = SaveState()

        self.hud_sheet = pygame.image.load(
            "./Assets/Images/hud_icons.png"
        ).convert_alpha()

        # extract the 8th icon (index 7)
        # VerticalBattleScreen __init__

        # load HUD sprite sheet once
        self.hud_sheet = pygame.image.load(
            "./Assets/Images/hud_icons.png"
        ).convert_alpha()

        ICON_SIZE = 16
        UI_ICON_SIZE = 24  # smaller than 32 since you said it was too big

        # -------------------------------------------------
        # HUD ICONS (explicit order, no guessing)
        # -------------------------------------------------

        # heart (index 0)
        heart_rect = pygame.Rect(0 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.heart_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(heart_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # buster cannon (index 1)
        buster_rect = pygame.Rect(1 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.buster_cannon_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(buster_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # wind slicer (index 2)
        wind_rect = pygame.Rect(2 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.wind_slicer_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(wind_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # napalm spread (index 3)
        napalm_rect = pygame.Rect(3 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.napalm_spread_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(napalm_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # energy ball (index 4)
        energy_rect = pygame.Rect(4 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.energy_ball_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(energy_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # plasma blaster (index 5)
        plasma_rect = pygame.Rect(5 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.plasma_blaster_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(plasma_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # metal shield (index 6)
        metal_rect = pygame.Rect(6 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.metal_shield_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(metal_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # MISSILE (index 7)
        self.missile_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(pygame.Rect(7 * 16, 0, 16, 16)),
            (32, 32)
        )

        # hyper laser (index 8) — missile skipped on purpose
        hyper_rect = pygame.Rect(8 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.hyper_laser_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(hyper_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # wave crash (index 9)
        wave_rect = pygame.Rect(9 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.wave_crash_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(wave_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )

        # engine (index 10) — optional / future use
        engine_rect = pygame.Rect(10 * ICON_SIZE, 0, ICON_SIZE, ICON_SIZE)
        self.engine_icon = pygame.transform.scale(
            self.hud_sheet.subsurface(engine_rect),
            (UI_ICON_SIZE, UI_ICON_SIZE)
        )
        # VerticalBattleScreen __init__

    # All weapon icons are loaded in update() method
        self.SUB_WEAPON_ICON_INDEX = {
            "Buster Cannon": 1,
            "Wind Slicer": 2,
            "Napalm Spread": 3,
            "Energy Ball": 4,
            "Plasma Blaster": 5,
            "Metal Shield": 6,
            "Hyper Laser": 8,
            "Wave Crash": 9,
        }

        self.sub_weapon_icons = {}

        self.textbox = TextBox(
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.BASE_WINDOW_HEIGHT
        )
        self.textbox.show("")
    def start(self, state):
        pass

    def set_player(self, player):
        self.starship = player


    def clamp_starship_to_screen(self):
        zoom = self.camera.zoom
        ship_w = self.starship.width
        ship_h = self.starship.height

        # --- HORIZONTAL (NO CAMERA X), EASY ---
        max_x = self.window_width / zoom - ship_w
        if self.starship.x < 0:
            self.starship.x = 0
        elif self.starship.x > max_x:
            self.starship.x = max_x

        # --- VERTICAL (CAMERA Y ACTIVE) ---
        cam_y = self.camera.y
        win_h = self.window_height

        min_y = cam_y
        max_y = cam_y + (win_h / zoom) - ship_h

        if self.starship.y < min_y:
            self.starship.y = min_y
        elif self.starship.y > max_y:
            self.starship.y = max_y

    def move_map_y_axis(self):
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        # move camera UP in world space (so map scrolls down)
        # self.camera_y -= self.map_scroll_speed_per_frame

        # clamp so we never scroll past top or bottom of the map
        max_camera_y = self.WORLD_HEIGHT - window_height
        if max_camera_y < 0:
            max_camera_y = 0

        if self.camera_y < 0:
            self.camera_y = 0
        elif self.camera_y > max_camera_y:
            self.camera_y = max_camera_y

        # keep Camera object in sync
        self.camera.y = float(self.camera_y)

    def update(self, state: 'GameState'):
        # print("PLAYER UPDATE Y:", self.starship.y)
        # print("STARSHIP INSTANCE:", id(self.starship))
        # now handle map scroll ONLY in LevelOne
        # FIRST: update input

        self.controller.update()

        # THEN: react to input
        if self.textbox.is_visible():
            if self.controller.qJustPressed:
                self.textbox.advance()

        if self.controller.qJustPressed:
            print("Q ADVANCE FIRED")


        for weapon_name, icon_index in self.SUB_WEAPON_ICON_INDEX.items():
            rect = pygame.Rect(icon_index * 16, 0, 16, 16)
            icon = self.hud_sheet.subsurface(rect)
            self.sub_weapon_icons[weapon_name] = pygame.transform.scale(icon, (24, 24))
        # --------------------------------
        # PLAYER DEATH → LOAD SAVE
        # --------------------------------

        # if self.starship.shipHealth <= 0:
        #     from Levels.LevelOne import LevelOne
        #
        #     # reload save
        #     if self.save_state.load_from_file(""
        #                                       "player_save.json"):
        #         new_level = LevelOne(state.textbox)
        #         state.currentScreen = new_level
        #         new_level.start(state)
        #
        #         # restore player AFTER start() sets spawn point
        #         self.save_state.restore_player(state.starship)
        #
        #     return
        self.move_map_y_axis()




        if not hasattr(self, "start_has_run"):
            self.start(state)  # This calls LevelOne.start()
            self.start_has_run = True
        # self.starship.update()
        if self.starship.shipHealth <= 0:
            self.playerDead = True
        #
        # if self.isStart:
        #     self.start(state)
        #     self.isStart = False

        self.controller.update()

        # Player movement
        if not self.playerDead:
            if self.controller.left_button:
                self.mover.player_move_left(self.starship)
            if self.controller.right_button:
                self.mover.player_move_right(self.starship)
            if self.controller.up_button:
                self.mover.player_move_up(self.starship)
            if self.controller.down_button:
                self.mover.player_move_down(self.starship)
        self.starship.update()

        # self.was_q_pressed_last_frame = self.controller.q_button

        self.clamp_starship_to_screen()
        # if not self.playerDead:
        #     self.starship.update()



        # -------------------------
        # PLAYER SHOOTING ONLY
        # # -------------------------

        if self.controller.fire_missiles and not self.playerDead:
            missile = self.starship.fire_missile()
            if missile is not None:
                self.player_missiles.append(missile)

        if self.controller.main_weapon_button and not self.playerDead:
            new_bullets = self.starship.fire_twin_linked_machinegun()
            self.player_bullets.extend(new_bullets)

        # if self.controller.main_weapon_button and not self.playerDead:
        #     new_bullets = self.starship.fire_twin_linked_machinegun()
        #     self.player_bullets.extend(new_bullets)

        # -------------------------
        # PLAYER MAGIC FIRING
        # -------------------------
        # If Buster Cannon is in slot 0:
        # Slot 0 — Buster Cannon
        if state.starship.equipped_magic[0] == "Buster Cannon" and not self.playerDead:

            # Start charging ONLY when button is first pressed
            if self.controller.magic_1_button and not state.starship.buster_cannon.is_charging:
                state.starship.buster_cannon.start_charge()

            # Continue charging while held
            if self.controller.magic_1_button:
                state.starship.buster_cannon.update()

            # Release → fire once
            if self.controller.magic_1_released:
                state.starship.buster_cannon.stop_charge()
                shots = state.starship.fire_buster_cannon()
                self.buster_cannon_bullets.extend(shots)

            # HELD → do nothing, let update handle charged
        if state.starship.equipped_magic[1] == "Buster Cannon" and not self.playerDead:

            # Start charging ONLY when button is first pressed
            if self.controller.magic_2_button and not state.starship.buster_cannon.is_charging:
                state.starship.buster_cannon.start_charge()

            # Continue charging while held
            if self.controller.magic_2_button:
                state.starship.buster_cannon.update()

            # Release → fire once
            if self.controller.magic_2_released:
                state.starship.buster_cannon.stop_charge()
                shots = state.starship.fire_buster_cannon()
                self.buster_cannon_bullets.extend(shots)

        # -------------------------
        # PLASMA BLASTER MAGIC
        # -------------------------
        if state.starship.equipped_magic[0] == "Plasma Blaster" and not self.playerDead:

            # HOLD → spawn ONE beam
            if self.controller.magic_1_button:
                if not self.plasma_blaster_bullets:  # 🔒 guard: only ONE
                    plasma = state.starship.fire_plasma_blaster()
                    if plasma is not None:
                        self.plasma_blaster_bullets.append(plasma)

        # -------------------------
        # ENERGY BALL MAGIC
        # -------------------------
        if state.starship.equipped_magic[0] == "Energy Ball" and not self.playerDead:

            # UPDATE EXISTING ENERGY BALLS (RIGHT HERE)
            for ball in list(self.energy_balls):
                ball.update()

                screen_y = ball.y - self.camera.y
                if screen_y + ball.height < 0:
                    self.energy_balls.remove(ball)

            # SPAWN NEW ENERGY BALL
            if self.controller.magic_1_button:

                dx = 0
                dy = 0
                speed = 6

                if self.controller.left_button:
                    dx -= 1
                if self.controller.right_button:
                    dx += 1
                if self.controller.up_button:
                    dy -= 1
                if self.controller.down_button:
                    dy += 1

                # Default direction (up)
                if dx == 0 and dy == 0:
                    dy = -1

                # Normalize so diagonals are not faster
                length = math.hypot(dx, dy)
                dx = (dx / length) * speed
                dy = (dy / length) * speed

                energy_ball = state.starship.fire_energy_ball(dx, dy)
                if energy_ball is not None:
                    self.energy_balls.append(energy_ball)

        # -------------------------

        # WAVE metal shield magic
        # -------------------------

        # And the same pattern for slot 1 / S
        if state.starship.equipped_magic[0] == "Metal Shield" and not self.playerDead:
            if self.controller.magic_1_button:
                # Only allow one active shield
                if not self.metal_shield_bullets:
                    shield = state.starship.fire_metal_shield()
                    if shield is not None:
                        self.metal_shield_bullets.append(shield)

        # -------------------------
        # NAPALM SPREAD MAGIC
        # -------------------------
        if state.starship.equipped_magic[0] == "Napalm Spread" and not self.playerDead:
            if self.controller.magic_1_button:
                napalm = state.starship.fire_napalm_spread()
                if napalm is not None:
                    self.napalm_spread_bullets.append(napalm)

        # -------------------------

        # Hyper laser
        # -------------------------
        if state.starship.equipped_magic[0] == "Hyper Laser" and not self.playerDead:
            if self.controller.magic_1_button:
                if not self.hyper_laser_bullets:  # ← guard
                    laser = state.starship.fire_hyper_laser()
                    if laser is not None:
                        self.hyper_laser_bullets.append(laser)

        # -------------------------
        # HYPER LASER RELEASE
        # -------------------------
        if not self.controller.magic_1_button:
            if self.hyper_laser_bullets:
                self.hyper_laser_bullets.clear()
        # -------------------------

        # WAVE CRASH MAGIC
        # -------------------------
        if state.starship.equipped_magic[0] == "Wave Crash" and not self.playerDead:
            if self.controller.magic_1_button:
                waves = state.starship.fire_wave_crash()
                self.wave_crash_bullets.extend(waves)

        if state.starship.equipped_magic[1] == "Wave Crash" and not self.playerDead:
            if self.controller.magic_2_button:
                waves = state.starship.fire_wave_crash()
                self.wave_crash_bullets.extend(waves)

        # -------------------------
        # WIND SLICER MAGIC
        # -------------------------
        if state.starship.equipped_magic[0] == "Wind Slicer" and not self.playerDead:
            if self.controller.magic_1_button:
                slicers = state.starship.fire_wind_slicer()
                self.wind_slicer_bullets.extend(slicers)


        self.bullet_helper()


        # -------------------------
        # PLASMA BLASTER UPDATE
        # -------------------------
        for plasma in list(self.plasma_blaster_bullets):
            plasma.update()

            # Convert to screen space
            screen_y = plasma.y - self.camera.y

            # Delete when off screen
            if screen_y + plasma.height < 0 or not plasma.is_active:
                self.plasma_blaster_bullets.remove(plasma)

        # -------------------------
        # WIND SLICER UPDATE
        # -------------------------
        for slicer in list(self.wind_slicer_bullets):
            slicer.update()

            # Convert to screen space (same pattern)
            screen_y = slicer.y - self.camera.y

            # Remove if off screen
            if screen_y + slicer.height < 0:
                self.wind_slicer_bullets.remove(slicer)

        # -------------------------
        # NAPALM SPREAD UPDATE
        # -------------------------
        # NAPALM SPREAD UPDATE
        # -------------------------

        for napalm in list(self.napalm_spread_bullets):
            napalm.update()

            # Remove only AFTER explosion finishes
            if not napalm.is_active:
                self.napalm_spread_bullets.remove(napalm)


        # -------------------------
        # PLAYER MISSILES ONLY
        # -------------------------
        for missile in list(self.player_missiles):

            # Make sure missile has a target BEFORE updating
            if getattr(missile, "target_enemy", None) is None:
                if hasattr(self, "get_nearest_enemy"):
                    missile.target_enemy = self.get_nearest_enemy(missile)

            missile.update()
            # Convert to screen space for culling
            screen_y = missile.y - self.camera.y

            # If missile goes above screen → delete
            if screen_y + missile.height < 0:
                self.player_missiles.remove(missile)

        # -------------------------
        # PLAYER Metal Shield
        # -------------------------

        for metal in list(self.metal_shield_bullets):
            metal.update_orbit(
                self.starship.x + self.starship.width / 2,
                self.starship.y + self.starship.height / 2
            )

            # Optional cleanup if shield has already blocked a hit
            if not metal.is_active:
                self.metal_shield_bullets.remove(metal)
            # Convert to screen space
            screen_y = metal.y - self.camera.y

            # If bullet is above the visible screen area → delete
            # if screen_y + metal.height < 0:
            #     # print(f"[DELETE] Bullet removed at world_y={bullet.y}, screen_y={screen_y}")
            #     self.metal_shield_bullets.remove(metal)



        for laser in list(self.hyper_laser_bullets):
            laser.update()

            # Convert to screen space
            screen_y = laser.y - self.camera.y

            # If bullet is above the visible screen area → delete
            if screen_y + laser.height < 0:
                # print(f"[DELETE] Bullet removed at world_y={bullet.y}, screen_y={screen_y}")
                self.hyper_laser_bullets.remove(laser)


        for bullet in list(self.player_bullets):
            bullet.update()

            # Convert to screen space
            screen_y = bullet.y - self.camera.y

            # If bullet is above the visible screen area → delete
            if screen_y + bullet.height < 0:
                # print(f"[DELETE] Bullet removed at world_y={bullet.y}, screen_y={screen_y}")
                self.player_bullets.remove(bullet)

        # -------------------------
        # WAVE CRASH BULLET CLEANUP
        # -------------------------
        for wave in list(self.wave_crash_bullets):
            wave.update()

            # Horizontal shots → check X instead of Y
            screen_x = wave.x - self.camera.x if hasattr(self.camera, "x") else wave.x

            # If wave goes off left or right of screen → delete
            if screen_x + wave.width < 0 or screen_x > (self.window_width / self.camera.zoom):
                self.wave_crash_bullets.remove(wave)

        # -------------------------
        # BUSTER CANNON BULLET CLEANUP
        # -------------------------
        for bc in list(self.buster_cannon_bullets):
            bc.update()

            # Convert to screen space (same method as regular bullets)
            screen_y = bc.y - self.camera.y

            # If the buster cannon shot goes above the visible screen → delete
            if screen_y + bc.height < 0:
                self.buster_cannon_bullets.remove(bc)



        # -------------------------
        # ENEMY BULLETS ONLY
        # -------------------------
        screen_top = self.camera.y
        screen_bottom = self.camera.y + (self.window_height / self.camera.zoom)
        for bullet in list(self.enemy_bullets):
            bullet.update()

            # WORLD-SPACE BOUNDS (same logic as player bullets)
            world_top_delete = self.camera.y - 200
            world_bottom_delete = self.camera.y + self.window_height + 200

            if bullet.y < world_top_delete or bullet.y > world_bottom_delete:
                # print(f"[DELETE ENEMY] y={bullet.y}, cam_y={self.camera.y}")
                self.enemy_bullets.remove(bullet)
                continue

            # Collision check
            if bullet.collide_with_rect(self.starship.hitbox):
                self.starship.shipHealth -= bullet.damage
                bullet.is_active = False
                self.enemy_bullets.remove(bullet)

        hazard_layer = self.tiled_map.get_layer_by_name("hazard")
        player_rect = self.starship.hitbox  # already in WORLD coordinates


        for col, row, tile in hazard_layer.tiles():

            tile_rect = pygame.Rect(
                col * self.tile_size,
                row * self.tile_size,
                self.tile_size,
                self.tile_size
            )

            if player_rect.colliderect(tile_rect):
                self.starship.shipHealth -= 1
                print("⚠️ Player took hazard damage! Health =", self.starship.shipHealth)
                break

        # -------------------------
        # ENEMY BODY COLLISION DAMAGE (GLOBAL RULE)
        # -------------------------
        player_rect = self.starship.hitbox

        if not self.starship.invincible:
            # TODO this MUST be reading from current_level.enemies or something, not
            # checking every f'n enemy every single time
            enemies = (
                    list(self.bileSpitterGroup) +
                    list(self.spinalRaptorGroup) +
                    list(self.triSpitterGroup) +
                    list(self.slaverGroup) +
                    list(self.bladeSpinnerGroup) +
                    list(self.fireLauncherGroup) +
                    list(self.kamikazeDroneGroup) +
                    list(self.transportWormGroup) +

                    list(self.bossLevelThreeGroup) +
                    list(self.bossLevelTwoGroup) +
                    list(self.bossLevelOneGroup) +
                    list(self.bossLevelFourGroup) +
                    list(self.bossLevelFiveGroup) +
                    list(self.bossLevelSixGroup)
            )

            for enemy in enemies:
                enemy_rect = pygame.Rect(
                    enemy.x,
                    enemy.y,
                    enemy.width,
                    enemy.height
                )

                if player_rect.colliderect(enemy_rect):
                    self.starship.shipHealth -= 10
                    self.starship.on_hit()
                    break  # ⛔ only one hit per frame

        # -------------------------
        # ENEMY COLLISION WITH UI PANEL (ERASE ENEMIES)
        # -------------------------
        ui_panel_rect = pygame.Rect(
            0,
            GlobalConstants.GAMEPLAY_HEIGHT,
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.UI_PANEL_HEIGHT
        )

        enemies = (
                list(self.bileSpitterGroup) +
                list(self.triSpitterGroup) +
                list(self.slaverGroup) +
                list(self.bladeSpinnerGroup) +
                list(self.fireLauncherGroup) +
                list(self.kamikazeDroneGroup) +
                list(self.transportWormGroup) +
                list(self.waspStingerGroup) +
                list(self.sporeFlowerGroup) +
                list(self.spineLauncherGroup) +
                list(self.acidLauncherGroup) +
                list(self.ravagerGroup) +
                list(self.spinalRaptorGroup) +

                list(self.bossLevelThreeGroup) +
                list(self.bossLevelTwoGroup) +
                list(self.bossLevelOneGroup) +
                list(self.bossLevelFourGroup) +
                list(self.bossLevelFiveGroup) +
                list(self.bossLevelSixGroup)
        )

        for enemy in list(enemies):
            # Convert enemy position to screen coordinates
            enemy_screen_y = enemy.y - self.camera.y

            # Create enemy rect in screen coordinates
            enemy_rect = pygame.Rect(
                enemy.x,
                enemy_screen_y,
                enemy.width,
                enemy.height
            )

            # Check if enemy intersects with UI panel
            if enemy_rect.colliderect(ui_panel_rect):
                # Set enemy health to zero and is_active to False to ensure it's removed and not drawn
                enemy.enemyHealth = 0
                enemy.is_active = False
                self.remove_enemy_if_dead(enemy)

        screen_bottom = self.camera.y + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
        UI_KILL_PADDING = 12  # pixels ABOVE the UI panel (tweak this)

        screen_bottom = (
                self.camera.y
                + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
                - UI_KILL_PADDING
        )
        all_enemies = (
                list(self.kamikazeDroneGroup)
                + list(self.bileSpitterGroup)
                + list(self.triSpitterGroup)
                + list(self.waspStingerGroup)
                + list(self.bladeSpinnerGroup)
                + list(self.sporeFlowerGroup)
                + list(self.spineLauncherGroup)
                + list(self.acidLauncherGroup)
                + list(self.ravagerGroup)
                + list(self.fireLauncherGroup)
                + list(self.slaverGroup)
                + list(self.transportWormGroup)
                + list(self.spinalRaptorGroup)

                + list(self.bossLevelOneGroup)
                + list(self.bossLevelTwoGroup)
                + list(self.bossLevelThreeGroup)
                + list(self.bossLevelFourGroup)
                + list(self.bossLevelFiveGroup)
                + list(self.bossLevelSixGroup)
        )

        for enemy in list(all_enemies):
            if enemy.y > screen_bottom:
                # Set is_active to False to ensure it's not drawn
                enemy.is_active = False

                enemy_groups = (
                    self.kamikazeDroneGroup,
                    self.bileSpitterGroup,
                    self.triSpitterGroup,
                    self.waspStingerGroup,
                    self.bladeSpinnerGroup,
                    self.sporeFlowerGroup,
                    self.spineLauncherGroup,
                    self.acidLauncherGroup,
                    self.ravagerGroup,
                    self.fireLauncherGroup,
                    self.slaverGroup,
                    self.transportWormGroup,
                    self.spinalRaptorGroup,

                    self.bossLevelOneGroup,
                    self.bossLevelTwoGroup,
                    self.bossLevelThreeGroup,
                    self.bossLevelFourGroup,
                    self.bossLevelFiveGroup,
                    self.bossLevelSixGroup
                )

                for group in enemy_groups:
                    if enemy in group:
                        group.remove(enemy)
                        break

    def draw(self, state) -> None:

        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        scene_surface = pygame.Surface((window_width, window_height))
        # scene_surface.fill((0, 0, 0))  # OR sky color
        scene_surface.fill((20, 20, 40))  # sky / space color
        zoom = self.camera.zoom
        self.starship.shipHealth


        # Gameplay render surface (NO UI PANEL INCLUDED)

        # Draw map + gameplay objects into gameplay surface

        self.draw_tiled_layers(scene_surface)
        # if hasattr(self, "draw_level_collision"):
        # self.draw_collision_tiles(scene_surface)
        # self.draw_collision_tiles(scene_surface)
        # after self.draw_tiled_layers(scene_surface)
        if hasattr(self, "draw_level_collision"):
            self.draw_collision_tiles(scene_surface)

        # Scale gameplay scene
        scaled_scene = pygame.transform.scale(
            scene_surface,
            (int(window_width * zoom), int(window_height * zoom))
        )

        # Clear full display (includes UI area)
        state.DISPLAY.fill(GlobalConstants.BLACK)

        # Draw gameplay area at top
        state.DISPLAY.blit(scaled_scene, (0, 0))

        # 🔽 UI CONTENT (TEXT, HP, ETC)
        # Removed call to draw_player_hp_bar to ensure only one heart image is displayed
        # self.draw_ui_panel(state.DISPLAY)

        # -------------------------
        # DRAW PLASMA BLASTER
        # -------------------------
        for plasma in self.plasma_blaster_bullets:
            px = self.camera.world_to_screen_x(plasma.x)
            py = self.camera.world_to_screen_y(plasma.y)
            pw = int(plasma.width * zoom)
            ph = int(plasma.height * zoom)

            # Draw plasma beam (thin vertical light)
            rect = pygame.Rect(px, py, pw, ph)
            pygame.draw.rect(state.DISPLAY, (0, 255, 255), rect)

            # Debug hitbox outline
            pygame.draw.rect(
                state.DISPLAY,
                (255, 255, 255),
                (px, py, pw, ph),
                1
            )


        # -------------------------
        # DRAW WIND SLICER BULLETS
        # -------------------------
        for slicer in self.wind_slicer_bullets:
            sx = self.camera.world_to_screen_x(slicer.x)
            sy = self.camera.world_to_screen_y(slicer.y)
            sw = int(slicer.width * zoom)
            sh = int(slicer.height * zoom)

            rect = pygame.Rect(sx, sy, sw, sh)

            # main projectile
            pygame.draw.rect(state.DISPLAY, (180, 220, 255), rect)

            # debug hitbox outline
            pygame.draw.rect(
                state.DISPLAY,
                (0, 150, 255),
                (sx, sy, sw, sh),
                2
            )

        # -------------------------
        # DRAW ENERGY BALLS
        # -------------------------
        for ball in self.energy_balls:
            bx = self.camera.world_to_screen_x(ball.x)
            by = self.camera.world_to_screen_y(ball.y)
            bw = int(ball.width * zoom)
            bh = int(ball.height * zoom)

            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, (0, 200, 255), rect)

            # debug hitbox outline
            pygame.draw.rect(
                state.DISPLAY,
                (255, 255, 255),
                (bx, by, bw, bh),
                1
            )

        for laser in self.hyper_laser_bullets:
            mx = self.camera.world_to_screen_x(laser.x)
            my = self.camera.world_to_screen_y(laser.y)
            mw = int(laser.width * zoom)
            mh = int(laser.height * zoom)

            rect = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

            # debug hitbox outline
            pygame.draw.rect(
                state.DISPLAY,
                (77, 113, 111),
                (mx, my, mw, mh),
                1
            )

        # -------------------------
        # DRAW PLAYER Metal Shield
        # -------------------------]
        for metal in self.metal_shield_bullets:
            mx = self.camera.world_to_screen_x(metal.x)
            my = self.camera.world_to_screen_y(metal.y)
            mw = int(metal.width * zoom)
            mh = int(metal.height * zoom)

            rect = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

            # debug hitbox outline
            pygame.draw.rect(
                state.DISPLAY,
                (55, 55, 111),
                (mx, my, mw, mh),
                1
            )

        # -------------------------
        # DRAW PLAYER MISSILES
        # -------------------------]
        for missile in self.player_missiles:
            mx = self.camera.world_to_screen_x(missile.x)
            my = self.camera.world_to_screen_y(missile.y)
            mw = int(missile.width * zoom)
            mh = int(missile.height * zoom)

            rect = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

            # debug hitbox outline
            pygame.draw.rect(
                state.DISPLAY,
                (255, 255, 0),
                (mx, my, mw, mh),
                1
            )


        for bullet in self.player_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)
            # bullet hitbox debug
            hb_x = bx
            hb_y = by
            hb_w = bw
            hb_h = bh
            pygame.draw.rect(state.DISPLAY, (255, 255, 0), (hb_x, hb_y, hb_w, hb_h), 1)

        for bullet in self.enemy_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)

            # Draw bullet
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, bullet.color, rect)

            # 🔶 Draw hitbox (debug)
            pygame.draw.rect(
                state.DISPLAY,
                (255, 255, 0),  # yellow hitbox
                (bx, by, bw, bh),
                3  # thin line
            )

        # -------------------------
        # DRAW BUSTER CANNON BULLETS
        # -------------------------
        for bc in self.buster_cannon_bullets:
            print("jf;dalsj;lfjdasl;fj;lsajfljsal;fj;dsljfl;jaslfdlsa")
            bx = self.camera.world_to_screen_x(bc.x)
            by = self.camera.world_to_screen_y(bc.y)
            bw = int(bc.width * zoom)
            bh = int(bc.height * zoom)

            # Draw buster cannon projectile
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, (1, 1, 1), rect)

            pygame.draw.rect(
                state.DISPLAY,
                (255, 255, 0),
                (bx - 2, by - 2, bw + 4, bh + 4),
                5
            )

        # -------------------------
        # DRAW NAPALM SPREAD (PROJECTILE PHASE)
        # -------------------------
        for napalm in self.napalm_spread_bullets:
            nx = self.camera.world_to_screen_x(napalm.x)
            ny = self.camera.world_to_screen_y(napalm.y)
            nw = int(napalm.width * zoom)
            nh = int(napalm.height * zoom)

            # Draw napalm grenade
            rect = pygame.Rect(nx, ny, nw, nh)
            pygame.draw.rect(state.DISPLAY, (255, 100, 0), rect)

            # Debug outline
            pygame.draw.rect(
                state.DISPLAY,
                (255, 200, 0),
                (nx - 2, ny - 2, nw + 4, nh + 4),
                3
            )

        # -------------------------
        # DRAW NAPALM EXPLOSION AOE
        # -------------------------
        for napalm in self.napalm_spread_bullets:
            if napalm.has_exploded:
                # print("dfsaj")

                # Center of explosion in screen space
                cx = self.camera.world_to_screen_x(napalm.x)
                cy = self.camera.world_to_screen_y(napalm.y)

                aoe_w = int(napalm.area_of_effect_x * zoom)
                aoe_h = int(napalm.area_of_effect_y * zoom)

                aoe_rect = pygame.Rect(
                    cx - aoe_w // 2,
                    cy - aoe_h // 2,
                    aoe_w,
                    aoe_h
                )

                # Draw explosion area (orange/red)
                pygame.draw.rect(state.DISPLAY, (255, 80, 0), aoe_rect, 4)

        # -------------------------
        for wave in self.wave_crash_bullets:
            print("jf;dalsj;lfjdasl;fj;lsajfljsal;fj;dsljfl;jaslfdlsa")
            bx = self.camera.world_to_screen_x(wave.x)
            by = self.camera.world_to_screen_y(wave.y)
            bw = int(wave.width * zoom)
            bh = int(wave.height * zoom)

            # Draw buster cannon projectile
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(state.DISPLAY, (1, 1, 1), rect)

            pygame.draw.rect(
                state.DISPLAY,
                (0, 255, 0),
                (bx , by ,  55,  55),
                10
            )

        # 🔽 UI PANEL (BOTTOM BAR) - Draw last to ensure it covers anything that comes into contact with it
        self.draw_ui_panel(state.DISPLAY)



    def bullet_helper(self):
        all_enemies = (
                list(self.kamikazeDroneGroup) +
                list(self.bileSpitterGroup) +
                list(self.triSpitterGroup) +
                list(self.slaverGroup) +
                list(self.waspStingerGroup) +
                list(self.bladeSpinnerGroup) +
                list(self.sporeFlowerGroup) +
                list(self.spineLauncherGroup) +
                list(self.acidLauncherGroup) +
                list(self.ravagerGroup) +
                list(self.transportWormGroup) +
                list(self.fireLauncherGroup) +
                list(self.spinalRaptorGroup) +

                list(self.bossLevelOneGroup) +
                list(self.bossLevelTwoGroup) +
                list(self.bossLevelThreeGroup) +
                list(self.bossLevelFourGroup) +
                list(self.bossLevelFiveGroup) +
                list(self.bossLevelSixGroup)
        )

        # -------------------------
        # PLASMA BLASTER
        # -------------------------
        for plasma in list(self.plasma_blaster_bullets):
            plasma_rect = pygame.Rect(plasma.x, plasma.y, plasma.width, plasma.height)

            for enemy in all_enemies:
                if plasma_rect.colliderect(enemy.hitbox):
                    enemy.enemyHealth -= plasma.damage
                    self.plasma_blaster_bullets.remove(plasma)

                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break

        # -------------------------
        # PLAYER BULLETS
        # -------------------------
        for bullet in list(self.player_bullets):
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)

            for enemy in all_enemies:
                if bullet_rect.colliderect(enemy.hitbox):
                    enemy.enemyHealth -= self.starship.bulletDamage
                    self.player_bullets.remove(bullet)

                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break

        # -------------------------
        # WIND SLICER
        # -------------------------
        for slicer in list(self.wind_slicer_bullets):

            for enemy in all_enemies:
                if slicer.hitbox.colliderect(enemy.hitbox):
                    enemy.enemyHealth -= slicer.damage

                    # remove slicer unless it is piercing
                    self.wind_slicer_bullets.remove(slicer)

                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break

        # -------------------------
        # MISSILES
        # -------------------------
        for missile in list(self.player_missiles):
            missile_rect = pygame.Rect(missile.x, missile.y, missile.width, missile.height)

            for enemy in all_enemies:
                if missile_rect.colliderect(enemy.hitbox):
                    enemy.enemyHealth -= self.starship.missileDamage
                    self.player_missiles.remove(missile)

                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break

        # -------------------------
        # BUSTER CANNON
        # -------------------------
        for bc in list(self.buster_cannon_bullets):
            bc_rect = pygame.Rect(bc.x, bc.y, bc.width, bc.height)

            for enemy in all_enemies:
                if bc_rect.colliderect(enemy.hitbox):
                    enemy.enemyHealth -= bc.damage
                    self.buster_cannon_bullets.remove(bc)

                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break

        # -------------------------
        # WAVE CRASH
        # -------------------------
        for wave in list(self.wave_crash_bullets):
            wave_rect = pygame.Rect(wave.x, wave.y, wave.width, wave.height)

            for enemy in all_enemies:
                if wave_rect.colliderect(enemy.hitbox):
                    enemy.enemyHealth -= wave.damage
                    self.wave_crash_bullets.remove(wave)

                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break

    def remove_enemy_if_dead(self, enemy) -> None:
        if enemy.enemyHealth > 0:
            return

        enemy.is_active = False

        enemy_groups = (
            self.kamikazeDroneGroup,
            self.bileSpitterGroup,
            self.triSpitterGroup,
            self.waspStingerGroup,
            self.bladeSpinnerGroup,
            self.sporeFlowerGroup,
            self.spineLauncherGroup,
            self.acidLauncherGroup,
            self.ravagerGroup,
            self.fireLauncherGroup,
            self.slaverGroup,
            self.transportWormGroup,
            self.bossLevelFiveGroup,

            self.bossLevelOneGroup,
            self.bossLevelTwoGroup,
            self.bossLevelThreeGroup,
            self.bossLevelFourGroup,
            self.bossLevelFiveGroup,
            self.bossLevelSixGroup
        )

        for group in enemy_groups:
            if enemy in group:
                group.remove(enemy)
                break
    # one place, no elif chain, no duplication



    def get_enemy_screen_rect(self, enemy) -> pygame.Rect:
        return pygame.Rect(
            self.camera.world_to_screen_x(enemy.x),
            self.camera.world_to_screen_y(enemy.y),
            int(enemy.width * self.camera.zoom),
            int(enemy.height * self.camera.zoom)
        )

    def weapon_rectangle(self, obj) -> pygame.Rect:
        return pygame.Rect(
            self.camera.world_to_screen_x(obj.x),
            self.camera.world_to_screen_y(obj.y),
            int(obj.width * self.camera.zoom),
            int(obj.height * self.camera.zoom)
        )

    def draw_player_hp_bar(self, surface):
        """
        Draws player HP text at the top of the screen.
        Format: HP: current/100
        """
        font = pygame.font.Font(None, 24)

        current_hp = max(0, int(self.starship.shipHealth))
        max_hp = 100

        hp_text = f"HP: {current_hp}/{max_hp}"
        text_surface = font.render(hp_text, True, (255, 255, 255))

        # Top-left padding
        surface.blit(text_surface, (10, 10))

    def draw_ui_panel(self, surface: pygame.Surface) -> None:
        font = pygame.font.Font(None, 24)

        missile_text = f"{self.starship.current_missiles}/{self.starship.max_missiles}"
        missile_text_surface = font.render(missile_text, True, (255, 255, 255))
        # -----------------------------
        # PANEL RECT
        # -----------------------------
        panel_rect = pygame.Rect(
            0,
            GlobalConstants.GAMEPLAY_HEIGHT,
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.UI_PANEL_HEIGHT
        )

        pygame.draw.rect(surface, (20, 20, 20), panel_rect)

        pygame.draw.line(
            surface,
            (255, 255, 255),
            (0, GlobalConstants.GAMEPLAY_HEIGHT),
            (GlobalConstants.BASE_WINDOW_WIDTH, GlobalConstants.GAMEPLAY_HEIGHT),
            2
        )

        # -----------------------------
        # Get current HP values
        # -----------------------------
        current_hp = max(0, int(self.starship.shipHealth))
        max_hp = max(1, int(self.starship.shipHealthMax))

        # -----------------------------
        # HP BAR
        # -----------------------------
        BAR_WIDTH = 100
        BAR_HEIGHT = 20

        hp_percent = current_hp / max_hp
        filled_width = max(0, min(BAR_WIDTH, int(BAR_WIDTH * hp_percent)))

        # Position the bar directly after the heart image
        bar_x = 50  # Starting position for the bar
        bar_y = GlobalConstants.GAMEPLAY_HEIGHT + 10

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT),
            1
        )

        if filled_width > 0:
            pygame.draw.rect(
                surface,
                (0, 200, 0),
                (bar_x + 1, bar_y + 1, filled_width - 2, BAR_HEIGHT - 2)
            )

        # -----------------------------
        # HUD ICON (LOAD ONCE)
        # -----------------------------

        # -----------------------------
        # HEART ICON (PRELOADED, NO IMAGE.LOAD HERE)
        # -----------------------------

        # draw heart icon (already sliced + scaled in __init__)
        heart_x = 10
        heart_y = GlobalConstants.GAMEPLAY_HEIGHT + 6
        surface.blit(self.heart_icon, (heart_x, heart_y))

        # -----------------------------
        # HP BAR (POSITIONED AFTER HEART)
        # -----------------------------

        bar_x = heart_x + self.heart_icon.get_width() + 8
        bar_y = GlobalConstants.GAMEPLAY_HEIGHT + 10

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT),
            1
        )

        if filled_width > 0:
            pygame.draw.rect(
                surface,
                (0, 200, 0),
                (bar_x + 1, bar_y + 1, filled_width - 2, BAR_HEIGHT - 2)
            )

        # -----------------------------
        # MISSILE ICON (PRELOADED)
        # -----------------------------

        icon_x = bar_x + BAR_WIDTH + 10
        icon_y = bar_y - 4
        surface.blit(self.missile_icon, (icon_x, icon_y))

        # -----------------------------
        # MISSILE COUNT TEXT
        # -----------------------------

        font = pygame.font.Font(None, 24)
        missile_text = f"{self.starship.current_missiles}/{self.starship.max_missiles}"
        missile_surface = font.render(missile_text, True, (255, 255, 255))

        missile_text_x = icon_x + 32 + 5
        missile_text_y = icon_y + 8

        surface.blit(missile_text_surface, (missile_text_x, missile_text_y))
        # -----------------------------
        # EQUIPPED WEAPON ICON POSITION
        # -----------------------------

        buster_icon_x = missile_text_x + missile_surface.get_width() + 16
        buster_icon_y = icon_y + 8

        # Draw yellow box for image placeholder (smaller size)
        box_x = missile_text_x + missile_surface.get_width() + 10
        box_y = icon_y + 4  # Align with the missile icon vertically, moved down by 4 pixels
        box_width = 40  # Width is good
        box_height = 36  # Reduced height further

        # Draw the number "1" in the middle of the top line of the box (bigger font)
        number_font = pygame.font.Font(None, 28)  # Increased from 20 to make the number bigger
        number_text = "1"
        number_surface = number_font.render(number_text, True, (255, 255, 0))  # Yellow text

        # Position the number in the middle of the top line
        number_x = box_x + (box_width - number_surface.get_width()) // 2
        number_y = box_y - number_surface.get_height() // 2  # Position number to be centered on the top line

        # Draw the yellow box with gaps in the top line for the number
        # Left side
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x, box_y),
            (number_x - 5, box_y),  # Stop 5 pixels before the number (increased from 3 for larger font)
            1  # 1 pixel width for the line
        )

        # Right side
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (number_x + number_surface.get_width() + 5, box_y),  # Start 5 pixels after the number (increased from 3)
            (box_x + box_width, box_y),
            1  # 1 pixel width for the line
        )

        # Bottom line
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x, box_y + box_height - 4),
            (box_x + box_width, box_y + box_height - 4),
            1  # 1 pixel width for the line
        )

        # Left side line
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x, box_y),
            (box_x, box_y + box_height - 4),
            1  # 1 pixel width for the line
        )

        # Right side line
        pygame.draw.line(
            surface,
            (255, 255, 0),  # Yellow color
            (box_x + box_width, box_y),
            (box_x + box_width, box_y + box_height - 4),
            1  # 1 pixel width for the line
        )

        # Draw the number
        surface.blit(number_surface, (number_x, number_y))

    # FIX — use the variables that actually exist above

        # buster_icon_x = missile_text_x + missile_surface.get_width() + 16
        # buster_icon_y = icon_y  + 10
        #
        # surface.blit(self.buster_cannon_icon, (buster_icon_x, buster_icon_y))
        #
        weapon_name = self.starship.equipped_magic[0]

        if weapon_name is not None:
            icon_index = self.SUB_WEAPON_ICON_INDEX.get(weapon_name)

            if icon_index is not None:
                icon_rect = pygame.Rect(icon_index * 16, 0, 16, 16)
                icon = self.hud_sheet.subsurface(icon_rect)
                icon = pygame.transform.scale(icon, (24, 24))

                surface.blit(icon, (buster_icon_x, buster_icon_y))

    def draw_tiled_layers(self, surface: pygame.Surface) -> None:
        tile_size = self.tile_size
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        # Ordered render: BACKGROUND → GROUND → HAZARD
        for layer_name in ("background", "hazard"):
            layer = self.tiled_map.get_layer_by_name(layer_name)

            for col, row, image in layer.tiles():
                if image is None:
                    continue

                world_y = row * tile_size
                screen_y = world_y - self.camera_y

                # Cull off-screen tiles
                if screen_y + tile_size < 0 or screen_y > window_height:
                    continue

                surface.blit(image, (col * tile_size, screen_y))

    def update_collision_tiles(self, damage: int = 5) -> None:
        layer = self.tiled_map.get_layer_by_name("collision")
        tile_size = self.tile_size
        KNOCKBACK = 4

        # ---------- PLAYER ----------
        player = self.starship
        player_rect = player.hitbox

        for col, row, image in layer.tiles():
            if image is None:
                continue

            tile_rect = pygame.Rect(
                col * tile_size,
                row * tile_size,
                tile_size,
                tile_size
            )

            if player_rect.colliderect(tile_rect):
                if not player.invincible:
                    player.shipHealth -= damage
                    player.on_hit()

                # --- resolve collision by minimal overlap ---
                dx_left = player_rect.right - tile_rect.left
                dx_right = tile_rect.right - player_rect.left
                dy_top = player_rect.bottom - tile_rect.top
                dy_bottom = tile_rect.bottom - player_rect.top

                min_dx = min(dx_left, dx_right)
                min_dy = min(dy_top, dy_bottom)

                if min_dx < min_dy:
                    # resolve X
                    if dx_left < dx_right:
                        player.x -= dx_left + KNOCKBACK
                    else:
                        player.x += dx_right + KNOCKBACK
                else:
                    # resolve Y
                    if dy_top < dy_bottom:
                        player.y -= dy_top + KNOCKBACK
                    else:
                        player.y += dy_bottom + KNOCKBACK

                player.update_hitbox()
                break

        # ---------- ENEMIES ----------
        enemy_groups = (
            self.bileSpitterGroup,
            self.spinalRaptorGroup,
            self.triSpitterGroup,
            self.slaverGroup,
            self.bladeSpinnerGroup,
            self.fireLauncherGroup,
            self.kamikazeDroneGroup,
            self.transportWormGroup,
            self.acidLauncherGroup,
            self.ravagerGroup,
            self.waspStingerGroup,
            self.sporeFlowerGroup,
            self.spineLauncherGroup,
        )

        for group in enemy_groups:
            for enemy in list(group):
                enemy_rect = enemy.hitbox

                for col, row, image in layer.tiles():
                    if image is None:
                        continue

                    tile_rect = pygame.Rect(
                        col * tile_size,
                        row * tile_size,
                        tile_size,
                        tile_size
                    )

                    if enemy_rect.colliderect(tile_rect):
                        dx_left = enemy_rect.right - tile_rect.left
                        dx_right = tile_rect.right - enemy_rect.left
                        dy_top = enemy_rect.bottom - tile_rect.top
                        dy_bottom = tile_rect.bottom - enemy_rect.top

                        min_dx = min(dx_left, dx_right)
                        min_dy = min(dy_top, dy_bottom)

                        if min_dx < min_dy:
                            if dx_left < dx_right:
                                enemy.x -= dx_left + KNOCKBACK
                            else:
                                enemy.x += dx_right + KNOCKBACK
                        else:
                            if dy_top < dy_bottom:
                                enemy.y -= dy_top + KNOCKBACK
                            else:
                                enemy.y += dy_bottom + KNOCKBACK

                        enemy.update_hitbox()
                        break

    def draw_collision_tiles(self, surface: pygame.Surface) -> None:
        tile_size = self.tile_size
        window_height = GlobalConstants.GAMEPLAY_HEIGHT

        layer = self.tiled_map.get_layer_by_name("collision")

        for col, row, image in layer.tiles():
            if image is None:
                continue

            world_y = row * tile_size
            screen_y = world_y - self.camera_y

            # Cull off-screen tiles (same as background)
            if screen_y + tile_size < 0 or screen_y > window_height:
                continue

            surface.blit(image, (col * tile_size, screen_y))
