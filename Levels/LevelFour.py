import pygame
import pytmx
from Constants.GlobalConstants import GlobalConstants
from Entity.Bosses.BossLevelFour import BossLevelFour
from Entity.Bosses.BossLevelOne import BossLevelOne
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
from ScreenClasses.MissionBriefingScreenLevelTwo import MissionBriefingScreenLevelTwo
from ScreenClasses.VerticalBattleScreen import VerticalBattleScreen


class LevelFour(VerticalBattleScreen):
    def __init__(self,textbox):
        super().__init__(textbox)
        # self.starship: StarShip = StarShip()

        self.level_start = True
        self.tiled_map = pytmx.load_pygame("./Levels/MapAssets/leveltmxfiles/level4.tmx")
        self.tile_size: int = self.tiled_map.tileheight
        self.map_width_tiles: int = self.tiled_map.width
        self.map_height_tiles: int = self.tiled_map.height
        self.WORLD_HEIGHT = self.map_height_tiles * self.tile_size + 400 # y position of map
        window_width, window_height = GlobalConstants.WINDOWS_SIZE
        self.camera_y = self.WORLD_HEIGHT - window_height # look at bottom of map
        self.camera.world_height = self.WORLD_HEIGHT
        self.camera.y = float(self.camera_y)
        self.map_scroll_speed_per_frame: float = .4 # move speed of camera
        # self.load_enemy_into_list()
        self.napalm_list: list = []
        self.total_enemies = 40
        self.creep_last_spawn_time = 0
        self.prev_enemy_count: int = None
        state.enemies_killed: int = 0
        self.worm_visible: bool = False

        self.level_start_time = pygame.time.get_ticks()
        self.time_limit_ms = 2 * 60 * 1000  # 2 minutes
        self.time_up = False
        self.missed_enemies = []
        self.game_over: bool = False
        self.level_complete = False
        self.worms_saved: list = []
        self.touched_worms: list[TransportWorm] = []


    def start(self, state) -> None:
        player_x = None
        player_y = None

        for obj in self.tiled_map.objects:
            if obj.name == "player":  # this string comes from Tiled
                player_x = obj.x
                player_y = obj.y
                break

        self.starship.x = player_x
        self.starship.y = player_y
        self.starship.update_hitbox()  # ⭐ REQUIRED ⭐
        self.load_enemy_into_list()

    def update(self, state) -> None:
        super().update(state)
        PADDING = 100

        if self.level_start:
            self.level_start = False
            self.starship.shipHealth = 222
            self.save_state.capture_player(self.starship, self.__class__.__name__)
            self.save_state.save_to_file("player_save.json")

        now = pygame.time.get_ticks()

        # --------------------------------
        # CAMERA SCROLL (DEFAULT = MOVE)
        # --------------------------------
        self.map_scroll_speed_per_frame = 0.4
        self.camera.scroll_speed_per_frame = 0.4

        # --------------------------------
        # CAMERA SCREEN-SPACE CHECKS
        # --------------------------------
        # USE PADDING ONLY HERE — IN SCREEN-SPACE VISIBILITY CHECKS

        player_screen_y = self.camera.world_to_screen_y(self.starship.y)
        player_screen_bottom = player_screen_y + self.starship.height

        player_visible = (
                player_screen_bottom >= + PADDING
                and player_screen_y <= self.camera.window_height + PADDING
        )

        print(
            f"[PLAYER SCREEN] y={player_screen_y:.1f} "
            f"bottom={player_screen_bottom:.1f} "
            f"visible={player_visible}"
        )

        # --------------------------------
        # TRANSPORT WORMS ONLY (SCREEN SPACE)
        # --------------------------------
        active_worms = []

        for enemy in state.enemies:
            if not isinstance(enemy, TransportWorm):
                continue

            worm_screen_y = self.camera.world_to_screen_y(enemy.y)
            worm_screen_bottom = worm_screen_y + enemy.height

            self.worm_visible = (
                    worm_screen_bottom >= + PADDING
                    and worm_screen_y <= self.camera.window_height + PADDING
            )

            print(
                f"[WORM SCREEN] id={id(enemy)} "
                f"y={worm_screen_y:.1f} "
                f"bottom={worm_screen_bottom:.1f} "
                f"visible={self.worm_visible}"
            )

            if self.worm_visible:
                active_worms.append(enemy)

        # --------------------------------
        # FREEZE ONLY IF BOTH ON SCREEN
        # --------------------------------
        if player_visible:
            for worm in active_worms:
                print(">>> PLAYER AND WORM ON SCREEN <<<")
                self.map_scroll_speed_per_frame = 0.0
                self.camera.scroll_speed_per_frame = 0.0
                break

        # --------------------------------
        # CREEP LAYER SCAN (ONLY WHEN FROZEN)
        # --------------------------------
        creep_found_on_screen = False

        if self.map_scroll_speed_per_frame == 0.0:
            try:
                creep_layer = self.tiled_map.get_layer_by_name("creep")
            except ValueError:
                creep_layer = None

            if creep_layer is not None:
                tile_w = self.tiled_map.tilewidth
                tile_h = self.tiled_map.tileheight

                screen_left = self.camera.get_world_x_left()
                screen_right = screen_left + (self.camera.window_width / self.camera.zoom)

                screen_top = self.camera.y
                screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

                start_x = int(screen_left // tile_w)
                end_x = int(screen_right // tile_w)
                start_y = int(screen_top // tile_h)
                end_y = int(screen_bottom // tile_h)

                for ty in range(start_y, end_y + 1):
                    if ty < 0 or ty >= len(creep_layer.data):
                        continue

                    for tx in range(start_x, end_x + 1):
                        if tx < 0 or tx >= len(creep_layer.data[ty]):
                            continue

                        if creep_layer.data[ty][tx] != 0:
                            creep_found_on_screen = True
                            break

                    if creep_found_on_screen:
                        break

        # --------------------------------
        # CREEP SPAWN (SLAVER)
        # --------------------------------
        if creep_found_on_screen and now - self.creep_last_spawn_time >= 5500:
            slaver = Slaver()
            slaver.x = screen_left
            slaver.y = screen_top
            slaver.width = 16
            slaver.height = 16
            slaver.camera = self.camera
            slaver.target_player = self.starship
            slaver.touched_worms = self.touched_worms
            slaver.transport_worms = active_worms  # Set the transport_worms list
            slaver.update_hitbox()

            state.enemies.append(slaver)
            self.creep_last_spawn_time = now

        # --------------------------------
        # WORM SUMMONING
        # --------------------------------
        for worm in active_worms:
            if now - worm.last_summon_time >= worm.summon_interval_ms:
                worm.summon_enemy(
                    enemy_classes=[
                        BileSpitter,
                        KamikazeDrone,
                        TriSpitter,
                        FireLauncher,
                    ],
                    enemy_groups={
                        BileSpitter: state.enemies,
                        KamikazeDrone: state.enemies,
                        TriSpitter: state.enemies,
                        FireLauncher: state.enemies,
                    },
                    spawn_y_offset=20
                )
                worm.last_summon_time = now

        # --------------------------------
        # UPDATE ENEMIES (ONCE)
        # --------------------------------
        for enemy in list(state.enemies):
            enemy.update()

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)

        # --------------------------------
        # LOSE CONDITION
        # --------------------------------
        if self.touched_worms:
            print("you lost")

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

        for enemy in state.enemies:
            enemy.draw(state.DISPLAY, self.camera)


        self.draw_ui_panel(state.DISPLAY)

        pygame.display.flip()

    def get_nearest_enemy(self, missile):
        # Get state from self
        state = getattr(self, 'state', None)

        if state is None or not state.enemies:
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

    def load_enemy_into_list(self):
        state.enemies.clear()

        for obj in self.tiled_map.objects:

            if obj.name == "level_4_boss":
                enemy = BossLevelFour()

            elif obj.name == "transport_worm":
                enemy = TransportWorm()

            elif obj.name == "kamikazi_drone":
                enemy = KamikazeDrone()

            elif obj.name == "bile_spitter":
                enemy = BileSpitter()

            elif obj.name == "blade_spinner":
                enemy = BladeSpinner()

            elif obj.name == "fire_launcher":
                enemy = FireLauncher()

            elif obj.name == "tri_spitter":
                enemy = TriSpitter()

            elif obj.name == "slaver":
                enemy = Slaver()

            else:
                continue

            enemy.x = obj.x
            enemy.y = obj.y
            enemy.width = obj.width
            enemy.height = obj.height
            enemy.update_hitbox()

            enemy.camera = self.camera
            enemy.target_player = self.starship

            state.enemies.append(enemy)
            # print(state.enemies)


    def enemy_helper(self):
        # screen bottom in WORLD coordinates
        screen_bottom = self.camera.y + (self.camera.window_height / self.camera.zoom)

        boss = "level_4_boss"

        # -------------------------
        # METAL SHIELD → ENEMY BULLETS
        # -------------------------
        for shield in list(self.player_bullets):

            if shield.weapon_name != "Metal Shield":
                continue

            if not shield.is_active:
                self.player_bullets.remove(shield)
                continue

            shield_rect = pygame.Rect(
                shield.x,
                shield.y,
                shield.width,
                shield.height
            )

            for bullet in list(self.enemy_bullets):
                if bullet.collide_with_rect(shield_rect):

                    absorbed = shield.absorb_hit()

                    if bullet in self.enemy_bullets:
                        self.enemy_bullets.remove(bullet)

                    if absorbed and shield in self.player_bullets:
                        self.player_bullets.remove(shield)

                    break

                for enemy in list(state.enemies):
                    if getattr(enemy, "enemy_name", None) != boss:
                        continue

                    # ✅ REQUIRED — DO NOT REMOVE
                    enemy.update()


            for enemy in list(state.enemies):
                if getattr(enemy, "enemy_name", None) != boss:
                    continue

                if enemy.enemyBullets:
                    self.enemy_bullets.extend(enemy.enemyBullets)
                    enemy.enemyBullets.clear()

                # -------------------------
                # BOSS DEATH
                # -------------------------
                if enemy.enemyHealth <= 0:
                    state.enemies.remove(enemy)
                    print("level complete")
        # for boss in list(self.bossLevelFourGroup):
        #
        #     boss.update()
        #
        #     if boss.enemyBullets:
        #         self.enemy_bullets.extend(boss.enemyBullets)
        #         boss.enemyBullets.clear()
        #
        #     if boss.enemyHealth <= 0:
        #         self.bossLevelFourGroup.remove(boss)
        #         print("level complete")

        for enemy in list(state.enemies):

            enemy_type = getattr(enemy, "enemy_name", None)

            # -------------------------
            # UPDATE
            # -------------------------
            enemy.update()

            if hasattr(enemy, "update_hitbox"):
                enemy.update_hitbox()

            # -------------------------
            # ENEMY BULLETS
            # -------------------------
            if hasattr(enemy, "enemyBullets") and enemy.enemyBullets:
                self.enemy_bullets.extend(enemy.enemyBullets)
                enemy.enemyBullets.clear()

            # -------------------------
            # TYPE-SPECIFIC DEBUG / LOGIC
            # -------------------------
            if enemy_type == "transport_worm":
                print(
                    "[LEVEL 4] Touched worms:",
                    [(w.enemyHealth, w.x, w.y) for w in self.touched_worms]
                )

            if enemy_type == "slaver" and enemy.enemyHealth <= 0:
                print("[LEVEL 4] Slaver removed after touching worm")

            # -------------------------
            # DEATH
            # -------------------------
            if enemy.enemyHealth <= 0:
                state.enemies.remove(enemy)
