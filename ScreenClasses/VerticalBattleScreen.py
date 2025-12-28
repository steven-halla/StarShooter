import pygame
from pygame import Surface
import pytmx
import math

from Constants.GlobalConstants import GlobalConstants
from Constants.Timer import Timer
from Controller.KeyBoardControls import KeyBoardControls
from Entity.Bosses.BossLevelFour import BossLevelFour
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelThree import BossLevelThree
from Entity.Bosses.BossLevelTwo import BossLevelTwo
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TransportWorm import TransportWorm
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.Monsters.WaspStinger import WaspStinger
from Entity.StarShip import StarShip
from Movement.MoveRectangle import MoveRectangle
from ScreenClasses.Camera import Camera
from Weapons.Bullet import Bullet
# from game_state import GameState


class VerticalBattleScreen:
    def __init__(self):
        # self.isStart: bool = True
        self.playerDead: bool = False
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
        self.slaverGroup: list[Slaver] = []

        self.bossLevelOneGroup: list[BossLevelOne] = []
        self.bossLevelTwoGroup: list[BossLevelTwo] = []
        self.bossLevelThreeGroup: list[BossLevelThree] = []
        self.bossLevelFourGroup: list[BossLevelFour] = []

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

        self.WORLD_HEIGHT: int = GlobalConstants.WINDOWS_SIZE[1] * 3

        self.SCROLL_SPEED_PER_SECOND: float = 55.0
        self.camera_y: float = 0.0
        self.SCROLL_SPEED_PER_FRAME: float = 55.0

        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        self.window_width = window_width
        self.window_height = window_height

        self.camera = Camera(
            window_width=window_width,
            window_height=window_height,
            world_height=self.WORLD_HEIGHT,
            scroll_speed_per_frame=self.SCROLL_SPEED_PER_FRAME,
            initial_zoom=2.5,   # DO NOT TOUCH CAMERA SETTINGS
        )


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
        _, window_height = GlobalConstants.WINDOWS_SIZE

        # move camera UP in world space (so map scrolls down)
        self.camera_y -= self.map_scroll_speed_per_frame

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
            enemies = (
                    list(self.bileSpitterGroup) +
                    list(self.triSpitterGroup) +
                    list(self.slaverGroup) +
                    list(self.bladeSpinnerGroup) +
                    list(self.fireLauncherGroup) +
                    list(self.kamikazeDroneGroup) +
                    list(self.transportWormGroup) +
                    list(self.bossLevelThreeGroup) +
                    list(self.bossLevelTwoGroup) +
                    list(self.bossLevelOneGroup) +
                    list(self.bossLevelFourGroup)
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



    def draw(self, state) -> None:



        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        zoom = self.camera.zoom

        scene_surface = pygame.Surface((window_width, window_height))

        self.draw_tiled_background(scene_surface)

        scaled_scene = pygame.transform.scale(
            scene_surface,
            (int(window_width * zoom), int(window_height * zoom))
        )

        state.DISPLAY.fill(GlobalConstants.BLACK)
        state.DISPLAY.blit(scaled_scene, (0, 0))
        self.draw_player_hp_bar(state.DISPLAY)
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

    def draw_tiled_background(self, surface: Surface) -> None:
        tile_size = self.tile_size
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        bg_layer = self.tiled_map.get_layer_by_name("background")

        for col, row, image in bg_layer.tiles():
            world_x = col * tile_size
            world_y = row * tile_size

            # only apply vertical camera offset, NO zoom here
            screen_x = world_x
            screen_y = world_y - self.camera_y

            # cull off-screen tiles
            if screen_y + tile_size < 0 or screen_y > window_height:
                continue

            surface.blit(image, (screen_x, screen_y))

            # -----------------------------
            # Draw HAZARD layer
            # -----------------------------
        hazard_layer = self.tiled_map.get_layer_by_name("hazard")

        for col, row, image in hazard_layer.tiles():
            world_x = col * tile_size
            world_y = row * tile_size

            screen_x = world_x
            screen_y = world_y - self.camera_y

            if screen_y + tile_size < 0 or screen_y > window_height:
                continue

            surface.blit(image, (screen_x, screen_y))

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
                list(self.bossLevelOneGroup) +
                list(self.bossLevelTwoGroup) +
                list(self.bossLevelThreeGroup) +
                list(self.bossLevelFourGroup)



        )
        # -------------------------
        # PLASMA BLASTER → ENEMY COLLISION
        # -------------------------
        for plasma in list(self.plasma_blaster_bullets):
            plasma_rect = self.weapon_rectangle(plasma)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if plasma_rect.colliderect(enemy_rect):
                    print("⚡ PLASMA BLASTER HIT", type(enemy).__name__)
                    enemy.enemyHealth -= plasma.damage
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break  # plasma is gone, stop checking
        # -------------------------
        # WIND SLICER → ENEMY COLLISION
        # -------------------------
        for slicer in list(self.wind_slicer_bullets):
            slicer_rect = self.weapon_rectangle(slicer)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if slicer_rect.colliderect(enemy_rect):
                    print("🌪️ WIND SLICER HIT", type(enemy).__name__)
                    enemy.enemyHealth -= slicer.damage
                    # 🔥 WIND SLICER IS CONSUMED ON ENEMY HIT
                    if slicer in self.wind_slicer_bullets:
                        self.wind_slicer_bullets.remove(slicer)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break  # slicer is gone, stop checking
        # -------------------------
        # WIND SLICER → ENEMY BULLET COLLISION
        # -------------------------
        for slicer in list(self.wind_slicer_bullets):
            slicer_rect = self.weapon_rectangle(slicer)
            for enemy_bullet in list(self.enemy_bullets):
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if slicer_rect.colliderect(enemy_rect):
                    print("🌪️ WIND SLICER CUT BULLET")
                    self.enemy_bullets.remove(enemy_bullet)
                    self.wind_slicer_bullets.remove(slicer)
                    break
        # -------------------------
        # ENERGY BALL → ENEMY COLLISION
        # -------------------------
        for ball in list(self.energy_balls):
            ball_rect = self.weapon_rectangle(ball)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if ball_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= ball.damage
                    ball.is_active = False
                    if ball in self.energy_balls:
                        self.energy_balls.remove(ball)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break  # ball is gone, stop checking
        # -------------------------
        # HYPER LASER → ENEMY COLLISION
        # -------------------------
        for laser in list(self.hyper_laser_bullets):
            laser_rect = self.weapon_rectangle(laser)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if laser_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.hyper_laser_damage
                    laser.is_active = False
                    if laser in self.hyper_laser_bullets:
                        self.hyper_laser_bullets.remove(laser)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break  # laser is gone, stop checking
        # ------------------------
        # METAL SHIELD → ENEMY COLLISION
        # -------------------------
        for metal in list(self.metal_shield_bullets):
            metal_rect = self.weapon_rectangle(metal)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if metal_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.missileDamage
                    metal.is_active = False
                    if metal in self.metal_shield_bullets:
                        self.metal_shield_bullets.remove(metal)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break  # shield is gone, stop checking
        # -------------------------
        # MISSILE → ENEMY COLLISION
        # -------------------------
        for missile in list(self.player_missiles):
            missile_rect = self.weapon_rectangle(missile)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if missile_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.missileDamage
                    missile.is_active = False
                    if missile in self.player_missiles:
                        self.player_missiles.remove(missile)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break  # missile is gone, stop checking
        # -------------------------
        # NAPALM SPREAD → ENEMY COLLISION / AOE
        # -------------------------
        for napalm in list(self.napalm_spread_bullets):
            napalm_rect = pygame.Rect(
                napalm.x,
                napalm.y,
                napalm.width,
                napalm.height
            )
            # ----------------------------------
            # DIRECT HIT → FORCE EXPLOSION
            # ----------------------------------
            if not napalm.has_exploded:
                for enemy in all_enemies:
                    if napalm_rect.colliderect(enemy.hitbox):
                        napalm.has_exploded = True
                        napalm.explosion_timer.reset()
                        enemy.enemyHealth -= napalm.damage
                        if enemy.enemyHealth <= 0:
                            self.remove_enemy_if_dead(enemy)
                        break  # only ONE direct-hit explosion
            # ----------------------------------
            # EXPLOSION AOE DAMAGE (ONCE)
            # ----------------------------------
            # ----------------------------------
            # EXPLOSION AOE DAMAGE (LINGERING – TICKED)
            # ----------------------------------
            # ----------------------------------
            # EXPLOSION AOE DAMAGE (TIMED TICKS)
            # ----------------------------------
            if napalm.has_exploded and not napalm.explosion_timer.is_ready():

                if napalm.damage_timer.is_ready():

                    cx = napalm.x + napalm.width // 2
                    cy = napalm.y + napalm.height // 2
                    aoe_rect = pygame.Rect(
                        cx - napalm.area_of_effect_x // 2,
                        cy - napalm.area_of_effect_y // 2,
                        napalm.area_of_effect_x,
                        napalm.area_of_effect_y
                    )

                    for enemy in all_enemies:
                        if aoe_rect.colliderect(enemy.hitbox):
                            enemy.enemyHealth -= napalm.damage

                            if isinstance(enemy, TransportWorm):
                                print(f"[NAPALM] TransportWorm HP: {enemy.enemyHealth}")

                            if enemy.enemyHealth <= 0:
                                self.remove_enemy_if_dead(enemy)

                    napalm.damage_timer.reset()
                # 🔒 AOE MUST ONLY APPLY ONCE
            # ----------------------------------
            # EXPLOSION AOE DAMAGE (LINGERING)
            # ----------------------------------
            if napalm.has_exploded and not napalm.explosion_timer.is_ready():
                cx = napalm.x + napalm.width // 2
                cy = napalm.y + napalm.height // 2
                aoe_rect = pygame.Rect(
                    cx - napalm.area_of_effect_x // 2,
                    cy - napalm.area_of_effect_y // 2,
                    napalm.area_of_effect_x,
                    napalm.area_of_effect_y
                )
                for enemy in all_enemies:
                    if aoe_rect.colliderect(enemy.hitbox) and napalm.damage_timer.is_ready():
                        enemy.enemyHealth -= napalm.damage
                        napalm.damage_timer.reset()
        # -------------------------
        # BUSTER CANNON → ENEMY COLLISION
        # -------------------------
        for bc in list(self.buster_cannon_bullets):
            bc_rect = self.weapon_rectangle(bc)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if bc_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= bc.damage
                    bc.is_active = False
                    if bc in self.buster_cannon_bullets:
                        self.buster_cannon_bullets.remove(bc)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break
        # -------------------------
        # PLAYER BULLETS → ENEMY COLLISION
        # -------------------------
        for bullet in list(self.player_bullets):
            b_rect = self.weapon_rectangle(bullet)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if b_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= self.starship.bulletDamage
                    bullet.is_active = False
                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break
        # -------------------------
        # WAVE CRASH → ENEMY COLLISION
        # -------------------------
        for wave in list(self.wave_crash_bullets):
            w_rect = self.weapon_rectangle(wave)
            for enemy in all_enemies:
                enemy_rect = self.get_enemy_screen_rect(enemy)
                if w_rect.colliderect(enemy_rect):
                    enemy.enemyHealth -= wave.damage
                    wave.is_active = False
                    if wave in self.wave_crash_bullets:
                        self.wave_crash_bullets.remove(wave)
                    if enemy.enemyHealth <= 0:
                        self.remove_enemy_if_dead(enemy)
                    break

    def remove_enemy_if_dead(self, enemy) -> None:
        if enemy.enemyHealth > 0:
            return

        if enemy in self.kamikazeDroneGroup:
            self.kamikazeDroneGroup.remove(enemy)
        elif enemy in self.bileSpitterGroup:
            self.bileSpitterGroup.remove(enemy)
        elif enemy in self.triSpitterGroup:
            self.triSpitterGroup.remove(enemy)
        elif enemy in self.waspStingerGroup:
            self.waspStingerGroup.remove(enemy)
        elif enemy in self.bladeSpinnerGroup:
            self.bladeSpinnerGroup.remove(enemy)
        elif enemy in self.sporeFlowerGroup:
            self.sporeFlowerGroup.remove(enemy)
        elif enemy in self.spineLauncherGroup:
            self.spineLauncherGroup.remove(enemy)
        elif enemy in self.acidLauncherGroup:
            self.acidLauncherGroup.remove(enemy)
        elif enemy in self.ravagerGroup:
            self.ravagerGroup.remove(enemy)
        elif enemy in self.fireLauncherGroup:
            self.fireLauncherGroup.remove(enemy)
        elif enemy in self.slaverGroup:
            self.slaverGroup.remove(enemy)
        elif enemy in self.bossLevelOneGroup:
            self.bossLevelOneGroup.remove(enemy)
        elif enemy in self.bossLevelTwoGroup:
            self.bossLevelTwoGroup.remove(enemy)

        elif enemy in self.bossLevelThreeGroup:
            self.bossLevelThreeGroup.remove(enemy)

        elif enemy in self.bossLevelFourGroup:
            self.bossLevelFourGroup.remove(enemy)

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
        panel_rect = pygame.Rect(
            0,
            GlobalConstants.GAMEPLAY_HEIGHT,  # bottom of gameplay
            GlobalConstants.BASE_WINDOW_WIDTH,
            GlobalConstants.UI_PANEL_HEIGHT
        )

        # panel background
        pygame.draw.rect(surface, (20, 20, 20), panel_rect)

        # top border line
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (0, GlobalConstants.GAMEPLAY_HEIGHT),
            (GlobalConstants.BASE_WINDOW_WIDTH, GlobalConstants.GAMEPLAY_HEIGHT),
            2
        )
