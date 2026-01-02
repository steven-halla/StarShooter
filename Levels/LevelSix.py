import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelFive import BossLevelFive
from Entity.Bosses.BossLevelOne import BossLevelOne
from Entity.Bosses.BossLevelSix import BossLevelSix
from Entity.Enemy import Enemy
from Entity.Monsters.AcidLauncher import AcidLauncher
from Entity.Monsters.BileSpitter import BileSpitter
from Entity.Monsters.BladeSpinners import BladeSpinner
from Entity.Monsters.FireLauncher import FireLauncher
from Entity.Monsters.KamikazeDrone import KamikazeDrone
from Entity.Monsters.Ravager import Ravager
from Entity.Monsters.RescuePod import RescuePod
from Entity.Monsters.Slaver import Slaver
from Entity.Monsters.SpinalRaptor import SpinalRaptor
from Entity.Monsters.SpineLauncher import SpineLauncher
from Entity.Monsters.SporeFlower import SporeFlower
from Entity.Monsters.TriSpitter import TriSpitter
from Entity.Monsters.WaspStinger import WaspStinger
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
        self.waspStingerGroup: list[WaspStinger] = []
        self.ravagerGroup: list[Ravager] = []
        self.bileSpitterGroup: list[BileSpitter] = []
        self.acidLauncherGroup: list[AcidLauncher] = []
        self.spineLauncherGroup: list[SpineLauncher] = []
        self.bossLevelSixGroup: list[BossLevelSix] = []

        self.flame_image = pygame.image.load(
            "./Levels/MapAssets/tiles/Asset-Sheet-with-grid.png"
        ).convert_alpha()



        # self.enemies: list[Enemy] = [] # consolidate all enemies into one list
        # self.load_enemy_into_list()
        self.napalm_list: list = []
        self.wind_slicer_list: list = []
        self.total_enemies = 40
        self.prev_enemy_count: int = None

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.missed_escape_pods = []
        self.game_over: bool = False
        self.level_complete = False

        self.save_state = SaveState()






        self._hazard_active = False
        self._hazard_start_time = None
        self._fire_growth_start_time = None
        self._fire_last_growth_time = None

        self.fire_row_length = 1
        self.MAX_FIRE_ROW_LENGTH = 27

        self.fire_row_length = 0  # columns in current row
        self.fire_row_index = 0  # which row we are on (0 = bottom)
        self.MAX_FIRE_ROW_LENGTH = 27  # columns per row
        self.MAX_FIRE_ROWS = 10  # total rows

        self.fire_rows_completed = 0
        self.fire_row_length = 0

        self.MAX_FIRE_ROW_LENGTH = 27
        self.MAX_FIRE_ROWS = 20

    def is_boss_on_screen(self) -> bool:
        cam_top = self.camera.y
        cam_bottom = cam_top + GlobalConstants.GAMEPLAY_HEIGHT

        for boss in self.bossLevelFiveGroup:
            boss_top = boss.y
            boss_bottom = boss.y + boss.height

            # World-space overlap check (NO zoom math)
            if boss_bottom >= cam_top and boss_top <= cam_bottom:
                return True

        return False


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

    def draw_hazard_square(self, surface: pygame.Surface, camera) -> None:
        if not self._hazard_active:
            return

        tile_size = 32
        offset = 50
        h = surface.get_height()

        sprite_rect = pygame.Rect(65, 130, 32, 32)
        base_sprite = self.flame_image.subsurface(sprite_rect)
        sprite = pygame.transform.scale(base_sprite, (tile_size, tile_size))

        # 1️⃣ Draw ALL completed rows (never disappear)
        for row in range(self.fire_rows_completed):
            y = h - offset - (row + 1) * tile_size
            for col in range(self.MAX_FIRE_ROW_LENGTH):
                x = col * tile_size
                surface.blit(sprite, (x, y))

        # 2️⃣ Draw current growing row
        if self.fire_rows_completed < self.MAX_FIRE_ROWS:
            y = h - offset - (self.fire_rows_completed + 1) * tile_size
            for col in range(self.fire_row_length):
                x = col * tile_size
                surface.blit(sprite, (x, y))

    # def draw_hazard_square(self, display) -> None:
    #     if not getattr(self, "_hazard_active", False):
    #         return
    #
    #     size = 16
    #     offset = 50
    #     h = display.get_height()
    #     color = (255, 0, 0)
    #
    #     left_x = 0
    #     right_x = size
    #
    #     # bottom row
    #     pygame.draw.rect(display, color, (left_x, h - size - offset, size, size))
    #     pygame.draw.rect(display, color, (right_x, h - size - offset, size, size))
    #
    #     # top row (touching bottom row)
    #     pygame.draw.rect(display, color, (left_x, h - (2 * size) - offset, size, size))
    #     pygame.draw.rect(display, color, (right_x, h - (2 * size) - offset, size, size))

    def update_hazard_square(self, current_time_ms: int) -> None:
        # Fire only exists when boss is visible
        if not self.is_boss_on_screen():
            return

        # Activate fire ONCE when boss appears
        if not self._hazard_active:
            self._hazard_active = True
            self._hazard_start_time = current_time_ms
            self._fire_last_growth_time = current_time_ms
            self.fire_rows_completed = 0
            self.fire_row_length = 0
            return

        # Stop growing after max rows
        if self.fire_rows_completed >= self.MAX_FIRE_ROWS:
            return

        # Grow every 500ms
        if current_time_ms - self._fire_last_growth_time >= 500:
            self._fire_last_growth_time = current_time_ms

            # Grow current row
            self.fire_row_length += 1

            # Move to next row when full
            if self.fire_row_length >= self.MAX_FIRE_ROW_LENGTH:
                self.fire_row_length = 0
                self.fire_rows_completed += 1
    def update(self, state) -> None:
        super().update(state)
        for ravager in list(self.ravagerGroup):
            ravager.update()

            for blade in list(self.wind_slicer_list):
                if blade.hitbox.colliderect(ravager.hitbox):
                    ravager.enemyHealth -= blade.damage
                    blade.on_hit()  # or destroy if single-use

        # Check if 3 or more rescue pods are destroyed
        if self.rescue_pod_destroyed >= 3:
            print("game over")
            # You might want to add additional game over logic here

        if self.level_start == True:
            self.level_start = False
            self.starship.shipHealth = 450
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

        now = pygame.time.get_ticks()
        self.update_hazard_square(now)
        self.update_hazard_damage(state.DISPLAY.get_height())
        self.extract_object_names()
        print(self.starship.shipHealth)

    def update_hazard_damage(self, surface_height: int) -> None:
        if not self._hazard_active:
            return

        tile_size = 32
        offset = 50
        damage = 5
        h = surface_height

        player_screen_rect = pygame.Rect(
            self.camera.world_to_screen_x(self.starship.hitbox.x),
            self.camera.world_to_screen_y(self.starship.hitbox.y),
            self.starship.hitbox.width,
            self.starship.hitbox.height
        )

        # 1️⃣ Damage completed rows
        for row in range(self.fire_rows_completed):
            y = h - offset - (row + 1) * tile_size
            for col in range(self.MAX_FIRE_ROW_LENGTH):
                x = col * tile_size
                rect = pygame.Rect(x, y, tile_size, tile_size)

                if rect.colliderect(player_screen_rect):
                    if not self.starship.invincible:
                        self.starship.shipHealth -= damage
                        self.starship.on_hit()
                    return

        # 2️⃣ Damage current growing row
        if self.fire_rows_completed < self.MAX_FIRE_ROWS:
            y = h - offset - (self.fire_rows_completed + 1) * tile_size
            for col in range(self.fire_row_length):
                x = col * tile_size
                rect = pygame.Rect(x, y, tile_size, tile_size)

                if rect.colliderect(player_screen_rect):
                    if not self.starship.invincible:
                        self.starship.shipHealth -= damage
                        self.starship.on_hit()
                    return
    def draw(self, state):
        # 1️⃣ Let BattleScreen draw map, bullets, UI, etc.
        super().draw(state)

        # 2️⃣ Draw TILE OBJECTS (pipes, decorations, etc.)
        for obj in self.tiled_map.objects:
            if hasattr(obj, "image") and obj.image is not None:
                screen_x = self.camera.world_to_screen_x(obj.x)
                screen_y = self.camera.world_to_screen_y(obj.y)
                state.DISPLAY.blit(obj.image, (screen_x, screen_y))

        # 3️⃣ Draw PLAYER
        if not self.playerDead:
            self.starship.draw(state.DISPLAY, self.camera)

        # 4️⃣ DRAW ALL ENEMIES — EXPLICIT AND ORDERED

        for enemy in self.rescuePodGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for enemy in self.spinalRaptorGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for enemy in self.waspStingerGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for enemy in self.ravagerGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for enemy in self.bileSpitterGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for enemy in self.acidLauncherGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for enemy in self.spineLauncherGroup:
            enemy.draw(state.DISPLAY, self.camera)
            enemy.draw_damage_flash(state.DISPLAY, self.camera)

        for boss in self.bossLevelFiveGroup:
            boss.draw(state.DISPLAY, self.camera)
            boss.draw_damage_flash(state.DISPLAY, self.camera)

        # 5️⃣ Flip ONCE, LAST
        self.draw_hazard_square(state.DISPLAY, self.camera)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        enemies = (
                # Excluding rescue pods from missile targeting
                list(self.spinalRaptorGroup) +
                list(self.waspStingerGroup) +
                list(self.ravagerGroup) +
                list(self.bileSpitterGroup) +
                list(self.acidLauncherGroup) +
                list(self.spineLauncherGroup) +
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
        self.waspStingerGroup.clear()
        self.ravagerGroup.clear()
        self.bileSpitterGroup.clear()
        self.acidLauncherGroup.clear()
        self.spineLauncherGroup.clear()
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

            if obj.name == "bile_spitter":
                enemy = BileSpitter()
                enemy.x = obj.x
                enemy.y = obj.y
                enemy.width = obj.width
                enemy.height = obj.height
                enemy.update_hitbox()
                enemy.camera = self.camera
                self.bileSpitterGroup.append(enemy)
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
        for boss in list(self.bossLevelSixGroup):

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

        # -------------------------
        # wasp stingers
        # -------------------------
        for wasp in list(self.waspStingerGroup):

            wasp.update()

            if wasp.enemyHealth <= 0:
                self.waspStingerGroup.remove(wasp)
                continue

            # Check collision with player
            if self.starship.hitbox.colliderect(wasp.hitbox):
                # Change color to indicate collision
                wasp.color = (135, 206, 235)
                # Apply damage to player if not invincible
                if not self.starship.invincible:
                    self.starship.shipHealth -= 5  # Damage amount
                    self.starship.on_hit()
            else:
                wasp.color = GlobalConstants.RED

        # -------------------------
        # ravagers
        # -------------------------
        for ravager in list(self.ravagerGroup):

            napalm = ravager.update()

            # Handle bullets from ravager
            if ravager.enemyBullets:
                self.enemy_bullets.extend(ravager.enemyBullets)
                ravager.enemyBullets.clear()

            # Handle napalm from ravager
            if napalm is not None:
                self.napalm_list.append(napalm)

            if ravager.enemyHealth <= 0:
                self.ravagerGroup.remove(ravager)
                continue

            # Check collision with player
            if self.starship.hitbox.colliderect(ravager.hitbox):
                # Change color to indicate collision
                ravager.color = (135, 206, 235)
                # Apply damage to player if not invincible
                if not self.starship.invincible:
                    self.starship.shipHealth -= 10  # Damage amount
                    self.starship.on_hit()
            else:
                ravager.color = GlobalConstants.RED

        # -------------------------
        # bile spitters
        # -------------------------
        for spitter in list(self.bileSpitterGroup):

            spitter.update()

            # Handle bullets from bile spitter
            if spitter.enemyBullets:
                self.enemy_bullets.extend(spitter.enemyBullets)
                spitter.enemyBullets.clear()

            if spitter.enemyHealth <= 0:
                self.bileSpitterGroup.remove(spitter)
                continue

            # Check collision with player
            if self.starship.hitbox.colliderect(spitter.hitbox):
                # Change color to indicate collision
                spitter.color = (135, 206, 235)
                # Apply damage to player if not invincible
                if not self.starship.invincible:
                    self.starship.shipHealth -= 10  # Damage amount
                    self.starship.on_hit()
            else:
                spitter.color = GlobalConstants.RED

        # -------------------------
        # spine launchers
        # -------------------------
        for launcher in list(self.spineLauncherGroup):

            launcher.update()

            # Handle bullets from acid launcher
            if launcher.enemyBullets:
                self.enemy_bullets.extend(launcher.enemyBullets)
                launcher.enemyBullets.clear()

            if launcher.enemyHealth <= 0:
                self.spineLauncherGroup.remove(launcher)
                continue

            # Check collision with player
            if self.starship.hitbox.colliderect(launcher.hitbox):
                # Change color to indicate collision
                launcher.color = (135, 206, 235)
                # Apply damage to player if not invincible
                if not self.starship.invincible:
                    self.starship.shipHealth -= 10  # Damage amount
                    self.starship.on_hit()
            else:
                launcher.color = GlobalConstants.RED

                # -------------------------
                # acid launchers
                # -------------------------
            for launcher in list(self.spineLauncherGroup):

                launcher.update()

                # Handle bullets from acid launcher
                if launcher.enemyBullets:
                    self.enemy_bullets.extend(launcher.enemyBullets)
                    launcher.enemyBullets.clear()

                if launcher.enemyHealth <= 0:
                    self.spineLauncherGroup.remove(launcher)
                    continue

                # Check collision with player
                if self.starship.hitbox.colliderect(launcher.hitbox):
                    # Change color to indicate collision
                    launcher.color = (135, 206, 235)
                    # Apply damage to player if not invincible
                    if not self.starship.invincible:
                        self.starship.shipHealth -= 10  # Damage amount
                        self.starship.on_hit()
                else:
                    launcher.color = GlobalConstants.RED

