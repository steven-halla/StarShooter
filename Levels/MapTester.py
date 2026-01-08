import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.Monsters.WaspStinger import WaspStinger
from Entity.StarShip import StarShip
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class MapTester(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()



        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level1.tmx")
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
        self.bileSpitterGroup: list[BileSpitter] = []
        self.kamikazeDroneGroup: list[KamikazeDrone] = []
        self.triSpitterGroup: list[TriSpitter] = []
        # self.load_enemy_into_list()
        self.napalm_list: list = []

    def start(self, state) -> None:
        print("start fun called")
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
            missile = self.starship.fire_missile()
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
        for enemy in self.fireLauncherGroup:
            enemy.draw(state.DISPLAY, self.camera)
        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY, self.camera)
        for enemy in self.acidLauncherGroup:
            enemy.draw(state.DISPLAY, self.camera)

        for enemy in self.spineLauncherGroup:
            enemy.draw(state.DISPLAY, self.camera)

        for enemy in self.sporeFlowerGroup:
            enemy.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.draw(state.DISPLAY, self.camera)

        for drone in self.kamikazeDroneGroup:
            drone.draw(state.DISPLAY, self.camera)

        for wasp in self.waspStingerGroup:
            wasp.draw(state.DISPLAY, self.camera)
        for ravager in self.ravagerGroup:
            ravager.draw(state.DISPLAY, self.camera)
        for blade in self.bladeSpinnerGroup:
            blade.draw(state.DISPLAY, self.camera)
        for boss in self.bossLevelOneGroup:
            boss.draw(state.DISPLAY, self.camera)

        for enemy_tri_spitter in self.triSpitterGroup:
            hb = pygame.Rect(
                self.camera.world_to_screen_x(enemy_tri_spitter.hitbox.x),
                self.camera.world_to_screen_y(enemy_tri_spitter.hitbox.y),
                int(enemy_tri_spitter.hitbox.width * zoom),
                int(enemy_tri_spitter.hitbox.height * zoom)
            )
            pygame.draw.rect(state.DISPLAY, (255, 255, 0), hb, 2)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                list(self.bileSpitterGroup) +
                list(self.kamikazeDroneGroup) +
                list(self.triSpitterGroup) +
                list(self.waspStingerGroup) +
                list(self.bladeSpinnerGroup) +
                list(self.sporeFlowerGroup) +
                list(self.spineLauncherGroup) +
                list(self.acidLauncherGroup) +
                list(self.ravagerGroup) +
                list(self.fireLauncherGroup) +
                list(self.bossLevelOneGroup)
        )

        if not enemies:
            return None

        # Visible camera bounds (world coordinates)
        visible_top = self.camera.y
        visible_bottom = self.camera.y + (self.window_height / self.camera.zoom)

        nearest_enemy = None
        nearest_dist = float("inf")
        mx, my = missile.x, missile.y

        for enemy in enemies:

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
        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "level_1_boss":
                enemy = BossLevelOne()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bossLevelOneGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
            if obj.name == "fire_launcher":
                enemy = FireLauncher()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.fireLauncherGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
            if obj.name == "ravager":
                enemy = Ravager()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.ravagerGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
            if obj.name == "acid_launcher":
                enemy = AcidLauncher()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.acidLauncherGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship

            if obj.name == "spine_launcher":
                enemy = SpineLauncher()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.spineLauncherGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
            if obj.name == "spore_flower":
                enemy = SporeFlower()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.sporeFlowerGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
            if obj.name == "wasp_stinger":
                enemy = WaspStinger()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.waspStingerGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
            if obj.name == "bile_spitter":
                enemy = BileSpitter()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bileSpitterGroup.append(enemy)

            if obj.name == "kamikazi_drone":
                drone = KamikazeDrone()
                drone.x = obj.x
                drone.y = obj.y
                drone.width = obj.width
                drone.height = obj.height
                drone.update_hitbox()
                self.kamikazeDroneGroup.append(drone)
                drone.camera = self.camera
                drone.target_player = self.starship
                continue
            if obj.name == "blade_spinner":
                enemy = BladeSpinner()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                self.bladeSpinnerGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
                continue

            if obj.name == "tri_spitter":
                enemy_tri_spitter = TriSpitter()
                enemy_tri_spitter.x = obj.x
                enemy_tri_spitter.y = obj.y
                enemy_tri_spitter.width = obj.width
                enemy_tri_spitter.height = obj.height
                enemy_tri_spitter.update_hitbox()
                self.triSpitterGroup.append(enemy_tri_spitter)
                enemy_tri_spitter.camera = self.camera
                enemy_tri_spitter.target_player = self.starship
                continue

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
        # -------------------------
        for metal in list(self.metal_shield_bullets):

            if not metal.is_active:
                self.metal_shield_bullets.remove(metal)
                continue

            # Build shield rect in WORLD space
            shield_rect = pygame.Rect(
                metal.x,
                metal.y,
                metal.width,
                metal.height
            )

            for bullet in list(self.enemy_bullets):

                # Enemy bullets already have a hitbox / rect logic
                if bullet.collide_with_rect(shield_rect):

                    # Shield absorbs the hit
                    absorbed = metal.absorb_hit()

                    # Remove enemy bullet
                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    # Remove shield if it absorbed
                    if absorbed and metal in self.metal_shield_bullets:
                        self.metal_shield_bullets.remove(metal)

                    break  # one hit only

        for boss in list(self.bossLevelOneGroup):
            boss.update()

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelOneGroup.remove(boss)
                continue

        for blade in list(self.bladeSpinnerGroup):
            blade.update()

            if blade.enemyHealth <= 0:
                self.bladeSpinnerGroup.remove(blade)
                continue

        for wasp in list(self.waspStingerGroup):
            wasp.update()

            if wasp.enemyHealth <= 0:
                self.waspStingerGroup.remove(wasp)
                continue

        for ravager in list(self.ravagerGroup):
            napalm = ravager.update()

            if napalm is not None:
                self.napalm_list.append(napalm)
                print("NAPALM ADDED TO LEVEL", len(self.napalm_list))

            if ravager.enemyBullets:
                self.enemy_bullets.extend(ravager.enemyBullets)
                ravager.enemyBullets.clear()

            if ravager.enemyHealth <= 0:
                self.ravagerGroup.remove(ravager)

        for drone in list(self.kamikazeDroneGroup):
            drone.update()

            if drone.enemyHealth <= 0:
                self.kamikazeDroneGroup.remove(drone)
                continue

        for fire in list(self.fireLauncherGroup):
            fire.update()

            if fire.enemyBullets:
                self.enemy_bullets.extend(fire.enemyBullets)
                fire.enemyBullets.clear()

            if fire.enemyHealth <= 0:
                self.fireLauncherGroup.remove(fire)
                continue

        for spore in list(self.sporeFlowerGroup):
            spore.update()

            if spore.enemyBullets:
                self.enemy_bullets.extend(spore.enemyBullets)
                spore.enemyBullets.clear()

            if spore.enemyHealth <= 0:
                self.sporeFlowerGroup.remove(spore)
                continue

        for acid in list(self.acidLauncherGroup):
            acid.update()

            if acid.enemyBullets:
                self.enemy_bullets.extend(acid.enemyBullets)
                acid.enemyBullets.clear()

            if acid.enemyHealth <= 0:
                self.spineLauncherGroup.remove(acid)
                continue

        for spine in list(self.spineLauncherGroup):
            spine.update()

            if spine.enemyBullets:
                self.enemy_bullets.extend(spine.enemyBullets)
                spine.enemyBullets.clear()

            if spine.enemyHealth <= 0:
                self.spineLauncherGroup.remove(spine)
                continue

        for enemy in self.bileSpitterGroup:
            enemy.update()
            if self.starship.hitbox.colliderect(enemy.hitbox):
                enemy.color = (135, 206, 235)  # SKYBLUE
            else:
                enemy.color = GlobalConstants.RED
            enemy.update_hitbox()

            if enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

        for enemy_tri_spitter in self.triSpitterGroup:
            enemy_tri_spitter.update()
            if self.starship.hitbox.colliderect(enemy_tri_spitter.hitbox):
                enemy_tri_spitter.color = (135, 206, 235)  # SKYBLUE
            else:
                enemy_tri_spitter.color = GlobalConstants.RED
            enemy_tri_spitter.update_hitbox()

            if enemy_tri_spitter.enemyBullets:
                self.enemy_bullets.extend(enemy_tri_spitter.enemyBullets)
                enemy_tri_spitter.enemyBullets.clear()

