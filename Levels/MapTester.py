import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.Coins import Coins
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.PodLayer import PodLayer
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.RescuePod import RescuePod
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.SpikeyBall import SpikeyBall
from Entity.Monsters.SpinalRaptor import SpinalRaptor
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TransportWorm import TransportWorm
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.Monsters.WaspStinger import WaspStinger
from Entity.StarShip import StarShip
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen
from Weapons.Bullet import Bullet


class MapTester(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()



        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/test_map.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4 # move speed of camera

        self.napalm_list: list = []

    def start(self, state) -> None:
        print("start fun calledf")
        player_x = None
        player_y = None

        # 🔧 REQUIRED: bind global starship into this screen
        self.starship = state.starship

        for obj in self.tiled_map.objects:
            if obj.name == "player":
                player_x = obj.x
                player_y = obj.y
                break

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()

        self.load_enemy_into_list(state)


    def update(self, state) -> None:
        # Call parent update but override bullet-related methods
        # First, save the original methods
        original_bullet_helper = self.bullet_helper
        original_weapon_helper = self.weapon_helper
        original_metal_shield_helper = self.metal_shield_helper
        original_bullet_collision_helper_remover = self.bullet_collision_helper_remover
        original_fire_all_weapons = self.fire_all_weapons

        # Replace with dummy methods to prevent parent class from using them
        self.bullet_helper = lambda: None
        self.weapon_helper = lambda: None
        self.metal_shield_helper = lambda: None
        self.bullet_collision_helper_remover = lambda: None
        self.fire_all_weapons = lambda s: None

        # Call parent update but skip the original fire_all_weapons
        # We need to modify the controller update and other basic functionality
        self.controller.update()

        # THEN: react to input
        if self.textbox.is_visible():
            if self.controller.qJustPressed:
                self.textbox.advance()

        self.move_map_y_axis()

        if not hasattr(self, "start_has_run"):
            self.start(state)
            self.start_has_run = True

        if self.starship.shipHealth <= 0:
            self.playerDead = True

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
        self.clamp_starship_to_screen()

        # Restore original methods
        self.bullet_helper = original_bullet_helper
        self.weapon_helper = original_weapon_helper
        self.metal_shield_helper = original_metal_shield_helper
        self.bullet_collision_helper_remover = original_bullet_collision_helper_remover
        self.fire_all_weapons = original_fire_all_weapons

        # Call our overridden methods with state parameter
        self.fire_all_weapons(state)
        self.bullet_helper(state)
        self.weapon_helper(state)
        self.metal_shield_helper(state)
        self.bullet_collision_helper_remover(state)

        # Collect enemy bullets
        for enemy in state.enemies:
            if hasattr(enemy, "enemyBullets"):
                for b in enemy.enemyBullets:
                    state.enemy_bullets.append(b)
                enemy.enemyBullets.clear()

        # Other helpers
        self.collision_tile_helper(state)
        self.rect_helper(state)

        # Handle enemies that go off screen
        UI_KILL_PADDING = 12  # pixels ABOVE the UI panel
        screen_bottom = (
                self.camera.y
                + (GlobalConstants.GAMEPLAY_HEIGHT / self.camera.zoom)
                - UI_KILL_PADDING
        )

        for enemy in list(state.enemies):
            # Skip coins
            if isinstance(enemy, Coins):
                continue

            # enemy is BELOW visible gameplay area
            if enemy.y > screen_bottom:
                enemy.is_active = False
                state.enemies.remove(enemy)

        # Note: Missile firing is now handled in fire_all_weapons method

        # Process enemy interactions
        self.enemy_helper(state)

        # Extract object names for debugging
        self.extract_object_names()


    def draw(self, state):
        # Call parent draw but override bullet-related methods
        # First, save the original methods
        original_draw_sub_weapon_rect_helper = self.draw_sub_weapon_rect_helper

        # Replace with our custom method
        self.draw_sub_weapon_rect_helper = lambda s: self.custom_draw_sub_weapon_rect_helper(s)

        # Call parent draw with modified methods
        window_width = GlobalConstants.BASE_WINDOW_WIDTH
        window_height = GlobalConstants.GAMEPLAY_HEIGHT
        scene_surface = pygame.Surface((window_width, window_height))
        scene_surface.fill((20, 20, 40))  # sky / space color
        zoom = self.camera.zoom

        self.draw_tiled_layers(scene_surface)

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

        # Draw player bullets with our custom method
        self.draw_sub_weapon_rect_helper(state)

        # Draw enemy bullets with camera transform
        for bullet in state.enemy_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * self.camera.zoom)
            bh = int(bullet.height * self.camera.zoom)

            # Draw a larger, more visible bullet for debugging
            pygame.draw.rect(
                state.DISPLAY,
                (255, 0, 0),  # RED for better visibility
                pygame.Rect(bx-2, by-2, bw+4, bh+4),
                0
            )

            # Draw the actual bullet
            pygame.draw.rect(
                state.DISPLAY,
                (0, 255, 0),  # GREEN
                pygame.Rect(bx, by, bw, bh),
                0
            )

        # Draw UI panel
        self.draw_ui_panel(state.DISPLAY)

        # Draw player hitbox
        px = self.camera.world_to_screen_x(self.starship.hitbox.x)
        py = self.camera.world_to_screen_y(self.starship.hitbox.y)
        pw = int(self.starship.hitbox.width * self.camera.zoom)
        ph = int(self.starship.hitbox.height * self.camera.zoom)

        pygame.draw.rect(
            state.DISPLAY,
            (255, 0, 0),
            pygame.Rect(px, py, pw, ph),
            2
        )

        # Draw napalm and other objects
        for napalm in self.napalm_list:
            napalm.draw(state.DISPLAY, self.camera)

        for obj in self.tiled_map.objects:
            if hasattr(obj, "image") and obj.image is not None:
                screen_x = self.camera.world_to_screen_x(obj.x)
                screen_y = self.camera.world_to_screen_y(obj.y)
                state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)

        # Restore original methods
        self.draw_sub_weapon_rect_helper = original_draw_sub_weapon_rect_helper

        pygame.display.flip()

    def custom_draw_sub_weapon_rect_helper(self, state):
        zoom = self.camera.zoom

        for bullet in state.player_bullets:
            bx = self.camera.world_to_screen_x(bullet.x)
            by = self.camera.world_to_screen_y(bullet.y)
            bw = int(bullet.width * zoom)
            bh = int(bullet.height * zoom)
            rect = pygame.Rect(bx, by, bw, bh)

            # ---- visual by capability / type ----
            if hasattr(bullet, "area_of_effect_x"):  # Napalm
                if getattr(bullet, "has_exploded", False):
                    aoe_w = int(bullet.area_of_effect_x * zoom)
                    aoe_h = int(bullet.area_of_effect_y * zoom)
                    aoe_rect = pygame.Rect(
                        bx - aoe_w // 2,
                        by - aoe_h // 2,
                        aoe_w,
                        aoe_h
                    )
                    pygame.draw.rect(state.DISPLAY, (255, 80, 0), aoe_rect, 4)
                else:
                    pygame.draw.rect(state.DISPLAY, (255, 100, 0), rect)

            elif hasattr(bullet, "update_orbit"):  # Metal Shield
                pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

            elif hasattr(bullet, "target_enemy"):  # Missile
                pygame.draw.rect(state.DISPLAY, (128, 0, 128), rect)

            elif bullet.weapon_name == "Buster Cannon":
                pygame.draw.rect(state.DISPLAY, (255, 255, 255), rect)
                pygame.draw.rect(
                    state.DISPLAY,
                    (255, 255, 0),
                    (bx - 2, by - 2, bw + 4, bh + 4),
                    5
                )

            elif bullet.weapon_name == "Wind Slicer":
                pygame.draw.rect(state.DISPLAY, (180, 220, 255), rect)

            elif bullet.weapon_name == "Energy Ball":
                pygame.draw.rect(state.DISPLAY, (0, 200, 255), rect)

            elif bullet.weapon_name == "Wave Crash":
                pygame.draw.rect(state.DISPLAY, (0, 255, 0), rect)

            elif bullet.weapon_name == "Plasma Blaster":
                pygame.draw.rect(state.DISPLAY, (0, 255, 255), rect)

            else:  # default (machine gun, etc.)
                pygame.draw.rect(state.DISPLAY, (255, 255, 0), rect)

            pygame.draw.rect(state.DISPLAY, (255, 255, 0), rect, 1)

    def fire_all_weapons(self, state):
        def has_active(self, weapon_name: str) -> bool:
            return any(b.weapon_name == weapon_name for b in state.player_bullets)

        # -------------------------
        # MACHINE GUN
        # -------------------------
        if self.controller.main_weapon_button and not self.playerDead:
            state.player_bullets.extend(
                self.starship.machine_gun.fire_machine_gun()
            )

        # -------------------------
        # PLAYER MISSILES
        # -------------------------
        if self.controller.fire_missiles and not self.playerDead:
            self.starship.missile.x = self.starship.x
            self.starship.missile.y = self.starship.y

            missile = self.starship.missile.fire_missile()
            if missile is not None:
                state.player_bullets.append(missile)

        # -------------------------
        # BUSTER CANNON
        # -------------------------
        if state.starship.equipped_magic[0] == "Buster Cannon" and not self.playerDead:
            if self.controller.magic_1_button:
                if not state.starship.buster_cannon.is_charging:
                    state.starship.buster_cannon.start_charge()
                state.starship.buster_cannon.update()
            elif state.starship.buster_cannon.is_charging:
                state.player_bullets.extend(
                    state.starship.buster_cannon.fire_buster_cannon()
                )

        # -------------------------
        # PLASMA BLASTER (single beam)
        # -------------------------
        if state.starship.equipped_magic[0] == "Plasma Blaster" and not self.playerDead:
            if self.controller.magic_1_button and not has_active(self, "Plasma Blaster"):
                plasma = state.starship.plasma_blaster.fire_plasma_blaster()
                if plasma is not None:
                    state.player_bullets.append(plasma)

        # -------------------------
        # ENERGY BALL (ROF internal)
        # -------------------------
        if state.starship.equipped_magic[0] == "Energy Ball" and not self.playerDead:
            if self.controller.magic_1_button:
                energy_ball = state.starship.energy_ball.fire_energy_ball(self.controller)
                if energy_ball is not None:
                    state.player_bullets.append(energy_ball)

        # -------------------------
        # METAL SHIELD (single)
        # -------------------------
        if state.starship.equipped_magic[0] == "Metal Shield" and not self.playerDead:
            if self.controller.magic_1_button and not has_active(self, "Metal Shield"):
                shield = state.starship.metal_shield.fire_metal_shield()
                if shield is not None:
                    state.player_bullets.append(shield)

        # -------------------------
        # NAPALM SPREAD
        # -------------------------
        if state.starship.equipped_magic[0] == "Napalm Spread" and not self.playerDead:
            if self.controller.magic_1_button:
                napalm = state.starship.napalm_spread.fire_napalm_spread()
                if napalm is not None:
                    state.player_bullets.append(napalm)

        # -------------------------
        # BEAM SABER (single, held)
        # -------------------------
        if state.starship.equipped_magic[0] == "Beam Saber" and not self.playerDead:
            if self.controller.magic_1_button and not has_active(self, "Beam Saber"):
                saber = state.starship.beam_saber.fire_beam_saber()
                if saber is not None:
                    state.player_bullets.append(saber)

        if not self.controller.magic_1_button:
            state.player_bullets[:] = [
                b for b in state.player_bullets if b.weapon_name != "Beam Saber"
            ]

        # -------------------------
        # WAVE CRASH
        # -------------------------
        if state.starship.equipped_magic[0] == "Wave Crash" and not self.playerDead:
            if self.controller.magic_1_button:
                state.player_bullets.extend(
                    state.starship.wave_crash.fire_wave_crash()
                )

        # -------------------------
        # WIND SLICER
        # -------------------------
        if state.starship.equipped_magic[0] == "Wind Slicer" and not self.playerDead:
            if self.controller.magic_1_button:
                state.player_bullets.extend(
                    state.starship.wind_slicer.fire_wind_slicer()
                )

    def get_nearest_enemy(self, state, missile):

        if not state.enemies:
            return None

        # Visible camera bounds (world coordinates)
        visible_top = self.camera.y
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        nearest_enemy = None
        nearest_dist = float("inf")
        mx, my = missile.x, missile.y

        for enemy in state.enemies:

            # ⛔ Skip enemies outside the screen
            if enemy.y + enemy.height < visible_top:
                continue  # enemy is above screen
            if enemy.y > visible_bottom:
                continue  # enemy is below screen

            # distance calculation
            dx = enemy.x - mx
            dy = enemy.y - my
            dist_sq = dx * dx + dy * dy

            if dist_sq < nearest_dist:
                nearest_dist = dist_sq
                nearest_enemy = enemy

        return nearest_enemy

    def extract_object_names(self) -> list[str]:
        """
        Returns a list of all object.name strings found in the Tiled map.
        """
        names = []

        for obj in self.tiled_map.objects:
            if hasattr(obj, "name") and obj.name:
                names.append(obj.name)
        # print(names)
        return names

    def bullet_helper(self, state=None):
        for bullet in list(state.player_bullets):

            # -------------------------
            # METAL SHIELD (uses rect, not hitbox)
            # -------------------------
            if bullet.weapon_name == "Metal Shield":
                shield_rect = bullet.rect

                for enemy in list(state.enemies):
                    if shield_rect.colliderect(enemy.hitbox):
                        enemy.enemyHealth -= bullet.damage
                        if enemy.enemyHealth <= 0:
                            self.remove_enemy_if_dead(enemy)
                continue

            # -------------------------
            # ALL OTHER BULLETS
            # -------------------------
            if not hasattr(bullet, "rect"):
                continue

            bullet_rect = bullet.rect

            for enemy in list(state.enemies):
                # Skip coins - they should only be collected by starship collision
                if hasattr(enemy, "__class__") and enemy.__class__.__name__ == "Coins":
                    continue

                if not bullet_rect.colliderect(enemy.hitbox):
                    continue

                enemy.enemyHealth -= getattr(bullet, "damage", 0)

                if hasattr(bullet, "trigger_explosion"):
                    bullet.trigger_explosion()
                elif getattr(bullet, "is_piercing", False):
                    pass
                else:
                    if bullet in state.player_bullets:
                        state.player_bullets.remove(bullet)

                if enemy.enemyHealth <= 0:
                    self.remove_enemy_if_dead(enemy, state)
                break

    def weapon_helper(self, state=None):
        for bullet in list(state.player_bullets):

            # --- movement / positioning ---
            if bullet.weapon_name == "Missile":
                if getattr(bullet, "target_enemy", None) is None and hasattr(self, "get_nearest_enemy"):
                    bullet.target_enemy = self.get_nearest_enemy(bullet,missile=self)
                bullet.update()

            elif bullet.weapon_name == "Metal Shield":
                bullet.update_orbit(
                    self.starship.x + self.starship.width / 2,
                    self.starship.y + self.starship.height / 2
                )

            elif bullet.weapon_name == "Beam Saber":
                bullet.x = self.starship.x + self.starship.width // 2
                bullet.y = self.starship.y - 20
                bullet.update()

            else:
                bullet.update()

            # 🔴 CRITICAL: rect must always be updated AFTER movement
            bullet.update_rect()

    def metal_shield_helper(self, state=None):
        for bullet in list(state.player_bullets):

            if bullet.weapon_name == "Metal Shield":
                continue  # never auto-remove shield

            screen_x = bullet.x - getattr(self.camera, "x", 0)
            screen_y = bullet.y - self.camera.y

            off_screen = (
                    screen_y + bullet.height < 0 or
                    screen_y > (self.window_height / self.camera.zoom) or
                    screen_x + bullet.width < 0 or
                    screen_x > (self.window_width / self.camera.zoom)
            )

            if off_screen or not getattr(bullet, "is_active", True):
                state.player_bullets.remove(bullet)

    def bullet_collision_helper_remover(self, state=None):
        for bullet in list(state.enemy_bullets):
            bullet.update()
            # Increase the buffer zone to ensure bullets have more time to appear on screen
            world_top_delete = self.camera.y - 500
            # Adjust for camera zoom to get correct world coordinates and increase buffer
            world_bottom_delete = self.camera.y + (self.window_height / self.camera.zoom) + 500

            # Debug print to help diagnose the issue
            # print(f"[BULLET CHECK] bullet.y={bullet.y:.1f}, camera.y={self.camera.y:.1f}, world_bottom_delete={world_bottom_delete:.1f}")

            if bullet.y < world_top_delete or bullet.y > world_bottom_delete and bullet.remove_type == 0:
                # print(f"[DELETE BULLET] y={bullet.y:.1f}, cam_y={self.camera.y:.1f}, reason: {'above' if bullet.y < world_top_delete else 'below'}")
                state.enemy_bullets.remove(bullet)
                continue

            # Collision check
            if bullet.collide_with_rect(self.starship.hitbox):
                self.starship.shipHealth -= bullet.damage
                bullet.is_active = False
                if bullet.remove_type == 0:
                    state.enemy_bullets.remove(bullet)

    def load_enemy_into_list(self, state):
        state.enemies.clear()
        # print("[LOAD] clearing enemies list")

        for obj in self.tiled_map.objects:
            enemy = None

            # print(f"[TMX] found object name={obj.name} at ({obj.x}, {obj.y})")

            if obj.name == "acid_launcher":
                enemy = AcidLauncher()

            elif obj.name == "bile_spitter":
                enemy = BileSpitter()

            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()

            elif obj.name == "coin":
                enemy = Coins()

            elif obj.name == "fire_launcher":
                enemy = FireLauncher()

            elif obj.name == "kamikaze_drone":
                enemy = KamikazeDrone()

            elif obj.name == "pod_layer":
                enemy = PodLayer()

            elif obj.name == "ravager":
                enemy = Ravager()

            elif obj.name == "rescue_pod":
                enemy = RescuePod()

            elif obj.name == "slaver":
                enemy = Slaver()

            elif obj.name == "spikey_ball":
                enemy = SpikeyBall()

            elif obj.name == "spinal_raptor":
                enemy = SpinalRaptor()

            elif obj.name == "spine_launcher":
                enemy = SpineLauncher()

            elif obj.name == "spore_flower":
                enemy = SporeFlower()

            elif obj.name == "transport_worm":
                enemy = TransportWorm()

            elif obj.name == "tri_spitter":
                enemy = TriSpitter()

            elif obj.name == "wasp_stinger":
                enemy = WaspStinger()

            if enemy is None:
                continue

            enemy.x = obj.x
            enemy.y = obj.y
            state.enemies.append(enemy)

            # -------------------------
            # POSITION / SIZE
            # -------------------------
            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height

            # -------------------------
            # REQUIRED STATE
            # -------------------------
            enemy.camera = self.camera
            enemy.target_player = self.starship

            # -------------------------
            # HEALTH INIT (CRITICAL)
            # -------------------------
            if hasattr(enemy, "maxHealth"):
                enemy.enemyHealth = enemy.maxHealth
            else:
                enemy.enemyHealth = 1  # safe fallback

            enemy.update_hitbox()

            state.enemies.append(enemy)

            print(
                f"[ADD] {enemy.__class__.__name__} "
                f"hp={enemy.enemyHealth} "
                f"→ enemies size = {len(state.enemies)}"
            )

        # print(f"[DONE] total enemies loaded = {len(state.enemies)}")

    def enemy_helper(self, state):
        # -------------------------
        # NAPALM UPDATE + DAMAGE
        # -------------------------
        for napalm in list(self.napalm_list):
            napalm.update()
            print("NAPALM UPDATE", napalm.x, napalm.y, napalm.is_active)

            if napalm.is_active and napalm.hits(self.starship.hitbox):
                if not self.starship.invincible:
                    self.starship.shipHealth -= napalm.damage
                    self.starship.on_hit()

            # Remove expired napalm
            if not napalm.is_active:
                self.napalm_list.remove(napalm)
        # -------------------------
        # METAL SHIELD → ENEMY BULLETS
        for metal in state.player_bullets:

            # ⛔ Metal Shield does NOT participate in enemy_helper
            if metal.weapon_name == "Metal Shield":
                continue

            # safe for normal bullets only
            # only bullets with hitbox participate in enemy_helper
            if not hasattr(metal, "hitbox"):
                continue

            bullet_rect = metal.hitbox
            shield_rect = metal.hitbox

            for bullet in list(state.enemy_bullets):

                if bullet.collide_with_rect(shield_rect) and bullet.remove_type == 0:

                    absorbed = metal.absorb_hit()

                    if bullet in state.enemy_bullets:
                        state.enemy_bullets.remove(bullet)

                    if absorbed and metal in state.player_bullets:
                        state.player_bullets.remove(metal)

                    break

            for bullet in list(state.enemy_bullets):

                # Enemy bullets already have a hitbox / rect logic
                if bullet.collide_with_rect(shield_rect) and bullet.remove_type == 0:

                    # Shield absorbs the hit
                    absorbed = metal.absorb_hit()

                    # Remove enemy bullet
                    if bullet in state.enemy_bullets:
                        state.enemy_bullets.remove(bullet)

                    # Remove shield if it absorbed
                    if absorbed and metal in state.player_bullets:
                        state.player_bullets.remove(metal)

                    break  # one hit only


        for enemy in list(state.enemies):
            enemy.update(state)



            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)


        # for enemy_tri_spitter in state.enemies:
        #     enemy_tri_spitter.update(state)
        #     if self.starship.hitbox.colliderect(enemy_tri_spitter.hitbox):
        #         enemy_tri_spitter.color = (135, 206, 235)  # SKYBLUE
        #     else:
        #         enemy_tri_spitter.color = GlobalConstants.RED
        #     enemy_tri_spitter.update_hitbox()
        #
        #     if enemy_tri_spitter.enemyBullets:
        #         self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
        #         enemy_tri_spitter.enemyBullets.clear()
