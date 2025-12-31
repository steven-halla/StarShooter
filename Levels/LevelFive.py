import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelFive import BossLevelFive
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Enemy import Enemy
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.Rescue_Pod import RescuePod
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.SpinalRaptor import SpinalRaptor
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TriSpitter import TriSpitter
from SaveStates.SaveState import SaveState
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelFive(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()

        self.level_start:bool = True
        self.current_page_lines: list[list[str]] = []
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level5.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_width: int = GlobalConstants.BASE_WINDOW_WIDTH
        window_height: int = GlobalConstants.GAMEPLAY_HEIGHT
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4 # move speed of camera

        self.rescue_pod_destroyed = 0  # Counter for destroyed rescue pods
        self.rescuePodGroup: list[RescuePod] = []
        self.spinalRaptorGroup: list[SpinalRaptor] = []
        self.bossLevelFiveGroup: list[BossLevelFive] = []



        # self.enemies: list[Enemy] = [] # consolidate all enemies into one list
        # self.load_enemy_into_list()
        self.napalm_list: list = []
        self.total_enemies = 40
        self.prev_enemy_count: int = None

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.missed_escape_pods = []
        self.game_over: bool = False
        self.level_complete = False
        self.save_state = SaveState()


    def start(self, state) -> None:
        player_x = None
        # self.textbox.show(self.intro_dialogue)
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break
        self.starship = state.starship

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()
        # self.starship.x = player_x
        # self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list()


    def update(self, state) -> None:
        super().update(state)

        # Check if 3 or more rescue pods are destroyed
        if self.rescue_pod_destroyed >= 3:
            print("game over")
            # You might want to add additional game over logic here

        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 150
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")



        now = pygame.time.get_ticks()

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

        for enemy in self.rescuePodGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for enemy in self.spinalRaptorGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for boss in self.bossLevelFiveGroup:
            boss.draw(state.DISPLAY, self.camera)
            boss.draw_damage_flash(state.DISPLAY, self.camera)



        self.draw_ui_panel(state.DISPLAY)


        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                # Excluding rescue pods from missile targeting
                list(self.spinalRaptorGroup) +
                list(self.bossLevelFiveGroup)
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
        self.rescuePodGroup.clear()
        self.bossLevelFiveGroup.clear()
        for obj in self.tiled_map.objects:
            # ⭐ LOAD ENEMIES (existing code)
            if obj.name == "level_5_boss":
                enemy = BossLevelFive()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bossLevelFiveGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship

            if obj.name == "rescue_pod":
                enemy = RescuePod()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                enemy.target_player = self.starship
                self.rescuePodGroup.append(enemy)

                continue

            if obj.name == "spinal_raptor":
                enemy = SpinalRaptor()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.spinalRaptorGroup.append(enemy)
                enemy.camera = self.camera
                enemy.target_player = self.starship
                enemy.rescue_pod_group = self.rescuePodGroup







    def enemy_helper(self):



        # -------------------------
        # NAPALM UPDATE + DAMAGE
        # -------------------------
        for napalm in list(self.napalm_list):
            napalm.update()

            if napalm.is_active and napalm.hits(self.starship.hitbox):
                if not self.starship.invincible:
                    self.starship.shipHealth -= napalm.damage
                    self.starship.on_hit()

            if not napalm.is_active:
                self.napalm_list.remove(napalm)

        # -------------------------
        # METAL SHIELD → ENEMY BULLETS
        # -------------------------
        for metal in list(self.metal_shield_bullets):

            if not metal.is_active:
                self.metal_shield_bullets.remove(metal)
                continue

            shield_rect = pygame.Rect(
                metal.x,
                metal.y,
                metal.width,
                metal.height
            )

            for bullet in list(self.enemy_bullets):
                if bullet.collide_with_rect(shield_rect):

                    absorbed = metal.absorb_hit()

                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    if absorbed and metal in self.metal_shield_bullets:
                        self.metal_shield_bullets.remove(metal)

                    break

        # -------------------------
        # BOSS
        # -------------------------
        for boss in list(self.bossLevelFiveGroup):

            boss.update()

            if boss.enemyBullets:
                self.enemy_bullets.extend(boss.enemyBullets)
                boss.enemyBullets.clear()

            if boss.enemyHealth <= 0:
                self.bossLevelFiveGroup.remove(boss)
                print("level complete")


        # -------------------------
        # rescue pods
        # -------------------------
        for pod in list(self.rescuePodGroup):

            pod.update()

            if pod.enemyHealth <= 0:
                self.rescuePodGroup.remove(pod)

            if self.starship.hitbox.colliderect(pod.hitbox):
                # When player touches a rescue pod, set pod's health to 0
                pod.enemyHealth = 0
                pod.color = (135, 206, 235)
            else:
                pod.color = GlobalConstants.RED


        # -------------------------
        # spinal raptors
        # -------------------------
        for raptor in list(self.spinalRaptorGroup):

            raptor.update()

            if raptor.enemyHealth <= 0:
                self.spinalRaptorGroup.remove(raptor)
                continue

            # Check collision with player
            if self.starship.hitbox.colliderect(raptor.hitbox):
                # We don't want the raptor to explode when it touches the starship
                # Just change color to indicate collision
                raptor.color = (135, 206, 235)
                # print("Raptor collided with player!")
            else:
                raptor.color = GlobalConstants.RED

            # Check collision with rescue pods
            for pod in list(self.rescuePodGroup):
                if raptor.hitbox.colliderect(pod.hitbox):
                    # When spinal raptor touches a rescue pod, set pod's health to 0
                    # Only increment counter if pod was not already destroyed
                    if pod.enemyHealth > 0:
                        self.rescue_pod_destroyed += 1
                        print(f"Raptor collided with rescue pod! Total destroyed: {self.rescue_pod_destroyed}")
                    pod.enemyHealth = 0
                    pod.color = (135, 206, 235)
