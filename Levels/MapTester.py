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

        self.load_enemy_into_list()


    def update(self, state) -> None:
        super().update(state)
        # Missile firing (override parent behavior)
        if self.controller.fire_missiles:

            missile = self.starship.missile.fire_missile()
            if missile is not None:

                # Lock onto nearest enemy
                missile.target_enemy = self.get_nearest_enemy(missile)

                # Compute initial direction toward target
                if missile.target_enemy is not None:
                    dx = missile.target_enemy.x - missile.x
                    dy = missile.target_enemy.y - missile.y
                    dist = max(1, (dx * dx + dy * dy) ** 0.5)
                    missile.direction_x = dx / dist
                    missile.direction_y = dy / dist
                else:
                    # No enemy → missile goes straight upward
                    missile.direction_x = 0
                    missile.direction_y = -1

                # Add to missile list
                self.player_missiles.append(missile)

                if missile.target_enemy is not None:
                    print(f"Missile locked onto: {type(missile.target_enemy).__name__} "
                          f"at ({missile.target_enemy.x}, {missile.target_enemy.y})")
                else:
                    print("Missile locked onto: NONE (no enemies found)")
        self.enemy_helper()


        self.extract_object_names()


    def draw(self, state):
        super().draw(state)
        for napalm in self.napalm_list:
            napalm.draw(state.DISPLAY, self.camera)
        zoom = self.camera.zoom

        for obj in self.tiled_map.objects:
            if hasattr(obj, "image") and obj.image is not None:
                screen_x = self.camera.world_to_screen_x(obj.x)
                screen_y = self.camera.world_to_screen_y(obj.y)
                state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)
        for enemy in self.enemies:
            enemy.draw(state.DISPLAY, self.camera)


        pygame.display.flip()

    def get_nearest_enemy(self, missile):

        if not self.enemies:
            return None

        # Visible camera bounds (world coordinates)
        visible_top = self.camera.y
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        nearest_enemy = None
        nearest_dist = float("inf")
        mx, my = missile.x, missile.y

        for enemy in self.enemies:

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

    def load_enemy_into_list(self):
        self.enemies.clear()
        # print("[LOAD] clearing enemies list")

        for obj in self.tiled_map.objects:
            enemy = None

            print(f"[TMX] found object name={obj.name} at ({obj.x}, {obj.y})")

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
            self.enemies.append(enemy)

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

            self.enemies.append(enemy)

            print(
                f"[ADD] {enemy.__class__.__name__} "
                f"hp={enemy.enemyHealth} "
                f"→ enemies size = {len(self.enemies)}"
            )

        print(f"[DONE] total enemies loaded = {len(self.enemies)}")

    def enemy_helper(self):
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
        for metal in self.player_bullets:

            # ⛔ Metal Shield does NOT participate in enemy_helper
            if metal.weapon_name == "Metal Shield":
                continue

            # safe for normal bullets only
            # only bullets with hitbox participate in enemy_helper
            if not hasattr(metal, "hitbox"):
                continue

            bullet_rect = metal.hitbox
            shield_rect = metal.hitbox

            for bullet in list(self.enemy_bullets):

                if bullet.collide_with_rect(shield_rect):

                    absorbed = metal.absorb_hit()

                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    if absorbed and metal in self.player_bullets:
                        self.player_bullets.remove(metal)

                    break

            for bullet in list(self.enemy_bullets):

                # Enemy bullets already have a hitbox / rect logic
                if bullet.collide_with_rect(shield_rect):

                    # Shield absorbs the hit
                    absorbed = metal.absorb_hit()

                    # Remove enemy bullet
                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    # Remove shield if it absorbed
                    if absorbed and metal in self.player_bullets:
                        self.player_bullets.remove(metal)

                    break  # one hit only

        for boss in list(self.enemies):
            boss.update()

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.enemies.remove(boss)
                continue

        for enemy_tri_spitter in self.enemies:
            enemy_tri_spitter.update()
            if self.starship.hitbox.colliderect(enemy_tri_spitter.hitbox):
                enemy_tri_spitter.color = (135, 206, 235)  # SKYBLUE
            else:
                enemy_tri_spitter.color = GlobalConstants.RED
            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()

